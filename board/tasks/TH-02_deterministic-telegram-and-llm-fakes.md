# TH-02 - Strengthen deterministic fakes for Telegram and LLM integrations

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Ensure tests can model Telegram and LLM interactions deterministically without using real external services.

## Context
The prompt requires mocked Telegram API calls, mocked LLM calls, and no dependence on real servers or internet access. The test suite already includes fakes and handler coverage, but the shared fake layer should be reviewed and strengthened so CI remains stable as coverage grows.

## Requirements
- Review existing Telegram and LLM fakes/fixtures for completeness and determinism.
- Add or refine shared test helpers for failure cases and representative happy paths.
- Eliminate reliance on timing, network, or machine-specific behavior in affected tests.

## Implementation Notes
- Reuse and improve `tests/_fakes.py` and shared fixtures rather than duplicating one-off mocks.
- Prefer narrowly-scoped fakes that reflect public contracts, not private implementation details.
- Keep test helpers readable so future tasks can extend them safely.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Shared fakes cover the CI-critical Telegram and LLM scenarios
- [x] Affected tests run without real network access
- [x] Failure cases are deterministic and easy to reproduce
- [x] Test helpers stay aligned with production contracts

## Affected Files / Components
- `tests/_fakes.py`
- `tests/conftest.py`
- `tests/test_handlers_*.py`
- `tests/test_chat_service*.py`

## Risks / Dependencies
- Dependency: fake behavior must stay synchronized with the production service contracts.
- Risk: overly clever fakes can hide real integration issues instead of surfacing them.

## Validation Steps
1. Run the relevant unit and integration tests without internet access.
2. Confirm Telegram and LLM behavior is fully simulated by fakes or mocks.
3. Review the shared helpers to ensure future tests can reuse them cleanly.

## Notes / Improvements
- `tests/_fakes.py` `FakeOllamaGateway` now supports a configured `models` list and records `list_models()` calls, enabling deterministic bootstrap/model-selection tests without hitting a real Ollama server.
- Added a smoke test covering `list_models()` determinism (`tests/test_foundations_smoke.py`).

## Follow-ups (optional)
- Add builder-style helpers if test setup is still repetitive after the refactor.
