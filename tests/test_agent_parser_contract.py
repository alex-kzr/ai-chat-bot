from __future__ import annotations

from src.agent.parser import ActionStep, FinalStep, ParseError, parse_agent_output


def test_parse_final_answer() -> None:
    parsed = parse_agent_output('{"final_answer":"done"}')
    assert isinstance(parsed, FinalStep)
    assert parsed.final_answer == "done"


def test_parse_tool_call() -> None:
    parsed = parse_agent_output('{"tool":"calculator","args":{"expression":"2+2"}}')
    assert isinstance(parsed, ActionStep)
    assert parsed.action == "calculator"
    assert parsed.args["expression"] == "2+2"


def test_parse_invalid_payload_returns_parse_error() -> None:
    parsed = parse_agent_output("not json")
    assert isinstance(parsed, ParseError)
