"""FEC-04 — Telegram API failures when sending replies are handled gracefully."""
from __future__ import annotations

import asyncio

import pytest

from src.handlers import handle_agent, handle_text
from tests._fakes import make_message_with_failing_answer


@pytest.mark.handlers
@pytest.mark.parametrize("exc", [RuntimeError("Telegram failed"), ConnectionError("network")])
async def test_handle_text_when_message_answer_raises_logs_and_does_not_reraise(
    caplog,
    handler_runtime,
    monkeypatch,
    exc: Exception,
) -> None:
    typing_cancel_calls = 0
    created_tasks: list[asyncio.Task] = []
    real_create_task = asyncio.create_task

    def _spy_create_task(coro, *args, **kwargs):  # type: ignore[no-untyped-def]
        nonlocal typing_cancel_calls
        task = real_create_task(coro, *args, **kwargs)
        created_tasks.append(task)
        coro_name = getattr(getattr(task, "get_coro", lambda: None)(), "__name__", "")
        if coro_name == "_keep_typing":
            real_cancel = task.cancel

            def _spy_cancel(*c_args, **c_kwargs):  # type: ignore[no-untyped-def]
                nonlocal typing_cancel_calls
                typing_cancel_calls += 1
                return real_cancel(*c_args, **c_kwargs)

            task.cancel = _spy_cancel  # type: ignore[method-assign]
        return task

    monkeypatch.setattr("src.handlers.asyncio.create_task", _spy_create_task)

    msg = make_message_with_failing_answer(exc=exc, text="my token is 123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    with caplog.at_level("INFO"):
        await handle_text(msg)
        await asyncio.sleep(0)

    assert typing_cancel_calls >= 1
    assert any("telegram_answer_failed" in r.getMessage() for r in caplog.records)
    assert "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ" not in "\n".join(r.getMessage() for r in caplog.records)


@pytest.mark.handlers
async def test_handle_agent_when_message_answer_raises_logs_and_does_not_reraise(
    caplog,
    handler_runtime,
) -> None:
    msg = make_message_with_failing_answer(exc=RuntimeError("Telegram failed"), text="/agent hello")

    with caplog.at_level("ERROR"):
        await handle_agent(msg)

    assert any("telegram_answer_failed" in r.getMessage() for r in caplog.records)
