"""BLC-02 — ConversationService trim and summarization tests."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from src.config import load_settings
from src.modules.history.service import ConversationService


def _make_service(
    *,
    max_messages: int = 4,
    threshold: int = 999,
    keep_recent: int = 2,
) -> tuple[ConversationService, AsyncMock]:
    settings = load_settings(
        env={
            "BOT_TOKEN": "test-token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "test-model",
            "MAX_HISTORY_MESSAGES": str(max_messages),
            "SUMMARY_THRESHOLD": str(threshold),
            "SUMMARY_KEEP_RECENT": str(keep_recent),
            "CONTEXT_LOGGING_ENABLED": "false",
        },
        load_dotenv_file=False,
    )
    ollama = AsyncMock()
    ollama.chat_once = AsyncMock(return_value="SUMMARY")
    return ConversationService(settings=settings, ollama=ollama), ollama


@pytest.mark.unit
def test_append_below_limit_preserves_all_messages_in_order() -> None:
    service, _ = _make_service(max_messages=4)

    service.append_message(1, "user", "first")
    service.append_message(1, "assistant", "second")
    service.append_message(1, "user", "third")

    history = service.get_history(1)
    assert len(history) == 3
    assert history[0]["content"] == "first"
    assert history[1]["content"] == "second"
    assert history[2]["content"] == "third"


@pytest.mark.unit
@pytest.mark.parametrize("limit", [2, 4, 10], ids=["limit-2", "limit-4", "limit-10"])
def test_append_past_limit_drops_oldest_first(limit: int) -> None:
    service, _ = _make_service(max_messages=limit)
    over = limit + 2
    messages = [f"msg-{i}" for i in range(over)]

    for i, msg in enumerate(messages):
        role = "user" if i % 2 == 0 else "assistant"
        service.append_message(1, role, msg)

    history = service.get_history(1)
    assert len(history) == limit
    for i, expected in enumerate(messages[-limit:]):
        assert history[i]["content"] == expected


@pytest.mark.unit
async def test_maybe_compress_history_above_threshold_calls_summarizer_once() -> None:
    # threshold=3, keep_recent=2, max_messages=10 (no trim interference)
    service, ollama = _make_service(max_messages=10, threshold=3, keep_recent=2)
    for i in range(4):
        service.append_message(1, "user", f"msg-{i}")

    await service.maybe_compress_history(1)

    ollama.chat_once.assert_called_once()


@pytest.mark.unit
async def test_maybe_compress_history_below_threshold_no_summarizer_call() -> None:
    service, ollama = _make_service(max_messages=4, threshold=10, keep_recent=2)
    service.append_message(1, "user", "msg-1")
    service.append_message(1, "assistant", "msg-2")

    await service.maybe_compress_history(1)

    ollama.chat_once.assert_not_called()


@pytest.mark.unit
def test_per_user_isolation() -> None:
    service, _ = _make_service(max_messages=4)

    service.append_message(1, "user", "user-one-message")
    service.append_message(2, "user", "user-two-message")
    service.append_message(1, "assistant", "user-one-reply")

    history_1 = service.get_history(1)
    history_2 = service.get_history(2)

    assert len(history_1) == 2
    assert history_1[0]["content"] == "user-one-message"
    assert len(history_2) == 1
    assert history_2[0]["content"] == "user-two-message"
