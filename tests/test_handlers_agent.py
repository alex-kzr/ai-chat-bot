"""THC-03 — /agent handler command parsing tests."""
from __future__ import annotations

import pytest

from src.handlers import handle_agent
from tests._fakes import make_message


@pytest.mark.handlers
async def test_handle_agent_empty_body_replies_with_usage_hint(handler_runtime) -> None:
    msg = make_message(text="/agent   ")

    await handle_agent(msg)

    msg.answer.assert_awaited_once()
    assert "Usage: `/agent <task>`" in msg.answer.await_args.args[0]
    assert handler_runtime.agent_orchestrator.run_task.await_count == 0


@pytest.mark.handlers
async def test_handle_agent_valid_body_dispatches_to_agent_and_replies(handler_runtime) -> None:
    handler_runtime.agent_orchestrator.run_task.return_value = "42"
    msg = make_message(text="/agent What is 12*15?")

    await handle_agent(msg)

    handler_runtime.agent_orchestrator.run_task.assert_awaited_once_with("What is 12*15?")
    msg.answer.assert_awaited_once_with("42")


@pytest.mark.handlers
async def test_handle_agent_oversize_task_rejected_before_agent_runs(handler_runtime) -> None:
    max_chars = handler_runtime.settings.security.max_user_input_chars
    msg = make_message(text="/agent " + ("a" * (max_chars + 1)))

    await handle_agent(msg)

    msg.answer.assert_awaited_once_with(f"Task is too long (max {max_chars} characters).")
    assert handler_runtime.agent_orchestrator.run_task.await_count == 0
    assert handler_runtime.conversation.mock_calls == []


@pytest.mark.handlers
async def test_handle_agent_rate_limited_user_replies_slow_down(handler_runtime) -> None:
    handler_runtime.rate_limiter.is_allowed.return_value = False
    msg = make_message(text="/agent Hello")

    await handle_agent(msg)

    msg.answer.assert_awaited_once_with("You're sending requests too quickly. Please slow down.")
    assert handler_runtime.agent_orchestrator.run_task.await_count == 0


@pytest.mark.handlers
async def test_handle_agent_empty_agent_reply_uses_fallback_phrase(monkeypatch, handler_runtime) -> None:
    handler_runtime.agent_orchestrator.run_task.return_value = ""
    monkeypatch.setattr("src.handlers.random.choice", lambda phrases: "fallback phrase")
    msg = make_message(text="/agent Hello")

    await handle_agent(msg)

    msg.answer.assert_awaited_once_with("fallback phrase")

