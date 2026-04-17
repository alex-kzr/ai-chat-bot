from __future__ import annotations

import logging
from dataclasses import dataclass

from .config import Settings
from .conversation import ConversationService
from .ollama_gateway import OllamaGateway
from .services.chat_orchestrator import ChatOrchestrator
from .agent.service import AgentOrchestrator
from .context_logging import configure_context_logging

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AppRuntime:
    settings: Settings
    ollama: OllamaGateway
    conversation: ConversationService
    agent_orchestrator: AgentOrchestrator
    chat_orchestrator: ChatOrchestrator


_runtime: AppRuntime | None = None


def create_runtime(settings: Settings) -> AppRuntime:
    configure_context_logging(settings)
    ollama = OllamaGateway(settings)
    conversation = ConversationService(settings=settings, ollama=ollama)
    agent_orchestrator = AgentOrchestrator()
    chat_orchestrator = ChatOrchestrator(
        conversation=conversation,
        agent=agent_orchestrator,
        show_thinking=settings.logging.show_thinking,
    )
    return AppRuntime(
        settings=settings,
        ollama=ollama,
        conversation=conversation,
        agent_orchestrator=agent_orchestrator,
        chat_orchestrator=chat_orchestrator,
    )


def set_runtime(runtime: AppRuntime) -> None:
    global _runtime
    _runtime = runtime


def get_runtime() -> AppRuntime:
    if _runtime is None:
        raise RuntimeError("Runtime is not initialized. Call bootstrap before starting handlers.")
    return _runtime
