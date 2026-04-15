"""
Conversation history summarization module.

Provides functions to compress conversation history by summarizing older messages
and keeping recent messages intact. Triggers when history exceeds SUMMARY_THRESHOLD.
"""

import logging
import httpx

from . import config
from .history import get_history, replace_history
from .prompts import SUMMARIZATION_PROMPT


logger = logging.getLogger(__name__)


def needs_summarization(user_id: int) -> bool:
    """
    Check if a user's conversation history exceeds the summarization threshold.

    Args:
        user_id: Telegram user ID

    Returns:
        True if len(history) > SUMMARY_THRESHOLD, False otherwise
    """
    history = get_history(user_id)
    return len(history) > config.SUMMARY_THRESHOLD


def get_messages_to_summarize(user_id: int) -> list[dict]:
    """
    Get the slice of history that will be replaced by summarization.

    Returns all messages except the last SUMMARY_KEEP_RECENT.
    Returns empty list if history is not long enough to summarize.

    Args:
        user_id: Telegram user ID

    Returns:
        List of messages to summarize. Empty list if nothing to summarize.
    """
    history = get_history(user_id)
    if len(history) <= config.SUMMARY_KEEP_RECENT:
        return []
    return history[: len(history) - config.SUMMARY_KEEP_RECENT]


async def call_llm_for_summary(messages: list[dict]) -> str:
    """
    Call the LLM to summarize a list of messages.

    Args:
        messages: List of message dictionaries to summarize

    Returns:
        Summary string, or empty string if LLM call fails
    """
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SUMMARIZATION_PROMPT},
        ] + messages,
        "stream": False,
    }

    logging.info(">>> Summarization LLM request with %d messages", len(messages))

    try:
        async with httpx.AsyncClient(timeout=config.OLLAMA_TIMEOUT) as client:
            response = await client.post(f"{config.OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            summary = data["message"]["content"].strip()
            return summary
    except Exception as e:
        logging.error("Summarization LLM error: %s", e)
        return ""


async def compress_history(user_id: int) -> None:
    """
    Compress a user's conversation history by summarizing older messages.

    Orchestrates the full summarization workflow:
    1. Get messages to summarize (all except last SUMMARY_KEEP_RECENT)
    2. If empty, return early
    3. Call LLM to produce summary
    4. If summary is empty (LLM error), return early
    5. Replace history with [summary_entry] + recent_messages

    Args:
        user_id: Telegram user ID
    """
    messages_to_summarize = get_messages_to_summarize(user_id)
    if not messages_to_summarize:
        return

    summary = await call_llm_for_summary(messages_to_summarize)
    if not summary:
        logging.warning("Summarization for user %d failed; skipping compression", user_id)
        return

    # Get recent messages to keep
    history = get_history(user_id)
    recent_messages = history[-config.SUMMARY_KEEP_RECENT:]

    # Create summary entry and new history
    summary_entry = {"role": "system", "content": f"[Conversation summary]\n{summary}"}
    new_history = [summary_entry] + recent_messages

    # Replace history in store
    replace_history(user_id, new_history)

    replaced_count = len(messages_to_summarize)
    logger.info(
        "Compressed history for user %d: replaced %d messages with summary",
        user_id,
        replaced_count,
    )
