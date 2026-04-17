# AL-05 - Robust JSON Parsing & Error Handling

## Status

* [ ] To Do
* [ ] In Progress
* [x] Done

## Purpose

Isolate all the fragility of parsing LLM JSON responses into a single testable module. The loop core should receive a typed result instead of dealing with raw text.

## Context

Local models (qwen3:4b, qwen3:0.6b) often wrap JSON in markdown blocks or add surrounding text. AL-04 relies on a stable parser for both supported formats:

* `{"thought": "...", "action": "tool_name", "args": {...}}` — tool invocation
* `{"final_answer": "..."}` — completion

## Requirements

* Create `src/agent/parser.py` with `parse_agent_output(raw: str) -> ParsedStep`.
* `ParsedStep` — tagged union: `ActionStep | FinalStep | ParseError`.

  * `ActionStep(thought: str, action: str, args: dict)`.
  * `FinalStep(final_answer: str)`.
  * `ParseError(reason: str, raw: str)`.
* JSON extraction order:

  1. First ` ```json ... ``` ` fenced block.
  2. First balanced `{...}` block (walk with string awareness, respecting escape sequences).
  3. Fallback → `ParseError`.
* Shape validation:

  * If key `final_answer` is present → `FinalStep`. `final_answer` must be a string.
  * If key `action` is present → `ActionStep`. `thought` — string (default `""`), `action` — string, `args` — dict (default `{}`).
  * Unknown keys are allowed, log at DEBUG level.
  * Neither `final_answer` nor `action` → `ParseError`.
* Never throw exceptions — always return one of the three variants.
* Synchronous function, no side effects.

## Implementation Notes

* For fenced block: `re.search(r"```\s*json\s*\n?(.*?)\n?```", text, re.DOTALL)`.
* For balanced JSON: walk using `brace_depth`, `in_string`, `escape_next` — do not use `json5` or third-party libraries.
* Loop integration (AL-04): on `ParseError` → retry once with message:
  `"Your previous output was not valid JSON. Respond with exactly one JSON object only."`
  On second `ParseError` → `stopped_reason="error"`.
* Log `ParseError.reason` at WARNING, `ParseError.raw[:200]` at DEBUG.

## Definition of Done

* [x] `parse_agent_output` handles: fenced JSON, raw JSON, JSON with surrounding text
* [x] `FinalStep` is correctly recognized by `final_answer` key
* [x] `ActionStep` is correctly recognized by `action` key
* [x] Invalid JSON → `ParseError` (never exception)
* [x] Loop in AL-04 uses this parser exclusively
* [x] Smoke test: all three input formats + malformed

## Affected Files / Components

* `src/agent/parser.py`
* `src/agent/core.py` (integration)

## Risks / Dependencies

* Depends on AL-04.
* Models may embed JSON inside strings — brace walker must handle string literals.
* `FinalStep` must take precedence over `ActionStep` if both keys are present.

## Validation Steps

1. `parse_agent_output('```json\n{"final_answer":"ok"}\n```')` → `FinalStep("ok")`.
2. `parse_agent_output('prefix {"thought":"t","action":"calculator","args":{"expression":"1+1"}} suffix')` → `ActionStep(thought="t", action="calculator", args={"expression":"1+1"})`.
3. `parse_agent_output('{"final_answer": "done", "action": "calc"}')` → `FinalStep("done")` (final_answer has priority).
4. `parse_agent_output('not json at all')` → `ParseError(reason=..., raw=...)`.
5. `parse_agent_output('{"action": "calc", "thought": "hi", "args": {"expression": "2+2"}}')` → `ActionStep`.
