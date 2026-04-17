import json
import logging
import re
from dataclasses import dataclass
from typing import Any, TypedDict, Union

from src.errors import AgentParseContractError

logger = logging.getLogger(__name__)


@dataclass
class ActionStep:
    """Agent requested a tool call."""

    action: str
    args: dict


@dataclass
class FinalStep:
    """Agent reached a final answer."""

    final_answer: str


@dataclass
class ParseError:
    """Failed to parse agent output."""

    reason: str
    raw: str


ParsedStep = Union[ActionStep, FinalStep, ParseError]


class AgentToolPayload(TypedDict):
    tool: str
    args: dict[str, Any]


def parse_agent_output(raw: str) -> ParsedStep:
    """Parse agent output into a structured step.

    Tries to extract JSON in this order:
    1. ```json ... ``` fenced block
    2. First balanced {...} in text
    3. Raw text (falls back to ParseError)

    Args:
        raw: Raw LLM response.

    Returns:
        ActionStep, FinalStep, or ParseError.
    """
    raw = raw.strip()

    # Try to extract fenced JSON block
    fenced_json = _extract_fenced_json(raw)
    if fenced_json:
        parsed = _validate_json(fenced_json)
        if parsed is not None:
            if not isinstance(parsed, dict):
                return ParseError(
                    reason=f"Top-level JSON must be an object, got {type(parsed).__name__}",
                    raw=fenced_json,
                )
            return _build_step(parsed, fenced_json)

    # Try to extract balanced JSON block
    balanced_json = _extract_balanced_json(raw)
    if balanced_json:
        parsed = _validate_json(balanced_json)
        if parsed is not None:
            if not isinstance(parsed, dict):
                return ParseError(
                    reason=f"Top-level JSON must be an object, got {type(parsed).__name__}",
                    raw=balanced_json,
                )
            return _build_step(parsed, balanced_json)

    # Fallback: parse error
    return ParseError(
        reason="Could not extract valid JSON from output",
        raw=raw,
    )


def parse_agent_output_or_raise(raw: str) -> ActionStep | FinalStep:
    parsed = parse_agent_output(raw)
    if isinstance(parsed, ParseError):
        raise AgentParseContractError(parsed.reason)
    return parsed


def _extract_fenced_json(text: str) -> str | None:
    """Extract JSON from ```json ... ``` fenced block."""
    # Match ```json ... ``` (with or without newlines)
    pattern = r"```\s*json\s*\n?(.*?)\n?```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _extract_balanced_json(text: str) -> str | None:
    """Extract first balanced JSON object from text."""
    start_idx = text.find("{")
    if start_idx == -1:
        return None

    # Walk from { to matching }, respecting strings
    brace_depth = 0
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        char = text[i]

        if escape_next:
            escape_next = False
            continue

        if char == "\\":
            escape_next = True
            continue

        if char == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if char == "{":
            brace_depth += 1
        elif char == "}":
            brace_depth -= 1
            if brace_depth == 0:
                return text[start_idx : i + 1]

    return None


def _validate_json(json_str: str) -> object | None:
    """Try to parse a JSON string.

    Args:
        json_str: JSON string.

    Returns:
        Parsed dict or None if invalid.
    """
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return None


def _build_step(data: dict, raw_json: str) -> Union[ActionStep, FinalStep, ParseError]:
    """Build ActionStep, FinalStep, or ParseError from parsed data.

    Args:
        data: Parsed JSON dict.
        raw_json: Original JSON string for error messages.

    Returns:
        Appropriate step type.
    """
    # Check for final_answer
    if "final_answer" in data:
        final_answer = data["final_answer"]
        if isinstance(final_answer, str):
            return FinalStep(final_answer=final_answer)
        return ParseError(
            reason=f"Invalid type for 'final_answer': expected string, got {type(final_answer).__name__}",
            raw=raw_json,
        )

    # Check for tool step
    if "tool" in data:
        tool = data.get("tool")
        args = data.get("args", {})

        if not isinstance(tool, str):
            return ParseError(
                reason=f"Invalid type for 'tool': expected string, got {type(tool).__name__}",
                raw=raw_json,
            )
        if not tool.strip():
            return ParseError(
                reason="Invalid value for 'tool': must be a non-empty string",
                raw=raw_json,
            )
        if not isinstance(args, dict):
            return ParseError(
                reason=f"Invalid type for 'args': expected object, got {type(args).__name__}",
                raw=raw_json,
            )
        return ActionStep(action=tool.strip(), args=args)

    # Neither final_answer nor tool found
    logger.warning(f"Could not identify step type in: {raw_json}")
    return ParseError(
        reason="No final_answer or tool key found",
        raw=raw_json,
    )
