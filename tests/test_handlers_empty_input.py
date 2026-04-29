"""FEC-01 — empty and whitespace-only input handler tests."""
from __future__ import annotations

import pytest

from src.events import MessageReceived
from src.handlers import handle_agent, handle_text
from tests._fakes import make_message


@pytest.mark.handlers
@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
async def test_handle_text_empty_or_whitespace_is_noop_and_does_not_call_orchestrator(handler_runtime, text: str) -> None:
    published: list[MessageReceived] = []
    handler_runtime.event_bus.subscribe(MessageReceived, lambda e: published.append(e))

    msg = make_message(text=text, user_id=42, username="alice")

    await handle_text(msg)

    handler_runtime.chat_orchestrator.process_text.assert_not_awaited()
    msg.answer.assert_not_awaited()
    assert published == []


@pytest.mark.handlers
@pytest.mark.parametrize("text", ["/agent", "/agent   "])
async def test_handle_agent_empty_task_replies_with_usage_and_does_not_run_agent(handler_runtime, text: str) -> None:
    msg = make_message(text=text, user_id=42, username="alice")

    await handle_agent(msg)

    handler_runtime.agent_orchestrator.run_task.assert_not_awaited()
    msg.answer.assert_awaited()
