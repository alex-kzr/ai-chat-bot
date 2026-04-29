"""THC-01 — /start handler contract tests."""
from __future__ import annotations

import pytest

from src.handlers import WELCOME_MESSAGE, handle_start
from tests._fakes import make_message


@pytest.mark.handlers
async def test_handle_start_replies_with_welcome_message(handler_runtime) -> None:
    msg = make_message(text="/start")

    await handle_start(msg)

    msg.answer.assert_awaited_once_with(WELCOME_MESSAGE)


@pytest.mark.handlers
async def test_handle_start_does_not_call_orchestrators_or_rate_limiter(handler_runtime) -> None:
    msg = make_message(text="/start")

    await handle_start(msg)

    assert handler_runtime.chat_orchestrator.process_text.await_count == 0
    assert handler_runtime.agent_orchestrator.run_task.await_count == 0
    assert handler_runtime.rate_limiter.is_allowed.await_count == 0

