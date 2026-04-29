# DV-02 - Add unit tests for safety protections

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Lock down the new guardrails with focused tests so regressions are caught before a stuck model can reach production behavior again.

## Context
The prompt explicitly requires unit coverage for repeated-output detection, infinite tool-loop detection, malformed JSON handling, stream timeout, repeated chunk detection, and forced finalization. These protections span parser, core loop, and streaming boundaries.

## Requirements
- Add deterministic unit tests for each new safety mechanism.
- Keep the tests offline and fully scripted without real LLM or network dependencies.
- Verify both the stop reason and any important diagnostics emitted by the runtime.

## Implementation Notes
- Reuse or extend existing pytest scaffolding under `tests/`.
- Prefer small focused tests near `src/agent/core.py`, `src/agent/parser.py`, and streaming helpers.
- Cover both successful recovery and terminal failure paths where the logic branches.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Repeated-output detection is unit tested
- [ ] Tool-loop, parser-hardening, and watchdog logic are unit tested
- [ ] Final-answer enforcement is unit tested
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `tests/`
- `src/agent/core.py`
- `src/agent/parser.py`

## Risks / Dependencies
- Dependency: guardrail and parser behavior must be explicit enough to test deterministically.
- Risk: over-mocking the runtime could hide integration issues if test seams are too artificial.

## Validation Steps
1. Run the new unit tests and confirm each failure mode produces the expected stop reason.
2. Check that repeated-chunk and timeout tests do not rely on flaky real-time waits.
3. Confirm the suite remains offline and deterministic.

## Follow-ups (optional)
- Split the tests into focused files if coverage grows beyond one logical module per file.
