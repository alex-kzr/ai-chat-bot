"""FEC-03 — LLM/orchestrator failures return a graceful fallback reply."""
from __future__ import annotations

import httpx
import pytest

from src.prompts import ERROR_PHRASES
from src.handlers import handle_text
from tests._fakes import make_message


def _http_status_error() -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "http://localhost:11434/api/chat")
    response = httpx.Response(500, request=request)
    return httpx.HTTPStatusError("500 server error", request=request, response=response)


@pytest.mark.handlers
@pytest.mark.parametrize(
    "exc",
    [
        httpx.TimeoutException("timeout API_KEY=sk-test"),
        _http_status_error(),
        RuntimeError("boom API_KEY=sk-test"),
    ],
)
async def test_handle_text_when_orchestrator_raises_replies_with_error_phrase_and_does_not_leak_sensitive_details(
    caplog,
    handler_runtime,
    exc: Exception,
) -> None:
    handler_runtime.chat_orchestrator.process_text.side_effect = exc
    msg = make_message(text="hello")

    with caplog.at_level("ERROR"):
        await handle_text(msg)

    handler_runtime.chat_orchestrator.process_text.assert_awaited_once()
    msg.answer.assert_awaited()

    sent = msg.answer.await_args.args[0]
    assert sent in ERROR_PHRASES

    logged = [r.getMessage() for r in caplog.records if "chat_orchestrator_failed" in r.getMessage()]
    assert len(logged) == 1
    assert "API_KEY=sk-test" not in "".join(logged)
