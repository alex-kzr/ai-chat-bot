"""BLC-03 — ChatOrchestrator routing and event-ordering tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.contracts import LLMReply
from src.events import MessageReceived, ResponseGenerated
from src.events.bus import EventBus
from src.services.chat_orchestrator import ChatOrchestrator


def _make_deps() -> tuple[EventBus, AsyncMock, MagicMock, AsyncMock]:
    event_bus = EventBus()

    chat = AsyncMock()
    chat.generate_response.return_value = LLMReply(llm_raw="hello", bot_reply="hello")
    # format_for_user is a static (sync) method — override so it doesn't return a coroutine.
    chat.format_for_user = MagicMock(return_value="hello")

    conversation = MagicMock()
    conversation.get_history.return_value = []
    conversation.maybe_compress_history = AsyncMock(return_value=None)

    agent = AsyncMock()
    agent.run_task.return_value = "agent answer"

    return event_bus, chat, conversation, agent


def _make_orchestrator(
    event_bus: EventBus,
    chat: AsyncMock,
    conversation: MagicMock,
    agent: AsyncMock,
    show_thinking: bool = False,
) -> ChatOrchestrator:
    return ChatOrchestrator(
        conversation=conversation,
        agent=agent,
        chat=chat,
        event_bus=event_bus,
        show_thinking=show_thinking,
    )


@pytest.mark.unit
async def test_plain_text_publishes_message_received_before_response_generated() -> None:
    event_bus, chat, conversation, agent = _make_deps()
    published: list = []
    event_bus.subscribe(MessageReceived, lambda e: published.append(e))
    event_bus.subscribe(ResponseGenerated, lambda e: published.append(e))

    orchestrator = _make_orchestrator(event_bus, chat, conversation, agent)
    await orchestrator.process_text(user_id=10, text="hello there")

    types = [type(e) for e in published]
    assert MessageReceived in types
    assert ResponseGenerated in types
    assert types.index(MessageReceived) < types.index(ResponseGenerated)


@pytest.mark.unit
async def test_plain_text_reply_matches_gateway_script() -> None:
    event_bus, chat, conversation, agent = _make_deps()
    chat.generate_response.return_value = LLMReply(llm_raw="scripted reply", bot_reply="scripted reply")
    chat.format_for_user = MagicMock(return_value="scripted reply")

    orchestrator = _make_orchestrator(event_bus, chat, conversation, agent)
    outcome = await orchestrator.process_text(user_id=5, text="what?")

    assert outcome.reply == "scripted reply"
    assert not outcome.used_agent


@pytest.mark.unit
async def test_url_text_routes_to_agent_not_chat() -> None:
    event_bus, chat, conversation, agent = _make_deps()
    orchestrator = _make_orchestrator(event_bus, chat, conversation, agent)

    outcome = await orchestrator.process_text(user_id=5, text="check https://example.com for me")

    agent.run_task.assert_called_once()
    chat.generate_response.assert_not_called()
    assert outcome.used_agent


@pytest.mark.unit
async def test_chat_failure_publishes_message_received_not_response_generated() -> None:
    event_bus, chat, conversation, agent = _make_deps()
    chat.generate_response.side_effect = RuntimeError("LLM exploded")
    published: list = []
    event_bus.subscribe(MessageReceived, lambda e: published.append(e))
    event_bus.subscribe(ResponseGenerated, lambda e: published.append(e))

    orchestrator = _make_orchestrator(event_bus, chat, conversation, agent)
    with pytest.raises(RuntimeError, match="LLM exploded"):
        await orchestrator.process_text(user_id=7, text="trigger failure")

    types = [type(e) for e in published]
    assert MessageReceived in types
    assert ResponseGenerated not in types


@pytest.mark.unit
async def test_events_tagged_with_correct_user_id() -> None:
    event_bus, chat, conversation, agent = _make_deps()
    published: list = []
    event_bus.subscribe(MessageReceived, lambda e: published.append(e))
    event_bus.subscribe(ResponseGenerated, lambda e: published.append(e))

    orchestrator = _make_orchestrator(event_bus, chat, conversation, agent)
    await orchestrator.process_text(user_id=99, text="hello")

    assert published, "No events published"
    for event in published:
        assert event.user_id == 99
