"""
Per-user conversation history storage module.

Provides functions to store and retrieve conversation history indexed by Telegram user ID.
"""

import logging
from src.config import MAX_HISTORY_MESSAGES

logger = logging.getLogger(__name__)

_store: dict[int, list[dict]] = {}


def get_history(user_id: int) -> list[dict]:
    """
    Get a copy of the conversation history for a user.

    Args:
        user_id: Telegram user ID

    Returns:
        A copy of the user's message history. Empty list if user has no history.
    """
    if user_id not in _store:
        return []
    return list(_store[user_id])


def trim_history(user_id: int) -> None:
    """
    Enforce message-count limit by removing oldest messages via FIFO.

    Args:
        user_id: Telegram user ID
    """
    if user_id not in _store:
        return

    while len(_store[user_id]) > MAX_HISTORY_MESSAGES:
        _store[user_id].pop(0)
        remaining = len(_store[user_id])
        logger.debug(f"Trimmed message for user {user_id}; remaining: {remaining}")


def append_message(user_id: int, role: str, content: str) -> None:
    """
    Add a message to a user's conversation history.

    Args:
        user_id: Telegram user ID
        role: Message role ("user" or "assistant")
        content: Message content
    """
    if user_id not in _store:
        _store[user_id] = []
    _store[user_id].append({"role": role, "content": content})
    trim_history(user_id)


def clear_history(user_id: int) -> None:
    """
    Remove all history for a user.

    Args:
        user_id: Telegram user ID
    """
    if user_id in _store:
        del _store[user_id]


def replace_history(user_id: int, messages: list[dict]) -> None:
    """
    Replace the entire conversation history for a user.

    Args:
        user_id: Telegram user ID
        messages: New list of message dictionaries
    """
    _store[user_id] = list(messages)
