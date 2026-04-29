from __future__ import annotations

import pytest

from src.events import MessageReceived
from src.events.bus import EventBus
from src.runtime import create_runtime
from tests._fakes import FakeOllamaGateway


@pytest.mark.asyncio
async def test_create_runtime_accepts_injected_dependencies(fake_settings) -> None:
    """create_runtime allows deterministic fakes without monkey-patching globals."""
    bus = EventBus()
    gateway = FakeOllamaGateway()

    runtime = create_runtime(
        fake_settings,
        event_bus=bus,
        ollama=gateway,
        configure_logging=False,
    )

    assert runtime.event_bus is bus
    assert runtime.ollama is gateway

    await bus.publish(MessageReceived(user_id=1, text="hello"))
    snapshot = runtime.conversation.get_history(1)
    assert snapshot == [{"role": "user", "content": "hello"}]
