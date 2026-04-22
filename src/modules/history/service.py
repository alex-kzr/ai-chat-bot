from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

from src.config import Settings
from src.contracts import ChatMessage
from src.events import ChatReplyProduced, MessageReceived, ResponseGenerated, UserTextReceived
from src.prompts import SUMMARIZATION_PROMPT

logger = logging.getLogger(__name__)


class _OllamaChatLike(Protocol):
    async def chat_once(self, messages: list[ChatMessage], *, model: str) -> str: ...


@dataclass(slots=True)
class ConversationService:
    settings: Settings
    ollama: _OllamaChatLike
    _store: dict[int, list[ChatMessage]] = field(default_factory=dict)
    _pending_summary: dict[int, list[ChatMessage]] = field(default_factory=dict)

    def get_history(self, user_id: int) -> list[ChatMessage]:
        return list(self._store.get(user_id, []))

    def get_last_messages(self, user_id: int, limit: int) -> list[ChatMessage]:
        if limit <= 0:
            return []
        history = self._store.get(user_id, [])
        return list(history[-limit:])

    def append_message(self, user_id: int, role: str, content: str) -> None:
        history = self._store.setdefault(user_id, [])
        history.append({"role": role, "content": content})
        self._trim(user_id)

    def replace_history(self, user_id: int, messages: list[ChatMessage]) -> None:
        self._store[user_id] = list(messages)

    def clear_history(self, user_id: int) -> None:
        self._store.pop(user_id, None)

    def needs_summarization(self, user_id: int) -> bool:
        return len(self._store.get(user_id, [])) > self.settings.summarization.threshold

    async def maybe_compress_history(self, user_id: int) -> None:
        history = self._store.get(user_id, [])
        pending = self._pending_summary.get(user_id, [])
        full_history = [*pending, *history]
        keep_recent = self.settings.summarization.keep_recent
        if len(full_history) <= keep_recent:
            return
        if len(full_history) <= self.settings.summarization.threshold:
            return

        messages_to_summarize = full_history[: len(full_history) - keep_recent]
        summary_prompt: list[ChatMessage] = [{"role": "system", "content": SUMMARIZATION_PROMPT}] + messages_to_summarize
        summary = await self.ollama.chat_once(summary_prompt, model=self.settings.chat_model)
        if not summary:
            logger.warning("Summarization for user %s returned empty summary", user_id)
            return

        recent = full_history[-keep_recent:]
        summary_entry = self.build_summary_entry(summary)
        self._store[user_id] = [summary_entry] + recent
        self._pending_summary.pop(user_id, None)
        logger.info(
            "Compressed history for user %s: replaced %s messages with summary",
            user_id,
            len(messages_to_summarize),
        )

    def build_summary_entry(self, summary: str) -> ChatMessage:
        return {"role": "system", "content": f"[Conversation summary]\n{summary.strip()}"}

    def on_user_text_received(self, event: UserTextReceived) -> None:
        self.append_message(event.user_id, "user", event.text)

    def on_chat_reply_produced(self, event: ChatReplyProduced) -> None:
        self.append_message(event.user_id, "assistant", event.reply)

    def on_message_received(self, event: MessageReceived) -> None:
        self.append_message(event.user_id, "user", event.text)

    def on_response_generated(self, event: ResponseGenerated) -> None:
        self.append_message(event.user_id, "assistant", event.reply)

    def _trim(self, user_id: int) -> None:
        history = self._store.get(user_id)
        if history is None:
            return
        while len(history) > self.settings.history.max_messages:
            dropped = history.pop(0)
            pending = self._pending_summary.setdefault(user_id, [])
            pending.append(dropped)
