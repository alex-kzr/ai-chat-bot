"""BLC-01 — ChatService request/response cycle tests."""
from __future__ import annotations

import pytest

from src.config import Settings, load_settings
from src.contracts import ChatMessage, LLMReply
from src.modules.chat.service import ChatService
from tests._fakes import FakeOllamaGateway


def _settings(*, system_prompt_enabled: bool = False) -> Settings:
    return load_settings(
        env={
            "BOT_TOKEN": "test-token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "test-model",
            "CONTEXT_LOGGING_ENABLED": "false",
            "SYSTEM_PROMPT_ENABLED": "true" if system_prompt_enabled else "false",
            "SYSTEM_PROMPT": "You are a helpful assistant.",
        },
        load_dotenv_file=False,
    )


@pytest.mark.unit
async def test_generate_response_calls_gateway_exactly_once() -> None:
    gateway = FakeOllamaGateway(script=[LLMReply(llm_raw="hi", bot_reply="hi")])
    service = ChatService(settings=_settings(), ollama=gateway)

    await service.generate_response("hello", history=[])

    assert len(gateway.calls) == 1


@pytest.mark.unit
async def test_generate_response_prompt_contains_system_history_user_in_order() -> None:
    # In the real flow the new user message is already the last item in history
    # (MessageReceived appends before get_history is called in ChatOrchestrator).
    history: list[ChatMessage] = [
        {"role": "user", "content": "previous question"},
        {"role": "assistant", "content": "previous answer"},
        {"role": "user", "content": "new question"},
    ]
    gateway = FakeOllamaGateway(script=[LLMReply(llm_raw="reply", bot_reply="reply")])
    service = ChatService(settings=_settings(system_prompt_enabled=True), ollama=gateway)

    await service.generate_response("new question", history=history)

    prompt = gateway.calls[0].prompt
    assert prompt is not None
    assert "You are a helpful assistant." in prompt
    assert "previous question" in prompt
    assert "previous answer" in prompt
    assert "new question" in prompt
    # System prompt precedes history; earlier history precedes later history.
    assert prompt.index("You are a helpful assistant.") < prompt.index("previous question")
    assert prompt.index("previous answer") < prompt.index("new question")


@pytest.mark.unit
async def test_generate_response_bot_reply_matches_gateway_script() -> None:
    gateway = FakeOllamaGateway(script=[LLMReply(llm_raw="the answer", bot_reply="the answer")])
    service = ChatService(settings=_settings(), ollama=gateway)

    result = await service.generate_response("what?", history=[])

    assert result.bot_reply == "the answer"


@pytest.mark.unit
@pytest.mark.parametrize(
    "thinking_text,expect_non_empty",
    [
        ("deep internal reasoning", True),
        ("", False),
    ],
    ids=["thinking-present", "thinking-absent"],
)
async def test_generate_response_thinking_field_preserved(
    thinking_text: str, expect_non_empty: bool
) -> None:
    gateway = FakeOllamaGateway(
        script=[LLMReply(llm_raw="answer", bot_reply="answer", thinking=thinking_text)]
    )
    service = ChatService(settings=_settings(), ollama=gateway)

    result = await service.generate_response("hello", history=[])

    assert bool(result.thinking) == expect_non_empty
    if expect_non_empty:
        assert result.thinking == thinking_text


@pytest.mark.unit
async def test_generate_response_does_not_mutate_history() -> None:
    history: list[ChatMessage] = [{"role": "user", "content": "original"}]
    snapshot = list(history)
    gateway = FakeOllamaGateway(script=[LLMReply(llm_raw="ok", bot_reply="ok")])
    service = ChatService(settings=_settings(), ollama=gateway)

    await service.generate_response("follow-up", history=history)

    assert history == snapshot
