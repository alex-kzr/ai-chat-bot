# THC-01 - Test handle_start

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Pin down the `/start` contract: it sends the welcome message verbatim and never reaches the LLM, agent, or rate limiter. Cheap, but a baseline regression catcher.

## Context
- `src/handlers.py:handle_start` — replies with `WELCOME_MESSAGE`.
- aiogram dispatch is filter-based; testing the function directly bypasses the router and is the simplest unit-level approach.

## Requirements
Add `tests/test_handlers_start.py`:
- Calling `handle_start(message)` invokes `message.answer` exactly once with `WELCOME_MESSAGE`.
- No call to runtime orchestrators (`chat_orchestrator`, `agent_orchestrator`).
- No call to `runtime.rate_limiter.is_allowed` (since `/start` bypasses it).

## Implementation Notes
- Use `make_message` from TF-02.
- Use the `fake_runtime` fixture (TF-01) but assert no calls were made on its async mocks.
- AAA, one assertion per test where natural.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Handler replies with the exact welcome string.
- [x] No orchestrator interaction.
- [x] Test marked `@pytest.mark.handlers`.

## Affected Files / Components
- `tests/test_handlers_start.py` (new)
- `src/handlers.py` (read-only)

## Risks / Dependencies
- Depends on TF-01, TF-02, TTD-01.

## Validation Steps
1. `pytest -q tests/test_handlers_start.py` — passes.
2. Change `WELCOME_MESSAGE` — test fails.
3. Full suite green.

## Follow-ups (optional)
- Once internationalization lands, parametrize on locale.
