"""FEC-02 — unsupported (non-text) Telegram messages are ignored."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.handlers import handle_text
from tests._fakes import make_message


@pytest.mark.handlers
@pytest.mark.parametrize("field", ["photo", "voice", "sticker", "document"])
async def test_handle_text_text_none_is_ignored_and_does_not_call_orchestrator(handler_runtime, field: str) -> None:
    msg = make_message(text=None)
    setattr(msg, field, [MagicMock()])  # emulate aiogram attribute presence

    await handle_text(msg)

    handler_runtime.chat_orchestrator.process_text.assert_not_awaited()
    msg.answer.assert_not_awaited()
