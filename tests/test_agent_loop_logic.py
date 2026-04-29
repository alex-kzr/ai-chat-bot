"""BLC-04 — Agent loop end-to-end tests."""
from __future__ import annotations

import json
import pytest
from unittest.mock import MagicMock

from src.agent.core import run_agent
from src.config import load_settings
from src.contracts import LLMReply
from src.runtime import AppRuntime

from tests._fakes import FakeOllamaGateway


def _agent_settings(max_steps: int = 5):
    # AGENT_MAX_STEPS minimum in config is 5; use that as our deterministic cap.
    return load_settings(
        env={
            "BOT_TOKEN": "test-token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "test-model",
            "AGENT_MAX_STEPS": str(max_steps),
            "CONTEXT_LOGGING_ENABLED": "false",
        },
        load_dotenv_file=False,
    )


def _make_runtime(gateway: FakeOllamaGateway, max_steps: int = 5) -> AppRuntime:
    return AppRuntime(
        settings=_agent_settings(max_steps=max_steps),
        users=MagicMock(),
        event_bus=MagicMock(),
        ollama=gateway,
        conversation=MagicMock(),
        chat_service=MagicMock(),
        agent_orchestrator=MagicMock(),
        chat_orchestrator=MagicMock(),
        rate_limiter=MagicMock(),
    )


def _final_answer(text: str) -> LLMReply:
    js = json.dumps({"final_answer": text})
    return LLMReply(llm_raw=js, bot_reply=js)


def _tool_call(tool: str, **args) -> LLMReply:
    js = json.dumps({"tool": tool, "args": args})
    return LLMReply(llm_raw=js, bot_reply=js)


@pytest.mark.unit
async def test_single_step_final_answer(monkeypatch) -> None:
    gateway = FakeOllamaGateway(script=[_final_answer("X")])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway))

    result = await run_agent("what is X?")

    assert result.final_answer == "X"
    assert result.stopped_reason == "final"
    assert len(gateway.calls) == 1


@pytest.mark.unit
async def test_multi_step_tool_call_then_final_answer(monkeypatch) -> None:
    gateway = FakeOllamaGateway(script=[
        _tool_call("calculator", expression="6*7"),
        _final_answer("42"),
    ])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway))

    result = await run_agent("what is 6*7?")

    assert result.final_answer == "42"
    assert result.stopped_reason == "final"
    assert len(gateway.calls) == 2
    tool_steps = [s for s in result.steps if s.action == "calculator"]
    assert len(tool_steps) == 1


@pytest.mark.unit
async def test_max_steps_cutoff(monkeypatch) -> None:
    # Always return a tool call — loop must stop at max_steps=5
    tool_call_reply = _tool_call("calculator", expression="1+1")
    gateway = FakeOllamaGateway(script=[tool_call_reply] * 6)
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, max_steps=5))

    result = await run_agent("loop forever")

    assert result.stopped_reason == "max_steps"
    assert result.final_answer is None


@pytest.mark.unit
async def test_parse_failure_stops_with_error(monkeypatch) -> None:
    # Both the initial call and its retry return unparseable text → error
    bad = LLMReply(llm_raw="not json at all", bot_reply="not json at all")
    gateway = FakeOllamaGateway(script=[bad, bad])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway))

    result = await run_agent("parse error task")

    assert result.stopped_reason == "error"
    assert result.final_answer is None


@pytest.mark.unit
async def test_tool_error_produces_observation_and_loop_continues(monkeypatch) -> None:
    # calculator with empty expression → "[tool_error] Missing expression argument"
    # second step returns final answer → loop completes normally
    gateway = FakeOllamaGateway(script=[
        _tool_call("calculator", expression=""),
        _final_answer("recovered"),
    ])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway))

    result = await run_agent("trigger tool error then recover")

    assert result.stopped_reason == "final"
    assert result.final_answer == "recovered"
    tool_steps = [s for s in result.steps if s.action == "calculator"]
    assert len(tool_steps) == 1
    assert tool_steps[0].observation is not None
    assert "[tool_error]" in tool_steps[0].observation
