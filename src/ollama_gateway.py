from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Sequence

import httpx

from .config import Settings
from .contracts import ChatMessage
from .errors import OllamaProtocolError, OllamaTransportError


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

    async def generate_once(self, prompt: str, *, model: str, temperature: float | None = None) -> str:
        payload: dict[str, object] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "think": self.settings.ollama.think,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        try:
            async with httpx.AsyncClient(timeout=self.settings.ollama.timeout) as client:
                response = await client.post(f"{self.settings.ollama.url}/api/generate", json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise OllamaTransportError(f"Generate request failed: {exc}") from exc

        return self._collect_generate_text(response.text)

    async def generate_streamed_text(
        self,
        prompt: str,
        *,
        model: str,
        on_thinking_chunk: Callable[[str], None] | None = None,
        on_content_chunk: Callable[[str], None] | None = None,
        on_stream_done: Callable[[], None] | None = None,
    ) -> tuple[str, str]:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "think": self.settings.ollama.think,
        }
        content = ""
        thinking = ""
        try:
            async with httpx.AsyncClient(timeout=self.settings.ollama.timeout) as client:
                async with client.stream("POST", f"{self.settings.ollama.url}/api/generate", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
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
                    if on_stream_done is not None:
                        on_stream_done()
        except httpx.HTTPError as exc:
            raise OllamaTransportError(f"Streamed generate request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise OllamaProtocolError("Invalid JSON line in streamed Ollama response") from exc

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
