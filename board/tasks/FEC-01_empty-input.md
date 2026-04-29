# FEC-01 - Empty and whitespace-only input

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Verify the handler does the right thing when the user sends nothing useful: no LLM call, no agent call, no exception, and a deterministic outcome.

## Context
- `src/handlers.py:handle_text` strips text before length checks.
- `src/handlers.py:handle_agent` strips text after removing the `/agent` prefix.

## Requirements
Add `tests/test_handlers_empty_input.py`:
- `handle_text("")`, `"   "`, `"\n\t"` → `chat_orchestrator.process_text` is **not** called; the handler exits cleanly. Document the current observable behavior (silent, or polite reply) and assert it.
- `handle_agent("/agent")`, `"/agent   "` → usage-hint reply (already covered by THC-03 — keep here only if it adds a distinct edge case); `run_task` not called.
- Whitespace-only input does not get appended to history (verify via event bus subscriber).

## Implementation Notes
- Use `make_message` and `fake_runtime`.
- Parametrize the text inputs.
- Assert orchestrator mocks have `call_count == 0`.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Empty / whitespace inputs covered for both handlers.
- [x] No external call triggered.
- [x] Marked `@pytest.mark.handlers`.

## Affected Files / Components
- `tests/test_handlers_empty_input.py` (new)
- `src/handlers.py` (read-only — but this task **may** add a guard if we discover empty text reaches the orchestrator).

## Risks / Dependencies
- Depends on TF-01, TF-02, TTD-01.

## Validation Steps
1. `pytest -q tests/test_handlers_empty_input.py` — passes.
2. Inject a print statement before the orchestrator call; confirm it does not fire on empty input.
3. Full suite green.

## Follow-ups (optional)
- Add a soft-prompt for whitespace-only inputs ("Did you mean to send something?") — out of scope here.
