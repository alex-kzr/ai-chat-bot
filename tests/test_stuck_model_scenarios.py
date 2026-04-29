from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from src.agent.core import run_agent
from src.config import load_settings
from src.context_logging import configure_context_logging
from src.contracts import LLMReply
from src.errors import OllamaTransportError
from src.ollama_gateway import OllamaGateway
from src.runtime import AppRuntime

from tests._fakes import FakeOllamaGateway


def _parse_context_log(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split(" | ", 2)
        if len(parts) != 3:
            continue
        try:
            records.append(json.loads(parts[2]))
        except json.JSONDecodeError:
            continue
    return records


def _settings(*, log_path: Path, env_overrides: dict[str, str] | None = None):
    env = {
        "BOT_TOKEN": "test-token",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "test-model",
        "CONTEXT_LOGGING_ENABLED": "true",
        "LOG_DESTINATION": "file",
        "LOG_FILE_PATH": str(log_path),
        "LOG_FORMAT": "json",
        "SYSTEM_PROMPT_ENABLED": "false",
    }
    if env_overrides:
        env |= env_overrides
    return load_settings(env=env, load_dotenv_file=False)


def _make_runtime(gateway: FakeOllamaGateway, *, settings) -> AppRuntime:
    from unittest.mock import MagicMock

    configure_context_logging(settings)
    return AppRuntime(
        settings=settings,
        users=MagicMock(),
        event_bus=MagicMock(),
        ollama=gateway,
        conversation=MagicMock(),
        chat_service=MagicMock(),
        agent_orchestrator=MagicMock(),
        chat_orchestrator=MagicMock(),
        rate_limiter=MagicMock(),
    )


@pytest.mark.integration
async def test_stuck_model_repeated_text_aborts_with_diagnostics(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_path = tmp_path / "context.log"
    settings = _settings(log_path=log_path, env_overrides={"AGENT_MAX_STEPS": "8"})

    repeated = json.dumps({"tool": "calculator", "args": {"expression": "1+1"}})
    gateway = FakeOllamaGateway(script=[LLMReply(llm_raw=repeated, bot_reply=repeated)] * 20)
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, settings=settings))

    result = await run_agent("infinite repeated text")

    assert result.stopped_reason == "repeat_detected"
    records = _parse_context_log(log_path)
    assert any(r.get("event") == "repeat_detected" for r in records)
    assert any(r.get("event") == "run_completed" and r.get("stopped_reason") == "repeat_detected" for r in records)


@pytest.mark.integration
async def test_stuck_model_malformed_json_spam_aborts_with_diagnostics(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    log_path = tmp_path / "context.log"
    settings = _settings(log_path=log_path, env_overrides={"AGENT_MAX_PARSE_RETRIES": "2"})

    bad = LLMReply(llm_raw="not json at all", bot_reply="not json at all")
    gateway = FakeOllamaGateway(script=[bad, bad, bad])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, settings=settings))

    result = await run_agent("malformed json spam")

    assert result.stopped_reason == "parser_retry_exhausted"
    records = _parse_context_log(log_path)
    assert any(r.get("event") == "parse_error_retrying" for r in records)
    assert any(r.get("event") == "parse_error_terminal" for r in records)
    assert any(r.get("event") == "run_completed" and r.get("stopped_reason") == "parser_retry_exhausted" for r in records)


class _FakeStreamResponse:
    def __init__(self, lines: list[object]):
        self._lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _tb):
        return False

    def raise_for_status(self) -> None:
        return None

    def aiter_lines(self):
        async def _gen():
            for item in self._lines:
                if isinstance(item, asyncio.Future):
                    await item
                    continue
                yield str(item)

        return _gen()


class _FakeAsyncClient:
    def __init__(self, *, timeout: float):
        self._timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _tb):
        return False

    def stream(self, _method: str, _url: str, *, json: object):
        return self._stream_response


@pytest.mark.integration
async def test_stuck_model_non_terminating_stream_aborts_and_logs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_path = tmp_path / "context.log"
    settings = _settings(
        log_path=log_path,
        env_overrides={"AGENT_LLM_STREAM_TIMEOUT": "1", "AGENT_MAX_REPEAT_STREAM_CHUNKS": "10"},
    )
    configure_context_logging(settings)
    gateway = OllamaGateway(settings=settings)

    stalled = asyncio.get_running_loop().create_future()
    client = _FakeAsyncClient(timeout=1.0)
    client._stream_response = _FakeStreamResponse([stalled])
    monkeypatch.setattr("src.ollama_gateway.httpx.AsyncClient", lambda timeout: client)

    with pytest.raises(OllamaTransportError):
        await gateway.generate_streamed_text(
            "prompt",
            model="test-model",
            run_id="run123",
            step_index=1,
        )

    records = _parse_context_log(log_path)
    assert any(r.get("event") == "ollama_stream_stalled" for r in records)
