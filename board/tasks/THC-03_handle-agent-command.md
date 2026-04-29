# THC-03 - Test handle_agent command parsing

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Lock in the `/agent` command surface: missing body produces the usage hint, valid body is dispatched to the agent orchestrator, and oversize task bodies are rejected before the agent runs.

## Context
- `src/handlers.py:handle_agent` — handles `/agent <task>`.
- Uses `runtime.agent_orchestrator.run_task(task)` and the same rate-limit/length checks as `handle_text`.

## Requirements
Add `tests/test_handlers_agent.py`:
- `/agent` with empty body → reply contains the usage hint (`"Usage: ` `/agent <task>` `"`); `agent_orchestrator.run_task` not called.
- `/agent What is 12*15?` → `run_task("What is 12*15?")` called once; reply contains the orchestrator's return value.
- Oversize task (length > `MAX_USER_INPUT_CHARS`) → polite rejection reply; `run_task` not called; history (if any) not touched.
- Rate-limited user → polite "slow down" reply; `run_task` not called.
- Empty agent reply (`run_task` returns `""`) → fallback phrase from `ERROR_PHRASES` is used.

## Implementation Notes
- Use `make_message(text="/agent ...")`; the handler strips the prefix.
- Stub `agent_orchestrator.run_task = AsyncMock(return_value="42")`.
- For the rate-limit case, flip `rate_limiter.is_allowed = AsyncMock(return_value=False)`.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Five cases covered, all passing.
- [x] No LLM call.
- [x] Marked `@pytest.mark.handlers`.

## Affected Files / Components
- `tests/test_handlers_agent.py` (new)
- `src/handlers.py` (read-only)

## Risks / Dependencies
- Depends on TF-01, TF-02, TTD-01.

## Validation Steps
1. `pytest -q tests/test_handlers_agent.py` — passes.
2. Remove the empty-body guard — usage-hint test fails.
3. Full suite green.

## Follow-ups (optional)
- Add a test for `parse_mode="Markdown"` once a Markdown rendering bug is reported (deferred).
