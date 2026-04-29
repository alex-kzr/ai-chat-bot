# FEC-02 - Unsupported message types ignored

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Confirm the bot's "text only" boundary: photos, voice, stickers, documents, and other non-text updates do not trigger the LLM or agent and do not crash the dispatcher.

## Context
- `src/handlers.py` registers `handle_text` with `F.text` filter.
- `project-overview.md` documents non-text messages as silently ignored.

## Requirements
Add `tests/test_handlers_unsupported_types.py`:
- Build messages with `text=None` and one of: `photo`, `voice`, `sticker`, `document` set to a truthy mock.
- Assert that the `F.text` filter excludes these messages — at the dispatcher level, the registered handler is not selected.
- As a complementary test, call `handle_text(message)` directly with `text=None` and assert it raises a clean `AttributeError`/`TypeError` *before* any orchestrator call, **OR** add a defensive `if not message.text: return` guard and test it. Choose one approach and document it in this task.

## Implementation Notes
- For the dispatcher-level test, use aiogram's `Router.resolve_used_update_types()` or build a `Dispatcher` and feed it a mocked update; if that is too heavy, restrict to the direct-call test.
- Prefer the lighter direct-call approach unless the dispatcher integration buys real safety.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Direct-call behavior on `text=None` documented and asserted.
- [x] No LLM/agent call.
- [x] Marked `@pytest.mark.handlers`.

## Affected Files / Components
- `tests/test_handlers_unsupported_types.py` (new)
- `src/handlers.py` (potentially: defensive `if not message.text: return` guard).

## Risks / Dependencies
- Depends on TF-01, TF-02.

## Validation Steps
1. `pytest -q tests/test_handlers_unsupported_types.py` — passes.
2. Send a photo manually (smoke) — bot stays silent (out-of-band check, not part of CI).
3. Full suite green.

## Follow-ups (optional)
- Polite "I only handle text messages" reply — explicit feature decision required first.
