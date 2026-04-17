from __future__ import annotations

import pytest

from src.config import load_settings
from src.conversation import ConversationService


class _GatewayStub:
    async def chat_once(self, messages, *, model: str) -> str:  # type: ignore[no-untyped-def]
        _ = messages, model
        return "summary text"


def _settings():
    return load_settings(
        env={
            "BOT_TOKEN": "token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "qwen3:0.6b",
            "MAX_HISTORY_MESSAGES": "3",
            "SUMMARY_THRESHOLD": "4",
            "SUMMARY_KEEP_RECENT": "2",
        },
        load_dotenv_file=False,
    )


def test_trim_history_on_append() -> None:
    svc = ConversationService(settings=_settings(), ollama=_GatewayStub())  # type: ignore[arg-type]
    user_id = 100
    svc.append_message(user_id, "user", "1")
    svc.append_message(user_id, "user", "2")
    svc.append_message(user_id, "user", "3")
    svc.append_message(user_id, "user", "4")
    history = svc.get_history(user_id)
    assert [m["content"] for m in history] == ["2", "3", "4"]


@pytest.mark.asyncio
async def test_summarization_replaces_old_messages() -> None:
    svc = ConversationService(settings=_settings(), ollama=_GatewayStub())  # type: ignore[arg-type]
    user_id = 200
    for idx in range(5):
        svc.append_message(user_id, "user", f"m{idx}")

    await svc.maybe_compress_history(user_id)

    history = svc.get_history(user_id)
    assert len(history) == 3
    assert history[0]["role"] == "system"
    assert "[Conversation summary]" in history[0]["content"]
    assert [m["content"] for m in history[1:]] == ["m3", "m4"]
