"""Smoke tests for the shared test infrastructure (conftest fixtures and _fakes helpers)."""
from __future__ import annotations

import pytest

from src.contracts import LLMReply
from src.runtime import AppRuntime
from tests._fakes import FakeOllamaGateway, make_message, make_message_with_failing_answer

# ---------------------------------------------------------------------------
# FakeOllamaGateway
# ---------------------------------------------------------------------------

@pytest.mark.unit
async def test_fake_gateway_returns_scripted_replies_in_order() -> None:
    """FakeOllamaGateway pops scripted replies in FIFO order."""
    r1 = LLMReply(llm_raw="r1", bot_reply="r1")
    r2 = LLMReply(llm_raw="r2", bot_reply="r2")
    gw = FakeOllamaGateway(script=[r1, r2])

    out1 = await gw.generate_once("p", model="m")
    out2 = await gw.generate_once("p", model="m")

    assert out1 == "r1"
    assert out2 == "r2"
    assert len(gw.calls) == 2


@pytest.mark.unit
async def test_fake_gateway_raises_scripted_exceptions() -> None:
    """FakeOllamaGateway raises exceptions that appear in the script."""
    gw = FakeOllamaGateway(script=[ValueError("boom")])

    with pytest.raises(ValueError, match="boom"):
        await gw.generate_once("p", model="m")


@pytest.mark.unit
async def test_fake_gateway_streamed_text_fires_callbacks() -> None:
    """generate_streamed_text fires on_thinking_chunk and on_content_chunk callbacks."""
    reply = LLMReply(llm_raw="raw", bot_reply="content", thinking="thought")
    gw = FakeOllamaGateway(script=[reply])

    thoughts: list[str] = []
    chunks: list[str] = []
    done_called: list[bool] = []

    content, thinking = await gw.generate_streamed_text(
        "p",
        model="m",
        on_thinking_chunk=thoughts.append,
        on_content_chunk=chunks.append,
        on_stream_done=lambda: done_called.append(True),
    )

    assert content == "content"
    assert thinking == "thought"
    assert thoughts == ["thought"]
    assert chunks == ["content"]
    assert done_called == [True]


@pytest.mark.unit
async def test_fake_gateway_chat_once_records_call() -> None:
    """chat_once records the method and model in calls."""
    reply = LLMReply(llm_raw="chat reply", bot_reply="chat reply")
    gw = FakeOllamaGateway(script=[reply])

    result = await gw.chat_once([{"role": "user", "content": "hi"}], model="chat-model")

    assert result == "chat reply"
    assert gw.calls[0].method == "chat_once"
    assert gw.calls[0].model == "chat-model"


@pytest.mark.unit
async def test_fake_gateway_list_models_returns_configured_models_and_records_call() -> None:
    """list_models returns configured models and records the call."""
    gw = FakeOllamaGateway(models=["m1", "m2"])

    models = await gw.list_models()

    assert models == ["m1", "m2"]
    assert gw.calls[0].method == "list_models"


# ---------------------------------------------------------------------------
# Telegram message builders
# ---------------------------------------------------------------------------

@pytest.mark.unit
async def test_make_message_exposes_expected_attributes() -> None:
    """make_message produces a mock with the attributes handler code reads."""
    msg = make_message(text="hello", user_id=99, username="bob", chat_id=99)

    assert msg.text == "hello"
    assert msg.from_user.id == 99
    assert msg.from_user.username == "bob"
    assert msg.chat.id == 99

    await msg.answer("reply")
    msg.answer.assert_awaited_once_with("reply")


@pytest.mark.unit
async def test_make_message_with_failing_answer_raises() -> None:
    """make_message_with_failing_answer raises on answer()."""
    msg = make_message_with_failing_answer(exc=RuntimeError("API down"))

    with pytest.raises(RuntimeError, match="API down"):
        await msg.answer("anything")


# ---------------------------------------------------------------------------
# fake_runtime fixture wiring (uses conftest.py fixtures)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fake_runtime_is_app_runtime_instance(fake_runtime: AppRuntime) -> None:
    """fake_runtime is a real AppRuntime, not a generic mock."""
    assert isinstance(fake_runtime, AppRuntime)


@pytest.mark.unit
def test_fake_runtime_settings_have_test_values(fake_runtime: AppRuntime) -> None:
    """fake_runtime uses small MAX_HISTORY_MESSAGES and modest input cap."""
    assert fake_runtime.settings.history.max_messages == 4
    assert fake_runtime.settings.security.max_user_input_chars == 200


@pytest.mark.unit
async def test_fake_runtime_rate_limiter_allows_by_default(fake_runtime: AppRuntime) -> None:
    """rate_limiter in fake_runtime allows requests by default."""
    allowed = await fake_runtime.rate_limiter.is_allowed(42)
    assert allowed is True
