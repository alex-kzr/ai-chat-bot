# THC-04 - Test message splitting and typing indicator

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Cover the two pieces of glue users actually feel: the 4096-character Telegram limit (split into ordered chunks) and the typing indicator (started, cancelled cleanly). Bugs here manifest as "bot looks frozen" or "first chunk missing".

## Context
- `src/handlers.py:_split_message` — pure function.
- `src/handlers.py:_keep_typing` — async background task tied to an `asyncio.Event`.

## Requirements
Add `tests/test_handlers_chunking.py`:
- `_split_message`:
  - Reply <= 4096 chars → single chunk.
  - Reply > 4096 chars → multiple chunks; concatenation equals input; each chunk's length is at most 4096; order preserved.
  - Boundary at exactly 4096 and 4097 characters (parametrize).
- `_keep_typing`:
  - When the stop event is set, the loop exits within one tick.
  - Cancelling the task does not raise out of the handler (`finally` wrapper).

## Implementation Notes
- For `_keep_typing`, use a fake `Message` whose `bot.send_chat_action` is `AsyncMock`.
- Use `asyncio.wait_for(task, timeout=…)` to guard against a stuck loop.
- Parametrize length cases with `pytest.param(..., id=...)` for readable IDs.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Splitting verified for under, exactly-at, and over-limit cases.
- [x] Typing-indicator start/stop verified.
- [x] Marked `@pytest.mark.handlers`.

## Affected Files / Components
- `tests/test_handlers_chunking.py` (new)
- `src/handlers.py` (read-only)

## Risks / Dependencies
- Depends on TF-02 (`make_message`).

## Validation Steps
1. `pytest -q tests/test_handlers_chunking.py` — passes.
2. Change `_TELEGRAM_MAX_LEN` to 100 — boundary tests should also pass with new boundary (parametrize from constant).
3. Full suite green.

## Follow-ups (optional)
- Test multi-byte / emoji boundary handling if reports surface.
