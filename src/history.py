"""
Per-user conversation history storage module.

Provides functions to store and retrieve conversation history indexed by Telegram user ID.
"""

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


def clear_history(user_id: int) -> None:
    """
    Remove all history for a user.

    Args:
        user_id: Telegram user ID
    """
    if user_id in _store:
        del _store[user_id]
