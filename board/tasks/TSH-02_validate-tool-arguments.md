# TSH-02 - Validate tool-call arguments with explicit schemas

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Stop arbitrary or malformed JSON from reaching tool implementations. Today the agent loop passes `parsed.args` (any dict shape the LLM produced) directly to `TOOLS[name].run(args)`, relying on each tool to defend itself. A consistent, centralized validation layer reduces tool-side error-handling complexity and prevents type-confusion bugs (e.g. a list passed where a string is expected).

## Context
- Agent loop: `src/agent/core.py` — see the `if normalized_action in TOOLS:` branch.
- Tool registry and per-tool `args_schema`: `src/agent/tools.py` (`ToolSpec`).
- Parser already enforces top-level shape (`tool`/`args` or `final_answer`) in `src/agent/parser.py`.

## Requirements
- Before invoking `run()`, validate `args` against the tool's `args_schema`:
  - Required keys must be present (or have a documented default).
  - Each value's Python type must match the declared schema type (`string`, `integer`, `number`, `boolean`).
  - Reject unknown keys.
- On validation failure, emit a deterministic `[tool_error] invalid_args: <field>: <reason>` observation and feed it back into the loop so the LLM can retry — do not raise.
- Keep the validator dependency-free (no Pydantic) to avoid a heavy dep; a tiny in-house validator is sufficient given the small schema vocabulary.

## Implementation Notes
- Add a `validate_tool_args(spec: ToolSpec, args: dict) -> tuple[bool, str]` helper in `src/agent/tools.py` (or a new `src/agent/validation.py`).
- Update each existing schema to include a `required: bool` flag where appropriate (default `True` for primary args, `False` for optional like `method`).
- Run validation in `core.py` immediately before `await TOOLS[normalized_action].run(parsed.args)`.

## Testing
- [x] Unit tests
- [x] Integration tests
- [x] Manual testing

## Definition of Done
- [x] All tool calls go through the centralized validator before `run()`.
- [x] Invalid `args` produce a `[tool_error] invalid_args:` observation.
- [x] Unknown keys are rejected.
- [x] Existing happy-path tool tests still pass.
- [x] New tests cover at least: missing required arg, wrong type, unknown key.

## Affected Files / Components
- `src/agent/tools.py`
- `src/agent/core.py`
- `tests/test_agent_tools_contract.py` (new cases)

## Risks / Dependencies
- The current schemas describe types informally — be conservative when interpreting them so existing prompts keep working.
- Avoid adding Pydantic; keep the schema language and validator small.

## Validation Steps
1. Send `{"tool": "calculator", "args": {"expr": "2+2"}}` (wrong key) — expect `[tool_error] invalid_args: unknown key 'expr'` (or similar) instead of an internal exception.
2. Send `{"tool": "http_request", "args": {"url": 42}}` — expect a type-mismatch error observation.
3. Send `{"tool": "calculator", "args": {"expression": "2+2"}}` — must continue to work.

## Follow-ups (optional)
- Introduce per-tool argument max-length caps in the same validator (helps DoS protection).
