"""THC-02 — handle_text happy-path handler tests."""
from __future__ import annotations

import asyncio

import pytest

from src.events import UserCreated
from src.handlers import handle_text
from tests._fakes import make_message


@pytest.mark.handlers
async def test_handle_text_first_message_publishes_user_created(handler_runtime) -> None:
    published: list[UserCreated] = []
    handler_runtime.event_bus.subscribe(UserCreated, lambda e: published.append(e))

    msg = make_message(text="  hello  ", user_id=42, username="alice")

    await handle_text(msg)

    assert len(published) == 1
    assert published[0].user_id == 42
    assert published[0].username == "alice"


@pytest.mark.handlers
async def test_handle_text_returning_user_does_not_publish_user_created(handler_runtime) -> None:
    # Arrange: create the user in the in-memory repo up-front.
    handler_runtime.users.get_or_create(telegram_user_id=42, username="alice")

    published: list[UserCreated] = []
    handler_runtime.event_bus.subscribe(UserCreated, lambda e: published.append(e))

    msg = make_message(text="hi", user_id=42, username="alice")

    await handle_text(msg)

    assert published == []


@pytest.mark.handlers
async def test_handle_text_calls_orchestrator_and_replies_and_schedules_log_task(monkeypatch, handler_runtime) -> None:
    created_tasks: list[asyncio.Task] = []
    handlers_create_task = asyncio.create_task

    def _spy_create_task(coro, *args, **kwargs):  # type: ignore[no-untyped-def]
        task = handlers_create_task(coro, *args, **kwargs)
        created_tasks.append(task)
        return task

    # src.handlers imports asyncio at module level; patch that reference to spy.
    monkeypatch.setattr("src.handlers.asyncio.create_task", _spy_create_task)

    msg = make_message(text="  hello world  ", user_id=42, username="alice")

    await handle_text(msg)

    handler_runtime.chat_orchestrator.process_text.assert_awaited_once_with(42, "hello world")
    msg.answer.assert_awaited_once_with("test reply")

    # Expect: typing task + _log_response task.
    assert len(created_tasks) >= 2
    assert any(getattr(t.get_coro(), "__name__", "") == "_log_response" for t in created_tasks)

