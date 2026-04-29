"""THC-04 — message chunking and typing indicator tests."""
from __future__ import annotations

import asyncio

import pytest

from src.handlers import _TELEGRAM_MAX_LEN, _keep_typing, _split_message
from tests._fakes import make_message


@pytest.mark.handlers
@pytest.mark.parametrize(
    "text",
    [
        pytest.param("a" * (_TELEGRAM_MAX_LEN - 1), id="under-limit"),
        pytest.param("a" * _TELEGRAM_MAX_LEN, id="exact-limit"),
        pytest.param("a" * (_TELEGRAM_MAX_LEN + 1), id="over-limit"),
        pytest.param("a" * (_TELEGRAM_MAX_LEN * 2 + 5), id="multi-chunk"),
    ],
)
async def test_split_message_chunks_join_back_to_input(text: str) -> None:
    parts = _split_message(text, limit=_TELEGRAM_MAX_LEN)

    assert "".join(parts) == text
    assert parts, "Expected at least one chunk"
    assert all(len(p) <= _TELEGRAM_MAX_LEN for p in parts)
    if len(text) <= _TELEGRAM_MAX_LEN:
        assert parts == [text]


@pytest.mark.handlers
async def test_keep_typing_exits_promptly_when_stop_is_set(monkeypatch) -> None:
    stop = asyncio.Event()
    msg = make_message()
    real_sleep = asyncio.sleep

    async def _send_chat_action(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        stop.set()

    msg.bot.send_chat_action.side_effect = _send_chat_action

    async def _fast_sleep(_seconds: float) -> None:
        # Avoid a real 4s delay while still yielding to the event loop.
        await real_sleep(0)

    monkeypatch.setattr("src.handlers.asyncio.sleep", _fast_sleep)

    task = asyncio.create_task(_keep_typing(msg, stop))
    await asyncio.wait_for(task, timeout=0.5)

    assert msg.bot.send_chat_action.await_count >= 1


@pytest.mark.handlers
async def test_keep_typing_can_be_cancelled_cleanly(monkeypatch) -> None:
    stop = asyncio.Event()
    msg = make_message()
    real_sleep = asyncio.sleep

    async def _fast_sleep(_seconds: float) -> None:
        await real_sleep(0)

    monkeypatch.setattr("src.handlers.asyncio.sleep", _fast_sleep)

    task = asyncio.create_task(_keep_typing(msg, stop))
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
