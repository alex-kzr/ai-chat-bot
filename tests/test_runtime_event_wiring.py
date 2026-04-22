from __future__ import annotations

import pytest

from src.config import load_settings
from src.events import MessageReceived, ResponseGenerated
from src.events.bus import EventBus
from src.modules.history import ConversationService
from src.runtime import _register_event_handlers


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
            "MAX_HISTORY_MESSAGES": "50",
            "SUMMARY_THRESHOLD": "999",
            "SUMMARY_KEEP_RECENT": "2",
        },
        load_dotenv_file=False,
    )


@pytest.mark.asyncio
async def test_runtime_registers_history_subscribers() -> None:
    bus = EventBus()
    history = ConversationService(settings=_settings(), ollama=_GatewayStub())  # type: ignore[arg-type]
    _register_event_handlers(bus, history)

    await bus.publish(MessageReceived(user_id=1, text="hello"))
    await bus.publish(ResponseGenerated(user_id=1, reply="hi", used_agent=False))

    snapshot = history.get_history(1)
    assert [m["role"] for m in snapshot] == ["user", "assistant"]
    assert [m["content"] for m in snapshot] == ["hello", "hi"]

