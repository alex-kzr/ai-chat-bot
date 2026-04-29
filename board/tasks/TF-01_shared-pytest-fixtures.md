# TF-01 - Shared pytest fixtures for runtime and settings

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide a single source of truth for building a fake `Runtime` so handler/service tests can ask for one instead of constructing settings, event bus, users, rate limiter, and orchestrators from scratch in every file.

## Context
- Existing scaffolding lives in `conftest.py` (root) and per-file fixtures.
- `src/runtime.py` exposes a module-level `_runtime` accessed via `get_runtime()`.
- `src/config.py` defines `Settings` with nested security/agent/etc. settings.
- Existing tests construct fixtures inline (e.g. `tests/test_chat_flow_events.py`, `tests/test_runtime_event_wiring.py`).

## Requirements
- Add the following fixtures (in `tests/conftest.py` or a new `tests/_fakes.py` imported by `conftest.py`):
  - `fake_settings` — a `Settings` instance with deterministic values (small `MAX_HISTORY_MESSAGES`, modest `max_user_input_chars`, generous rate limits).
  - `event_bus` — a fresh in-memory `EventBus`.
  - `user_service` — a fresh `UserService`.
  - `rate_limiter` — an `AsyncMock`-backed limiter that always allows by default but can be flipped to deny per-test.
  - `chat_orchestrator` and `agent_orchestrator` — `AsyncMock`s with realistic return shapes (`process_text` returns a `ProcessOutcome`-like object, `run_task` returns a string).
  - `fake_runtime` — composes the above into a `Runtime` (or a duck-typed stand-in if constructing the real one is heavy).
- Fixtures are function-scoped by default; mark `fake_settings` as session-scoped if construction is non-trivial.

## Implementation Notes
- Prefer real `EventBus` and `UserService` over mocks — they are lightweight and exercise real code.
- Mock at I/O boundaries (orchestrators, rate limiter, anything that would call Ollama or Telegram).
- Do not import aiogram in the fixtures module — keep it test-double friendly.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] `fake_runtime` fixture available to every test file.
- [x] Re-running existing tests still passes (no fixture name collisions).
- [x] No fixture leaks state between tests.
- [x] Fixtures are documented with one-line docstrings.

## Affected Files / Components
- `tests/conftest.py`
- (optional) `tests/_fakes.py`

## Risks / Dependencies
- Risk: collision with existing fixtures. Mitigation: namespace new fixtures (`fake_*`).

## Validation Steps
1. `pytest -q` — full suite passes.
2. Add a smoke test that requests `fake_runtime` and asserts its components are wired.
3. Existing tests must not need changes.

## Follow-ups (optional)
- Promote shared helpers to a `tests/conftest_helpers.py` if the file grows.
