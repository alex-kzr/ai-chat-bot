# THC-02 - Test handle_text happy path

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Cover the most-traveled bot path end-to-end (handler boundary inwards): user resolution, rate-limit pass, length pass, orchestrator dispatch, and reply delivery. This is the test that catches "the bot stopped responding" regressions.

## Context
- `src/handlers.py:handle_text` — orchestrator-driven chat path.
- Dependencies accessed via `get_runtime()` — use TTD-01 override or monkeypatch.

## Requirements
Add `tests/test_handlers_text.py`:
- First-time user: `users.get_or_create` returns `(user, created=True)` → `UserCreated` is published on the event bus exactly once.
- Returning user: `created=False` → no `UserCreated` published.
- Rate-limit pass: `chat_orchestrator.process_text` is called with the resolved `user_id` and the trimmed text.
- Reply delivered: `message.answer` called with the orchestrator's reply text.
- `_log_response` background task is scheduled (assert via spying on `asyncio.create_task` or by awaiting all pending tasks before assertions).

## Implementation Notes
- Use `make_message`, `fake_runtime`, recording subscriber on `event_bus`.
- Stub `chat_orchestrator.process_text` to return a duck-typed `ProcessOutcome` with `.reply` and `.llm_raw`.
- Use `pytest.mark.asyncio` (or rely on `asyncio_mode = "auto"`).
- Mark with `@pytest.mark.handlers`.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Orchestrator called with correct args.
- [x] Reply delivered via `message.answer`.
- [x] `UserCreated` published only on first contact.
- [x] No LLM, no Telegram network call.

## Affected Files / Components
- `tests/test_handlers_text.py` (new)
- `src/handlers.py` (read-only)

## Risks / Dependencies
- Depends on TF-01, TF-02, TTD-01.

## Validation Steps
1. `pytest -q tests/test_handlers_text.py` — passes.
2. Comment out `await message.answer(...)` — test fails.
3. Full suite green.

## Follow-ups (optional)
- Add a slow-typing-indicator test once that timing becomes configurable.
