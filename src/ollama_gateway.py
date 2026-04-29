from __future__ import annotations

import json
import asyncio
from collections.abc import Callable, Sequence
from dataclasses import dataclass

import httpx

from .config import Settings
from .contracts import ChatMessage
from .context_logging import log_agent_event, summarize_text
from .errors import OllamaProtocolError, OllamaTransportError
from .prompts import AGENT_STOP_SEQUENCES


@dataclass(slots=True)
class OllamaGateway:
    settings: Settings

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.settings.ollama.url}/api/tags")
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaTransportError(f"Failed to list models: {exc}") from exc

        try:
            payload = response.json()
            models = [str(item["name"]) for item in payload.get("models", []) if "name" in item]
        except Exception as exc:
            raise OllamaProtocolError("Invalid /api/tags response payload") from exc
        return models

    async def generate_once(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float | None = None,
        timeout: float | None = None,
        run_id: str | None = None,
        step_index: int | None = None,
        request_kind: str | None = None,
        retry_index: int | None = None,
    ) -> str:
        payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": self.settings.ollama.think,
            "stop": list(AGENT_STOP_SEQUENCES),
        }
        if temperature is not None:
            payload["temperature"] = temperature
        client_timeout = self.settings.ollama.timeout if timeout is None else timeout
        started_at = asyncio.get_running_loop().time()
        if run_id is not None and step_index is not None:
            log_agent_event(
                run_id,
                "ollama_generate_started",
                step_index=step_index,
                kind=request_kind or "unknown",
                retry_index=retry_index,
                model=model,
                timeout_s=float(client_timeout) if client_timeout is not None else None,
                prompt=summarize_text(prompt, max_chars=300),
            )
        try:
            async with httpx.AsyncClient(timeout=client_timeout) as client:
                response = await client.post(f"{self.settings.ollama.url}/api/generate", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            if run_id is not None and step_index is not None:
                log_agent_event(
                    run_id,
                    "ollama_generate_failed",
                    level="error",
                    step_index=step_index,
                    kind=request_kind or "unknown",
                    retry_index=retry_index,
                    error=str(exc),
                )
            raise OllamaTransportError(f"Generate request failed: {exc}") from exc

        content = self._collect_generate_text(response.text)
        if run_id is not None and step_index is not None:
            duration_ms = int((asyncio.get_running_loop().time() - started_at) * 1000)
            log_agent_event(
                run_id,
                "ollama_generate_completed",
                step_index=step_index,
                kind=request_kind or "unknown",
                retry_index=retry_index,
                duration_ms=duration_ms,
                response=summarize_text(content, max_chars=300),
            )
        return content

    async def generate_streamed_text(
        self,
        prompt: str,
        *,
        model: str,
        timeout: float | None = None,
        on_thinking_chunk: Callable[[str], None] | None = None,
        on_content_chunk: Callable[[str], None] | None = None,
        on_stream_done: Callable[[], None] | None = None,
        run_id: str | None = None,
        step_index: int | None = None,
    ) -> tuple[str, str]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "think": self.settings.ollama.think,
            "stop": list(AGENT_STOP_SEQUENCES),
        }
        content = ""
        thinking = ""
        client_timeout = self.settings.agent.safety.llm_request_timeout if timeout is None else timeout
        stream_stall_timeout = float(self.settings.agent.safety.llm_stream_timeout)
        max_repeat_chunks = int(self.settings.agent.safety.max_repeat_stream_chunks)
        started_at = asyncio.get_running_loop().time()
        if run_id is not None and step_index is not None:
            log_agent_event(
                run_id,
                "ollama_stream_started",
                step_index=step_index,
                model=model,
                timeout_s=float(client_timeout) if client_timeout is not None else None,
                stall_timeout_s=stream_stall_timeout,
                max_repeat_chunks=max_repeat_chunks,
                prompt=summarize_text(prompt, max_chars=300),
            )
        try:
            async with httpx.AsyncClient(timeout=client_timeout) as client:
                async with client.stream("POST", f"{self.settings.ollama.url}/api/generate", json=payload) as response:
                    response.raise_for_status()
                    last_line = ""
                    repeated_lines = 0
                    line_count = 0
                    aiter = response.aiter_lines().__aiter__()
                    while True:
                        try:
                            line = await asyncio.wait_for(aiter.__anext__(), timeout=stream_stall_timeout)
                        except StopAsyncIteration:
                            break
                        except TimeoutError as exc:
                            if run_id is not None and step_index is not None:
                                log_agent_event(
                                    run_id,
                                    "ollama_stream_stalled",
                                    level="error",
                                    step_index=step_index,
                                    stall_timeout_s=stream_stall_timeout,
                                )
                            raise OllamaTransportError(
                                f"Stream stalled (no new chunks) for {stream_stall_timeout:.1f}s"
                            ) from exc

                        if not line:
                            continue
                        line_count += 1

                        if line == last_line:
                            repeated_lines += 1
                        else:
                            last_line = line
                            repeated_lines = 1

                        if repeated_lines >= max_repeat_chunks:
                            if run_id is not None and step_index is not None:
                                log_agent_event(
                                    run_id,
                                    "ollama_stream_repeated_chunks",
                                    level="error",
                                    step_index=step_index,
                                    repeated_lines=repeated_lines,
                                    max_repeat_chunks=max_repeat_chunks,
                                    last_line=summarize_text(last_line, max_chars=200),
                                )
                            raise OllamaProtocolError(
                                f"Stream repeated identical chunks (limit={max_repeat_chunks})"
                            )

                        chunk = json.loads(line)
                        content_delta = str(chunk.get("response", ""))
                        content += content_delta
                        thinking_delta = str(chunk.get("thinking", ""))
                        thinking += thinking_delta
                        if on_thinking_chunk is not None and thinking_delta:
                            on_thinking_chunk(thinking_delta)
                        if on_content_chunk is not None and content_delta:
                            on_content_chunk(content_delta)
                        if chunk.get("done"):
                            break
        except httpx.HTTPError as exc:
            if run_id is not None and step_index is not None:
                log_agent_event(
                    run_id,
                    "ollama_stream_failed",
                    level="error",
                    step_index=step_index,
                    error=str(exc),
                )
            raise OllamaTransportError(f"Streamed generate request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            if run_id is not None and step_index is not None:
                log_agent_event(
                    run_id,
                    "ollama_stream_bad_json",
                    level="error",
                    step_index=step_index,
                    error=str(exc),
                )
            raise OllamaProtocolError("Invalid JSON line in streamed Ollama response") from exc
        finally:
            if on_stream_done is not None:
                on_stream_done()

        if run_id is not None and step_index is not None:
            duration_ms = int((asyncio.get_running_loop().time() - started_at) * 1000)
            log_agent_event(
                run_id,
                "ollama_stream_completed",
                step_index=step_index,
                duration_ms=duration_ms,
                line_count=line_count,
                content=summarize_text(content, max_chars=300),
                thinking=summarize_text(thinking, max_chars=300),
            )

        return content.strip(), thinking.strip()

    async def chat_once(self, messages: Sequence[ChatMessage], *, model: str) -> str:
        payload = {"model": model, "messages": list(messages), "stream": False}
        try:
            async with httpx.AsyncClient(timeout=self.settings.ollama.timeout) as client:
                response = await client.post(f"{self.settings.ollama.url}/api/chat", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaTransportError(f"Chat request failed: {exc}") from exc

        try:
            data = response.json()
            content = str(data["message"]["content"]).strip()
        except Exception as exc:
            raise OllamaProtocolError("Invalid /api/chat response payload") from exc
        return content

    @staticmethod
    def _collect_generate_text(raw: str) -> str:
        content = ""
        for line in raw.strip().splitlines():
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError as exc:
                raise OllamaProtocolError("Invalid JSON line in /api/generate response") from exc
            content += str(chunk.get("response", ""))
            if chunk.get("done"):
                break
        return content.strip()
