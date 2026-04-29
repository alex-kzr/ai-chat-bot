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
    assert parsed.retry_reason is None


def test_parse_tool_call_with_retry_reason() -> None:
    parsed = parse_agent_output('{"tool":"calculator","args":{"expression":"2+2"},"retry_reason":"transient"}')
    assert isinstance(parsed, ActionStep)
    assert parsed.action == "calculator"
    assert parsed.retry_reason == "transient"


def test_parse_invalid_payload_returns_parse_error() -> None:
    parsed = parse_agent_output("not json")
    assert isinstance(parsed, ParseError)


def test_parse_fenced_json_with_noise() -> None:
    parsed = parse_agent_output(
        """
Sure! Here's the response:

```json
{"final_answer":"ok"}
```

Thanks.
""".strip()
    )
    assert isinstance(parsed, FinalStep)
    assert parsed.final_answer == "ok"


def test_parse_fenced_non_json_still_works() -> None:
    parsed = parse_agent_output(
        """
```text
{"tool":"calculator","args":{"expression":"2+2"}}
```
""".strip()
    )
    assert isinstance(parsed, ActionStep)
    assert parsed.action == "calculator"


def test_parse_picks_schema_valid_json_when_multiple_objects_present() -> None:
    parsed = parse_agent_output(
        """
Some unrelated data: {"foo":"bar"}
Now the real payload: {"tool":"calculator","args":{"expression":"2+2"}}
""".strip()
    )
    assert isinstance(parsed, ActionStep)
    assert parsed.action == "calculator"


def test_parse_rejects_final_answer_with_unexpected_keys() -> None:
    parsed = parse_agent_output('{"final_answer":"ok","tool":"calculator","args":{}}')
    assert isinstance(parsed, ParseError)
