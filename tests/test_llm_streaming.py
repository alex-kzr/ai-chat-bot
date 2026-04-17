from __future__ import annotations

import logging
from types import SimpleNamespace

import pytest

from src.config import load_settings
from src.llm import ask_llm
from src.prompts import ERROR_PHRASES


def _settings_for_tests():
    settings = load_settings(
        env={
            "BOT_TOKEN": "token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "qwen3:0.6b",
            "LOG_LEVEL": "DEBUG",
            "CONTEXT_LOGGING_ENABLED": "false",
            "SYSTEM_PROMPT_ENABLED": "false",
        },
        load_dotenv_file=False,
    )
    return settings


@pytest.mark.asyncio
async def test_ask_llm_recovers_when_stream_has_only_thinking(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_for_tests()

    class FakeOllama:
        async def generate_streamed_text(self, *_args, **_kwargs):
            return "", "internal thoughts only"

        async def generate_once(self, *_args, **_kwargs):
            return "final answer from fallback"

    monkeypatch.setattr(
        "src.runtime.get_runtime",
        lambda: SimpleNamespace(settings=settings, ollama=FakeOllama()),
    )

    result = await ask_llm("hello", history=[], user_id=1)
    assert result.bot_reply == "final answer from fallback"
    assert result.thinking == "internal thoughts only"
    assert result.llm_raw == "final answer from fallback\n\ninternal thoughts only"


@pytest.mark.asyncio
async def test_ask_llm_returns_error_when_stream_and_fallback_are_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_for_tests()

    class FakeOllama:
        async def generate_streamed_text(self, *_args, **_kwargs):
            return "", "internal thoughts only"

        async def generate_once(self, *_args, **_kwargs):
            return ""

    monkeypatch.setattr(
        "src.runtime.get_runtime",
        lambda: SimpleNamespace(settings=settings, ollama=FakeOllama()),
    )

    result = await ask_llm("hello", history=[], user_id=1)
    assert result.llm_raw == "[error]"
    assert result.bot_reply in ERROR_PHRASES
    assert result.thinking == ""


@pytest.mark.asyncio
async def test_ask_llm_logs_thinking_stream_by_lines(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
    request,  # noqa: ARG001
) -> None:
    settings = _settings_for_tests()

    class FakeOllama:
        async def generate_streamed_text(self, *_args, **kwargs):
            on_thinking_chunk = kwargs.get("on_thinking_chunk")
            assert on_thinking_chunk is not None
            on_thinking_chunk("line one")
            on_thinking_chunk(" extended\nline two")
            on_thinking_chunk(" tail")
            return "done", "line one extended\nline two tail"

    monkeypatch.setattr(
        "src.runtime.get_runtime",
        lambda: SimpleNamespace(settings=settings, ollama=FakeOllama()),
    )

    with caplog.at_level(logging.DEBUG, logger="src.llm"):
        await ask_llm("hello", history=[], user_id=1)
    think_logs = [r.getMessage() for r in caplog.records if "<<< THINK:" in r.getMessage()]
    assert think_logs == [
        "<<< THINK: line one extended",
        "<<< THINK: line two tail",
    ]
