from __future__ import annotations

import pytest

from src.config import load_settings
from src.contracts import LLMReply
from src.events import MessageReceived, ResponseGenerated
from src.events.bus import EventBus
from src.modules.history import ConversationService
from src.runtime import _register_event_handlers
from src.services.chat_orchestrator import ChatOrchestrator


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
            "SYSTEM_PROMPT_ENABLED": "false",
            "CONTEXT_LOGGING_ENABLED": "false",
        },
        load_dotenv_file=False,
    )


class _AgentStub:
    async def run_task(self, _task: str) -> str:
        raise AssertionError("Agent path not expected in this test")


class _ChatStub:
    async def generate_response(self, _text: str, *, history, user_id):  # type: ignore[no-untyped-def]
        _ = history, user_id
        return LLMReply(llm_raw="hi", bot_reply="hi", thinking="")

    @staticmethod
    def format_for_user(reply: LLMReply, *, show_thinking: bool) -> str:  # noqa: ARG004
        return reply.bot_reply


@pytest.mark.asyncio
async def test_chat_orchestrator_publishes_events_and_history_subscriber_stores_messages() -> None:
    bus = EventBus()
    history = ConversationService(settings=_settings(), ollama=_GatewayStub())  # type: ignore[arg-type]
    _register_event_handlers(bus, history)

    published: list[str] = []

    def capture_message(_event: MessageReceived) -> None:
        published.append("message_received")

    def capture_response(_event: ResponseGenerated) -> None:
        published.append("response_generated")

    bus.subscribe(MessageReceived, capture_message)
    bus.subscribe(ResponseGenerated, capture_response)

    orchestrator = ChatOrchestrator(
        conversation=history,
        agent=_AgentStub(),  # type: ignore[arg-type]
        chat=_ChatStub(),  # type: ignore[arg-type]
        event_bus=bus,
        show_thinking=False,
    )

    outcome = await orchestrator.process_text(user_id=1, text="hello")
    assert outcome.reply == "hi"
    assert published == ["message_received", "response_generated"]

    snapshot = history.get_history(1)
    assert [m["role"] for m in snapshot] == ["user", "assistant"]
    assert [m["content"] for m in snapshot] == ["hello", "hi"]

