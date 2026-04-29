# BLC-04 - Cover agent loop end-to-end

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Treat `agent.core.run_agent` as the unit under test and drive it through the full loop with a scripted gateway: tool dispatch → observation feedback → final answer, plus the `max_steps` cutoff. This protects the agent contract regardless of model behavior.

## Context
- `src/agent/core.py` contains the iterative loop.
- `src/agent/parser.py` parses strict JSON.
- `src/agent/tools.py` exposes `calculator` and `http_request`.
- Existing tests (`test_agent_parser_contract.py`, `test_agent_tools_contract.py`) cover parts; this task covers the loop integration with mocked tools and gateway.

## Requirements
Add `tests/test_agent_loop_logic.py`:
- Happy-path single-step: scripted reply is `{"final_answer": "X"}` — `AgentResult.final_answer == "X"`, `stopped_reason == "final"`, `steps == []`.
- Happy-path multi-step: scripted replies = `[tool_call(calculator, ...), final_answer("42")]` — calculator is invoked once, observation fed back, final answer surfaces.
- `max_steps` reached: scripted replies always emit a tool call — loop stops at the configured cap with `stopped_reason == "max_steps"`.
- Parse failure: scripted reply is malformed JSON — loop logs and either retries (if implemented) or stops with `stopped_reason == "error"` per current contract.
- Tool error: tool raises a controlled exception — observation is the structured `[tool_error]` envelope; loop continues.

## Implementation Notes
- Use `FakeOllamaGateway` with a multi-entry script.
- Mock `calculator.run` (or substitute the registry entry) to keep tool execution deterministic.
- Set `agent_max_steps = 3` in `fake_settings` to keep the cutoff test fast.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] All five scenarios covered.
- [x] No real LLM call; no real HTTP call.
- [x] Tests run in <2s total.

## Affected Files / Components
- `tests/test_agent_loop_logic.py` (new)
- `src/agent/core.py` (read-only)

## Risks / Dependencies
- Depends on TF-02 (`FakeOllamaGateway`).
- Depends on TSH-02 already shipped (tool argument validation) — observed `[tool_error]` envelope is the current contract.

## Validation Steps
1. `pytest -q tests/test_agent_loop_logic.py` — passes.
2. Lower `max_steps` to 1 and confirm cutoff trips deterministically.
3. Full suite green.

## Follow-ups (optional)
- Extend with a property-based test once the JSON contract has a formal schema.
