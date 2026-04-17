"""
Compatibility wrappers over the conversation state service.
"""

from __future__ import annotations

from .runtime import get_runtime


def get_history(user_id: int) -> list[dict]:
    return list(get_runtime().conversation.get_history(user_id))


def append_message(user_id: int, role: str, content: str) -> None:
    get_runtime().conversation.append_message(user_id, role, content)


def clear_history(user_id: int) -> None:
    get_runtime().conversation.clear_history(user_id)


def replace_history(user_id: int, messages: list[dict]) -> None:
    get_runtime().conversation.replace_history(user_id, list(messages))


def trim_history(user_id: int) -> None:
    # Trimming is handled inside append_message in ConversationService.
    _ = user_id
