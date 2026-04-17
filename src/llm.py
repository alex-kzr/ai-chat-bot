from __future__ import annotations

import logging
import random

from .context_logging import extract_context, count_context_tokens, log_context
from .contracts import ChatMessage, LLMReply
from .errors import OllamaProtocolError, OllamaTransportError
from .prompts import ERROR_PHRASES

logger = logging.getLogger(__name__)


class _ContentStreamDebugLogger:
    def __init__(self, target_logger: logging.Logger) -> None:
        self._logger = target_logger
        self._buffer = ""

    def push(self, chunk: str) -> None:
        if not chunk:
            return
        self._buffer += chunk
        self._flush_complete_lines()

    def finalize(self) -> None:
        if self._buffer:
            self._logger.debug("<<< LLM: %s", self._buffer)
        self._buffer = ""

    def _flush_complete_lines(self) -> None:
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._logger.debug("<<< LLM: %s", line)


class _ThinkingStreamDebugLogger:
    def __init__(self, target_logger: logging.Logger) -> None:
        self._logger = target_logger
        self._buffer = ""

    def push(self, chunk: str) -> None:
        if not chunk:
            return
        self._buffer += chunk
        self._flush_complete_lines()

    def finalize(self) -> None:
        tail = self._buffer.strip()
        if tail:
            self._logger.debug("<<< THINK: %s", tail)
        self._buffer = ""

    def _flush_complete_lines(self) -> None:
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            clean_line = line.strip()
            if clean_line:
                self._logger.debug("<<< THINK: %s", clean_line)


def _messages_to_prompt(messages: list[ChatMessage]) -> str:
    prompt_parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(content)
        elif role == "user":
            prompt_parts.append(f"User: {content}")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}")
    return "\n\n".join(prompt_parts) + "\n\nAssistant:"


async def ask_llm(user_text: str, history: list[ChatMessage] | None = None, user_id: str | int | None = None) -> LLMReply:
    from .runtime import get_runtime

    runtime = get_runtime()
    settings = runtime.settings
    history = history or []

    messages: list[ChatMessage] = []
    if settings.system_prompt.enabled:
        messages.append({"role": "system", "content": settings.system_prompt.prompt})
    messages.extend(history)

    if settings.logging.context_enabled:
        try:
            context_data = extract_context(
                messages=messages,
                model_name=settings.chat_model,
                user_id=str(user_id) if user_id is not None else None,
            )
            context_data["statistics"]["token_count"] = count_context_tokens(messages)
            log_context(context_data, level="debug")
        except Exception as exc:
            logger.warning("Failed to log context: %s", exc)

    prompt = _messages_to_prompt(messages)
    debug_enabled = logger.isEnabledFor(logging.DEBUG)
    thinking_debug_logger = _ThinkingStreamDebugLogger(logger) if debug_enabled else None
    content_debug_logger = _ContentStreamDebugLogger(logger) if debug_enabled else None
    try:
        content, thinking = await runtime.ollama.generate_streamed_text(
            prompt,
            model=settings.chat_model,
            on_thinking_chunk=thinking_debug_logger.push if thinking_debug_logger is not None else None,
            on_content_chunk=content_debug_logger.push if content_debug_logger is not None else None,
            on_stream_done=content_debug_logger.finalize if content_debug_logger is not None else None,
        )
    except (OllamaTransportError, OllamaProtocolError) as exc:
        if content_debug_logger is not None:
            content_debug_logger.finalize()
        logger.error("LLM error: %s", exc)
        return LLMReply(llm_raw="[error]", bot_reply=random.choice(ERROR_PHRASES), thinking="")
    finally:
        if thinking_debug_logger is not None:
            thinking_debug_logger.finalize()

    content = content.strip()
    thinking = thinking.strip()
    if not content:
        if thinking:
            logger.warning("LLM returned thinking-only stream without final answer text")
            try:
                fallback_content = (
                    await runtime.ollama.generate_once(
                        prompt,
                        model=settings.chat_model,
                    )
                ).strip()
            except (OllamaTransportError, OllamaProtocolError) as exc:
                logger.error("LLM fallback error after thinking-only stream: %s", exc)
                fallback_content = ""
            if fallback_content:
                llm_raw = fallback_content + ("\n\n" + thinking if thinking else "")
                return LLMReply(llm_raw=llm_raw, bot_reply=fallback_content, thinking=thinking)
        else:
            logger.warning("LLM returned empty response")
        return LLMReply(llm_raw="[error]", bot_reply=random.choice(ERROR_PHRASES), thinking="")
    llm_raw = content + ("\n\n" + thinking if thinking else "")
    return LLMReply(llm_raw=llm_raw, bot_reply=content, thinking=thinking)
