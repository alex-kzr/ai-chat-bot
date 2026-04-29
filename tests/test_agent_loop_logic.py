"""BLC-04 — Agent loop end-to-end tests."""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from src.agent.core import run_agent
from src.config import load_settings
from src.contracts import LLMReply
from src.runtime import AppRuntime
from tests._fakes import FakeOllamaGateway


def _agent_settings(max_steps: int = 5, *, env_overrides: dict[str, str] | None = None):
    # AGENT_MAX_STEPS minimum in config is 5; use that as our deterministic cap.
    env = {
        "BOT_TOKEN": "test-token",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "test-model",
        "AGENT_MAX_STEPS": str(max_steps),
        "AGENT_MAX_REPEAT_STATE_SIGNATURES": "3",
        "CONTEXT_LOGGING_ENABLED": "false",
    }
    if env_overrides:
        env |= env_overrides
    return load_settings(env=env, load_dotenv_file=False)


def _make_runtime(
    gateway: FakeOllamaGateway,
    max_steps: int = 5,
    *,
    env_overrides: dict[str, str] | None = None,
) -> AppRuntime:
    return AppRuntime(
        settings=_agent_settings(max_steps=max_steps, env_overrides=env_overrides),
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


def _tool_call(tool: str, *, retry_reason: str | None = None, **args) -> LLMReply:
    payload: dict[str, object] = {"tool": tool, "args": args}
    if retry_reason is not None:
        payload["retry_reason"] = retry_reason
    js = json.dumps(payload)
    return LLMReply(llm_raw=js, bot_reply=js)


def _raw_reply(raw: str) -> LLMReply:
    return LLMReply(llm_raw=raw, bot_reply=raw)


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
    script = [_tool_call("calculator", expression=f"{i}+1") for i in range(1, 7)]
    gateway = FakeOllamaGateway(script=script)
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

    assert result.stopped_reason == "parser_retry_exhausted"
    assert result.final_answer is None


@pytest.mark.integration
async def test_agent_parses_noisy_fenced_json(monkeypatch) -> None:
    noisy = _raw_reply(
        """
Sure! Here's what I'll do next:

```json
{"final_answer":"ok"}
```

Done.
""".strip()
    )
    gateway = FakeOllamaGateway(script=[noisy])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway))

    result = await run_agent("return ok")

    assert result.stopped_reason == "final"
    assert result.final_answer == "ok"


@pytest.mark.integration
async def test_empty_final_answer_is_repaired_with_bounded_retry(monkeypatch) -> None:
    gateway = FakeOllamaGateway(script=[_final_answer(""), _final_answer("ok")])
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway))

    result = await run_agent("return ok")

    assert result.stopped_reason == "final"
    assert result.final_answer == "ok"
    assert len(gateway.calls) == 2


@pytest.mark.integration
async def test_too_long_final_answer_is_repaired_with_bounded_retry(monkeypatch) -> None:
    too_long = "x" * 501
    gateway = FakeOllamaGateway(script=[_final_answer(too_long), _final_answer("short")])
    monkeypatch.setattr(
        "src.runtime._runtime",
        _make_runtime(gateway, env_overrides={"AGENT_MAX_FINAL_ANSWER_CHARS": "500"}),
    )

    result = await run_agent("return short")

    assert result.stopped_reason == "final"
    assert result.final_answer == "short"
    assert len(gateway.calls) == 2


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


@pytest.mark.unit
async def test_repeated_model_output_stops_early(monkeypatch) -> None:
    tool_call_reply = _tool_call("calculator", expression="1+1")
    gateway = FakeOllamaGateway(script=[tool_call_reply] * 10)
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, max_steps=8))

    result = await run_agent("repeat forever")

    assert result.stopped_reason == "repeat_detected"
    assert result.final_answer is None
    assert len(gateway.calls) == 2


@pytest.mark.unit
async def test_cyclic_tool_signatures_stop(monkeypatch) -> None:
    replies = [
        _tool_call("calculator", expression="1+1"),
        _tool_call("calculator", expression="2+2"),
    ]
    gateway = FakeOllamaGateway(script=replies * 10)
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, max_steps=10))

    result = await run_agent("cycle forever")

    assert result.stopped_reason == "repeat_detected"
    assert result.final_answer is None
    assert len(gateway.calls) >= 6


@pytest.mark.unit
async def test_identical_tool_call_without_retry_reason_stops(monkeypatch) -> None:
    gateway = FakeOllamaGateway(
        script=[
            _tool_call("calculator", expression="1+1"),
            _tool_call("calculator", expression="1+1"),
        ]
    )
    monkeypatch.setattr(
        "src.runtime._runtime",
        _make_runtime(gateway, max_steps=8, env_overrides={"AGENT_MAX_REPEAT_FINAL_ANSWER": "10"}),
    )

    result = await run_agent("retry forever")

    assert result.stopped_reason == "tool_loop"
    assert result.final_answer is None
    assert len(gateway.calls) == 2


@pytest.mark.unit
async def test_identical_tool_call_with_retry_reason_is_bounded(monkeypatch) -> None:
    gateway = FakeOllamaGateway(
        script=[
            _tool_call("calculator", expression="1+1", retry_reason="transient"),
            _tool_call("calculator", expression="1+1", retry_reason="transient"),
            _tool_call("calculator", expression="1+1", retry_reason="transient"),
            _tool_call("calculator", expression="1+1", retry_reason="transient"),
        ]
    )
    monkeypatch.setattr(
        "src.runtime._runtime",
        _make_runtime(gateway, max_steps=10, env_overrides={"AGENT_MAX_REPEAT_FINAL_ANSWER": "10"}),
    )

    result = await run_agent("retry with reason")

    assert result.stopped_reason == "tool_loop"
    assert result.final_answer is None
    assert len(gateway.calls) == 4


@pytest.mark.unit
async def test_changed_tool_args_do_not_trigger_tool_loop(monkeypatch) -> None:
    gateway = FakeOllamaGateway(
        script=[
            _tool_call("calculator", expression="1+1"),
            _tool_call("calculator", expression="2+2"),
            _final_answer("done"),
        ]
    )
    monkeypatch.setattr("src.runtime._runtime", _make_runtime(gateway, max_steps=8))

    result = await run_agent("allow changed args")

    assert result.stopped_reason == "final"
    assert result.final_answer == "done"
