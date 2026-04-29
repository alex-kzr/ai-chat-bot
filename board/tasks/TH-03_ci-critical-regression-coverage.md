# TH-03 - Add CI-critical regression coverage for isolated execution

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Close any remaining automated test gaps that could let CI configuration or critical runtime behavior regress silently.

## Context
A CI pipeline is only valuable if it protects the right contracts. Given the current architecture, the highest-value coverage areas are startup/configuration behavior, message handling, chat orchestration, and controlled failure paths around Telegram and LLM boundaries.

## Requirements
- Identify the most important gaps for CI confidence.
- Add targeted tests for startup wiring, deterministic failure behavior, or other missing CI-critical paths.
- Keep the suite fast and isolated while improving confidence.

## Implementation Notes
- Prefer focused tests for contracts and edge cases over broad slow end-to-end scenarios.
- Use existing markers and shared fixtures consistently.
- If a new test category is needed, define it explicitly and document why.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] CI-critical regression gaps are identified and covered
- [x] New tests run deterministically in local and CI environments
- [x] Test additions improve confidence without making the pipeline unnecessarily slow
- [x] Coverage aligns with the architecture and failure modes described in the prompt

## Affected Files / Components
- `tests/test_runtime_event_wiring.py`
- `tests/test_handlers_*.py`
- `tests/test_llm_failures.py`
- `tests/test_chat_orchestrator_logic.py`

## Risks / Dependencies
- Dependency: this task builds on the fake/test-helper quality from TH-02.
- Risk: adding too many slow integration tests can undermine CI speed goals.

## Validation Steps
1. Review the final CI-critical test matrix.
2. Run the targeted tests and verify they do not hit external services.
3. Confirm the new coverage protects the intended failure modes and contracts.

## Notes / Coverage added
- Added unit coverage for startup model selection logic (`src.bootstrap.choose_model`) with injected prompt/output to keep tests fully isolated.
- Validated full test suite remains fast and deterministic (`python -m pytest -q`).

## Follow-ups (optional)
- Add coverage reporting thresholds later if the team decides to enforce them.
