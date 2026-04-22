from __future__ import annotations

import pytest

from src.config import load_settings
from src.modules.chat import ChatService


def _settings_for_tests():
    return load_settings(
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


@pytest.mark.asyncio
async def test_chat_service_recovers_when_stream_has_only_thinking() -> None:
    settings = _settings_for_tests()

    class FakeOllama:
        async def generate_streamed_text(self, *_args, **_kwargs):
            return "", "internal thoughts only"

        async def generate_once(self, *_args, **_kwargs):
            return "final answer from fallback"

    service = ChatService(settings=settings, ollama=FakeOllama())
    result = await service.generate_response("hello", history=[], user_id=1)

    assert result.bot_reply == "final answer from fallback"
    assert result.thinking == "internal thoughts only"
    assert result.llm_raw == "final answer from fallback\n\ninternal thoughts only"

