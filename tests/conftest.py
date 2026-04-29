"""Shared pytest fixtures for the ai-chat-bot test suite."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.config import Settings, load_settings
from src.events.bus import EventBus
from src.modules.users import UserService
from src.runtime import (
    AppRuntime,
    reset_runtime_for_testing,
    set_runtime_for_testing,
)
from src.services.chat_orchestrator import ChatOutcome

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def fake_settings() -> Settings:
    """Deterministic Settings for tests: small history, modest input cap, generous rate limits."""
    return load_settings(
        env={
            "BOT_TOKEN": "test-token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "test-model",
            "MAX_HISTORY_MESSAGES": "4",
            "MAX_USER_INPUT_CHARS": "200",
            "RATE_LIMIT_REQUESTS_PER_MINUTE": "10000",
            "RATE_LIMIT_BURST": "10000",
            "SUMMARY_THRESHOLD": "999",
            "SUMMARY_KEEP_RECENT": "2",
            "SYSTEM_PROMPT_ENABLED": "false",
            "CONTEXT_LOGGING_ENABLED": "false",
        },
        load_dotenv_file=False,
    )


# ---------------------------------------------------------------------------
# Infrastructure stubs
# ---------------------------------------------------------------------------

@pytest.fixture
def event_bus() -> EventBus:
    """Fresh in-memory EventBus per test."""
    return EventBus()


@pytest.fixture
def user_service() -> UserService:
    """Fresh UserService per test."""
    return UserService()


@pytest.fixture
def rate_limiter() -> AsyncMock:
    """AsyncMock-backed rate limiter that always allows by default.

    To deny a request in a specific test, set:
        rate_limiter.is_allowed.return_value = False
    """
    mock = AsyncMock()
    mock.is_allowed.return_value = True
    return mock


# ---------------------------------------------------------------------------
# Orchestrator stubs
# ---------------------------------------------------------------------------

@pytest.fixture
def chat_orchestrator() -> AsyncMock:
    """AsyncMock ChatOrchestrator; process_text returns a successful ChatOutcome."""
    mock = AsyncMock()
    mock.process_text.return_value = ChatOutcome(
        reply="test reply",
        llm_raw="test reply",
        used_agent=False,
    )
    return mock


@pytest.fixture
def agent_orchestrator() -> AsyncMock:
    """AsyncMock AgentOrchestrator; run_task returns a plain string."""
    mock = AsyncMock()
    mock.run_task.return_value = "agent result"
    return mock


# ---------------------------------------------------------------------------
# Composite runtime
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_runtime(
    fake_settings: Settings,
    event_bus: EventBus,
    user_service: UserService,
    rate_limiter: AsyncMock,
    chat_orchestrator: AsyncMock,
    agent_orchestrator: AsyncMock,
) -> AppRuntime:
    """Fully-wired AppRuntime backed by fakes and mocks for handler tests.

    I/O boundaries (ollama, conversation, chat_service) are MagicMocks.
    Orchestrators and rate limiter are AsyncMocks so tests can inspect calls.
    """
    return AppRuntime(
        settings=fake_settings,
        users=user_service,
        event_bus=event_bus,
        ollama=MagicMock(),
        conversation=MagicMock(),
        chat_service=MagicMock(),
        agent_orchestrator=agent_orchestrator,
        chat_orchestrator=chat_orchestrator,
        rate_limiter=rate_limiter,
    )


# ---------------------------------------------------------------------------
# Handler-level runtime injection
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def session_fake_runtime(fake_settings: Settings) -> AppRuntime:
    """Session-scoped fake AppRuntime for tests that want a stable global runtime."""
    return AppRuntime(
        settings=fake_settings,
        users=UserService(),
        event_bus=EventBus(),
        ollama=MagicMock(),
        conversation=MagicMock(),
        chat_service=MagicMock(),
        agent_orchestrator=AsyncMock(),
        chat_orchestrator=AsyncMock(),
        rate_limiter=AsyncMock(),
    )


@pytest.fixture(scope="session")
def runtime_override_session(session_fake_runtime: AppRuntime) -> AppRuntime:
    """Set a global runtime override for the duration of a test session."""
    set_runtime_for_testing(session_fake_runtime)
    try:
        yield session_fake_runtime
    finally:
        reset_runtime_for_testing()


@pytest.fixture
def handler_runtime(fake_runtime: AppRuntime) -> AppRuntime:
    """Provide a fake runtime to handlers via src.runtime's test-only override seam."""
    set_runtime_for_testing(fake_runtime)
    try:
        yield fake_runtime
    finally:
        reset_runtime_for_testing()


# ---------------------------------------------------------------------------
# Smoke test for the fixture wiring
# ---------------------------------------------------------------------------

def test_fake_runtime_components_are_wired(
    fake_runtime: AppRuntime,
    fake_settings: Settings,
    event_bus: EventBus,
    user_service: UserService,
) -> None:
    """Verify fake_runtime exposes all expected components."""
    assert fake_runtime.settings is fake_settings
    assert fake_runtime.event_bus is event_bus
    assert fake_runtime.users is user_service
    assert fake_runtime.chat_orchestrator is not None
    assert fake_runtime.agent_orchestrator is not None
    assert fake_runtime.rate_limiter is not None
    assert fake_runtime.settings.history.max_messages == 4
    assert fake_runtime.settings.security.max_user_input_chars == 200
