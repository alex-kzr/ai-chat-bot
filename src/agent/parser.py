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
    retry_reason: str | None = None


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

    step, parse_failures = _parse_from_candidates(raw)
    if step is not None:
        return step

    # Provide a deterministic failure reason; avoid "silent" fallthrough.
    if parse_failures:
        return ParseError(reason=parse_failures[0], raw=raw)
    return ParseError(reason="Could not extract JSON from output", raw=raw)


def parse_agent_output_or_raise(raw: str) -> ActionStep | FinalStep:
    parsed = parse_agent_output(raw)
    if isinstance(parsed, ParseError):
        raise AgentParseContractError(parsed.reason)
    return parsed


def _parse_from_candidates(raw: str) -> tuple[ActionStep | FinalStep | ParseError | None, list[str]]:
    """Try to parse a contract-compliant step from a messy model output.

    Returns:
        (step or None, failures)
    """
    failures: list[str] = []

    # 1) Fenced blocks (```json ...``` or ``` ... ```)
    fenced_blocks = _extract_fenced_blocks(raw)
    for json_str in _prioritize_fenced_blocks(fenced_blocks):
        step = _parse_json_object_to_step(json_str, failures)
        if step is not None:
            return step, failures

    # 2) Inline balanced objects; try all and pick the first that validates the schema.
    for json_str in _iter_balanced_json_objects(raw):
        step = _parse_json_object_to_step(json_str, failures)
        if step is not None:
            return step, failures

    # 3) If the raw itself is JSON (e.g., no braces noise), try it last.
    step = _parse_json_object_to_step(raw, failures)
    if step is not None:
        return step, failures

    return None, failures


def _extract_fenced_blocks(text: str) -> list[tuple[str | None, str]]:
    """Return all triple-backtick fenced blocks as (lang, body)."""
    # Match ```lang?\n<body>\n``` (lang may be absent).
    blocks: list[tuple[str | None, str]] = []
    for match in re.finditer(r"```[ \t]*([A-Za-z0-9_-]+)?[ \t]*\r?\n(.*?)\r?\n```", text, re.DOTALL):
        lang = match.group(1).lower().strip() if match.group(1) else None
        body = match.group(2).strip()
        blocks.append((lang, body))
    return blocks


def _prioritize_fenced_blocks(blocks: list[tuple[str | None, str]]) -> list[str]:
    """Prefer ```json``` blocks, then other fenced blocks."""
    json_first = [body for lang, body in blocks if lang == "json"]
    other = [body for lang, body in blocks if lang != "json"]
    return [*json_first, *other]


def _iter_balanced_json_objects(text: str) -> list[str]:
    """Extract all balanced JSON objects from text (best-effort)."""
    candidates: list[str] = []
    for start_idx in _iter_char_indexes(text, "{"):
        candidate = _extract_balanced_from(text, start_idx)
        if candidate is not None:
            candidates.append(candidate)
    return candidates


def _iter_char_indexes(text: str, char: str) -> list[int]:
    indexes: list[int] = []
    i = text.find(char)
    while i != -1:
        indexes.append(i)
        i = text.find(char, i + 1)
    return indexes


def _extract_balanced_from(text: str, start_idx: int) -> str | None:
    """Extract a single balanced {...} object from a specific start position."""
    brace_depth = 0
    in_string = False
    escape_next = False

    for i in range(start_idx, len(text)):
        c = text[i]

        if escape_next:
            escape_next = False
            continue

        if c == "\\":
            escape_next = True
            continue

        if c == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if c == "{":
            brace_depth += 1
        elif c == "}":
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


def _parse_json_object_to_step(
    json_str: str,
    failures: list[str],
) -> ActionStep | FinalStep | ParseError | None:
    parsed = _validate_json(json_str)
    if parsed is None:
        failures.append("Extracted JSON candidate but it was not valid JSON")
        return None
    if not isinstance(parsed, dict):
        failures.append(f"Top-level JSON must be an object, got {type(parsed).__name__}")
        return None
    step = _build_step(parsed, json_str)
    if isinstance(step, ParseError):
        failures.append(step.reason)
        return None
    return step


def _build_step(data: dict, raw_json: str) -> ActionStep | FinalStep | ParseError:
    """Build ActionStep, FinalStep, or ParseError from parsed data.

    Args:
        data: Parsed JSON dict.
        raw_json: Original JSON string for error messages.

    Returns:
        Appropriate step type.
    """
    has_final = "final_answer" in data
    has_tool = "tool" in data

    if has_final and has_tool:
        return ParseError(
            reason="Payload must include exactly one of 'final_answer' or 'tool'",
            raw=raw_json,
        )

    if has_final:
        allowed_keys = {"final_answer"}
        unexpected = sorted(set(data.keys()) - allowed_keys)
        if unexpected:
            return ParseError(
                reason=f"Unexpected keys for final answer payload: {unexpected}",
                raw=raw_json,
            )
        final_answer = data["final_answer"]
        if not isinstance(final_answer, str):
            return ParseError(
                reason=f"Invalid type for 'final_answer': expected string, got {type(final_answer).__name__}",
                raw=raw_json,
            )
        return FinalStep(final_answer=final_answer)

    if has_tool:
        allowed_keys = {"tool", "args", "retry_reason"}
        unexpected = sorted(set(data.keys()) - allowed_keys)
        if unexpected:
            return ParseError(
                reason=f"Unexpected keys for tool payload: {unexpected}",
                raw=raw_json,
            )

        tool = data.get("tool")
        args = data.get("args", {})
        retry_reason = data.get("retry_reason")

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
        if retry_reason is not None and not isinstance(retry_reason, str):
            return ParseError(
                reason=f"Invalid type for 'retry_reason': expected string, got {type(retry_reason).__name__}",
                raw=raw_json,
            )
        clean_reason = retry_reason.strip() if isinstance(retry_reason, str) else None
        return ActionStep(action=tool.strip(), args=args, retry_reason=clean_reason or None)

    # Neither final_answer nor tool found
    logger.warning(f"Could not identify step type in: {raw_json}")
    return ParseError(
        reason="No final_answer or tool key found",
        raw=raw_json,
    )
