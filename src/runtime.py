from __future__ import annotations

import logging
from dataclasses import dataclass

from .agent.service import AgentOrchestrator
from .config import Settings
from .context_logging import configure_context_logging
from .events import MessageReceived, ResponseGenerated
from .events.bus import EventBus
from .modules.chat import ChatService
from .modules.history import ConversationService
from .modules.users import UserService
from .ollama_gateway import OllamaGateway
from .services.chat_orchestrator import ChatOrchestrator
from .services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AppRuntime:
    settings: Settings
    users: UserService
    event_bus: EventBus
    ollama: OllamaGateway
    conversation: ConversationService
    chat_service: ChatService
    agent_orchestrator: AgentOrchestrator
    chat_orchestrator: ChatOrchestrator
    rate_limiter: RateLimiter


_runtime: AppRuntime | None = None
_runtime_override: AppRuntime | None = None
_runtime_override_stack: list[AppRuntime | None] = []


def create_runtime(settings: Settings) -> AppRuntime:
    configure_context_logging(settings)
    users = UserService()
    event_bus = EventBus()
    ollama = OllamaGateway(settings)
    conversation = ConversationService(settings=settings, ollama=ollama)
    _register_event_handlers(event_bus, conversation)
    chat_service = ChatService(settings=settings, ollama=ollama)
    agent_orchestrator = AgentOrchestrator()
    chat_orchestrator = ChatOrchestrator(
        conversation=conversation,
        agent=agent_orchestrator,
        chat=chat_service,
        event_bus=event_bus,
        show_thinking=settings.logging.show_thinking,
    )
    rate_limiter = RateLimiter(
        requests_per_minute=settings.security.rate_limit_requests_per_minute,
        burst=settings.security.rate_limit_burst,
    )
    return AppRuntime(
        settings=settings,
        users=users,
        event_bus=event_bus,
        ollama=ollama,
        conversation=conversation,
        chat_service=chat_service,
        agent_orchestrator=agent_orchestrator,
        chat_orchestrator=chat_orchestrator,
        rate_limiter=rate_limiter,
    )


def _register_event_handlers(event_bus: EventBus, conversation: ConversationService) -> None:
    event_bus.subscribe(MessageReceived, conversation.on_message_received)
    event_bus.subscribe(ResponseGenerated, conversation.on_response_generated)


def set_runtime(runtime: AppRuntime) -> None:
    global _runtime
    _runtime = runtime


def set_runtime_for_testing(runtime: AppRuntime) -> None:
    """Override runtime for tests without monkey-patching module internals.

    Test-only helper.
    """
    global _runtime_override
    _runtime_override_stack.append(_runtime_override)
    _runtime_override = runtime


def reset_runtime_for_testing() -> None:
    """Reset any active runtime override.

    Test-only helper.
    """
    global _runtime_override
    if _runtime_override_stack:
        _runtime_override = _runtime_override_stack.pop()
    else:
        _runtime_override = None


def get_runtime() -> AppRuntime:
    if _runtime_override is not None:
        return _runtime_override
    if _runtime is None:
        raise RuntimeError("Runtime is not initialized. Call bootstrap before starting handlers.")
    return _runtime
