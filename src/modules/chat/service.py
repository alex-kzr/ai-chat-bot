from __future__ import annotations

import logging
import random
from collections.abc import Callable
from typing import Protocol

from src.config import Settings
from src.context_logging import count_context_tokens, extract_context, log_context
from src.contracts import ChatMessage, LLMReply
from src.errors import OllamaProtocolError, OllamaTransportError
from src.prompts import ERROR_PHRASES, build_delimited_prompt

logger = logging.getLogger("src.llm")


class _OllamaLike(Protocol):
    async def generate_streamed_text(
        self,
        prompt: str,
        *,
        model: str,
        on_thinking_chunk: Callable[[str], None] | None = None,
        on_content_chunk: Callable[[str], None] | None = None,
        on_stream_done: Callable[[], None] | None = None,
    ) -> tuple[str, str]: ...

    async def generate_once(self, prompt: str, *, model: str) -> str: ...


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
    return build_delimited_prompt(messages)


class ChatService:
    def __init__(
        self,
        *,
        settings: Settings,
        ollama: _OllamaLike,
    ) -> None:
        self._settings = settings
        self._ollama = ollama

    async def generate_response(
        self,
        user_text: str,
        *,
        history: list[ChatMessage] | None = None,
        user_id: str | int | None = None,
    ) -> LLMReply:
        history = history or []
        settings = self._settings

        messages: list[ChatMessage] = []
        if settings.system_prompt.enabled:
            system_message: ChatMessage = {"role": "system", "content": settings.system_prompt.prompt}
            messages.append(system_message)
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
            content, thinking = await self._ollama.generate_streamed_text(
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
                    fallback_content = (await self._ollama.generate_once(prompt, model=settings.chat_model)).strip()
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

    @staticmethod
    def format_for_user(reply: LLMReply, *, show_thinking: bool) -> str:
        if show_thinking and reply.thinking:
            return f"💭 <thinking>\n{reply.thinking}\n</thinking>\n\n{reply.bot_reply}"
        return reply.bot_reply
