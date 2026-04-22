from __future__ import annotations

import pytest

from src.events.bus import EventBus
from src.events.contracts import MessageReceived


@pytest.mark.asyncio
async def test_event_bus_runs_all_subscribers_and_contains_failures() -> None:
    bus = EventBus()
    calls: list[str] = []

    async def good(_event: MessageReceived) -> None:
        calls.append("good")

    def bad(_event: MessageReceived) -> None:
        calls.append("bad")
        raise RuntimeError("boom")

    bus.subscribe(MessageReceived, bad)
    bus.subscribe(MessageReceived, good)

    await bus.publish(MessageReceived(user_id=1, text="hi"))

    assert calls == ["bad", "good"]

