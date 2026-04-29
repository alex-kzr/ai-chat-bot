"""
Compatibility wrappers over ConversationService summarization behavior.
"""

from __future__ import annotations

from collections.abc import Sequence

from .contracts import ChatMessage
from .runtime import get_runtime


def needs_summarization(user_id: int) -> bool:
    return get_runtime().conversation.needs_summarization(user_id)


def get_messages_to_summarize(user_id: int) -> list[ChatMessage]:
    history = get_runtime().conversation.get_history(user_id)
    keep_recent = get_runtime().settings.summarization.keep_recent
    if len(history) <= keep_recent:
        return []
    return history[: len(history) - keep_recent]


async def call_llm_for_summary(messages: Sequence[ChatMessage]) -> str:
    runtime = get_runtime()
    return await runtime.ollama.chat_once(messages, model=runtime.settings.chat_model)


async def compress_history(user_id: int) -> None:
    await get_runtime().conversation.maybe_compress_history(user_id)
