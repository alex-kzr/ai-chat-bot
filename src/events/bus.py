from __future__ import annotations

import inspect
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, TypeVar

logger = logging.getLogger(__name__)

E = TypeVar("E")


class EventHandler(Protocol[E]):
    def __call__(self, event: E) -> Awaitable[None] | None: ...


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[type[Any], list[Callable[[Any], Awaitable[None] | None]]] = {}

    def subscribe(self, event_type: type[E], handler: EventHandler[E]) -> None:
        handlers = self._subscribers.setdefault(event_type, [])
        handlers.append(handler)  # type: ignore[arg-type]

    async def publish(self, event: Any) -> None:
        event_type = type(event)
        handlers = list(self._subscribers.get(event_type, []))

        logger.info("event_published type=%s subscribers=%s", event_type.__name__, len(handlers))
        for handler in handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception:
                logger.exception("event_handler_failed type=%s handler=%s", event_type.__name__, _handler_name(handler))


def _handler_name(handler: object) -> str:
    name = getattr(handler, "__name__", None)
    if isinstance(name, str) and name:
        return name
    return handler.__class__.__name__

