from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.agent.core import run_agent
from src.config import load_settings
from src.context_logging import configure_context_logging
from src.contracts import LLMReply
from src.runtime import AppRuntime
from tests._fakes import FakeOllamaGateway


def _parse_context_log(path: Path) -> list[dict]:
    records: list[dict] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if " | " not in line:
            continue
        parts = line.split(" | ", 2)
        if len(parts) != 3:
            continue
        payload = parts[2].strip()
        try:
            records.append(json.loads(payload))
        except json.JSONDecodeError:
            continue
    return records


def _agent_settings(*, log_path: Path, env_overrides: dict[str, str] | None = None):
    env = {
        "BOT_TOKEN": "test-token",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "test-model",
        "AGENT_MAX_STEPS": "6",
        "AGENT_MAX_REPEAT_STATE_SIGNATURES": "3",
        "CONTEXT_LOGGING_ENABLED": "true",
        "LOG_DESTINATION": "file",
        "LOG_FILE_PATH": str(log_path),
        "LOG_FORMAT": "json",
    }
    if env_overrides:
        env |= env_overrides
    return load_settings(env=env, load_dotenv_file=False)


def _make_runtime(gateway: FakeOllamaGateway, *, settings) -> AppRuntime:
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


@pytest.mark.unit
async def test_loop_diagnostics_emits_run_completed_on_repeat(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_path = tmp_path / "context.log"
    settings = _agent_settings(log_path=log_path)

    repeated = json.dumps({"tool": "calculator", "args": {"expression": "1+1"}})
    gateway = FakeOllamaGateway(script=[LLMReply(llm_raw=repeated, bot_reply=repeated)] * 10)
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, settings=settings))

    result = await run_agent("repeat forever")

    assert result.stopped_reason == "repeat_detected"
    records = _parse_context_log(log_path)
    assert any(r.get("event") == "run_started" for r in records)
    completed = [r for r in records if r.get("event") == "run_completed"]
    assert completed
    assert completed[-1]["stopped_reason"] == "repeat_detected"


@pytest.mark.unit
async def test_loop_diagnostics_emits_tool_loop_event(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_path = tmp_path / "context.log"
    settings = _agent_settings(
        log_path=log_path,
        env_overrides={"AGENT_MAX_REPEAT_FINAL_ANSWER": "10"},
    )

    tool = json.dumps({"tool": "calculator", "args": {"expression": "1+1"}})
    gateway = FakeOllamaGateway(
        script=[
            LLMReply(llm_raw=tool, bot_reply=tool),
            LLMReply(llm_raw=tool, bot_reply=tool),
        ]
    )
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, settings=settings))

    result = await run_agent("retry forever")

    assert result.stopped_reason == "tool_loop"
    records = _parse_context_log(log_path)
    assert any(r.get("event") == "tool_loop_detected" for r in records)
    completed = [r for r in records if r.get("event") == "run_completed"]
    assert completed[-1]["stopped_reason"] == "tool_loop"


@pytest.mark.unit
async def test_loop_diagnostics_emits_parse_error_events(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    log_path = tmp_path / "context.log"
    settings = _agent_settings(log_path=log_path, env_overrides={"AGENT_MAX_PARSE_RETRIES": "2"})

    bad = LLMReply(llm_raw="not json", bot_reply="not json")
    gateway = FakeOllamaGateway(script=[bad, bad, bad])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, settings=settings))

    result = await run_agent("parse error task")

    assert result.stopped_reason == "parser_retry_exhausted"
    records = _parse_context_log(log_path)
    assert any(r.get("event") == "parse_error_retrying" for r in records)
    assert any(r.get("event") == "parse_error_terminal" for r in records)
    completed = [r for r in records if r.get("event") == "run_completed"]
    assert completed[-1]["stopped_reason"] == "parser_retry_exhausted"
