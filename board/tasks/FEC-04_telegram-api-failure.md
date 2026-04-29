# FEC-04 - Telegram API failure handling

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Verify the handler does not crash, hang, or leak secrets when sending the reply fails (network blip, Telegram rate-limit, server error).

## Context
- `message.answer` is awaited in `handle_text`, `handle_agent`, `handle_start`.
- `_keep_typing` runs as a background task; if `message.answer` raises, the `finally` block must still cancel it.

## Requirements
Add `tests/test_telegram_failures.py`:
- `make_message_with_failing_answer(exc=aiogram_exceptions.TelegramRetryAfter(...))` (or a generic `RuntimeError`).
- Assert the handler logs the failure once.
- Assert the typing-indicator background task is cancelled (no warning about a never-awaited task in `caplog`/warnings).
- Assert the handler does not re-raise (or re-raises in a single, documented path — choose and document).
- Sanitized log line: even when the input contains a fake bot token, the log line is masked.

## Implementation Notes
- Use `pytest.warns(...)` to catch un-awaited-task warnings; ideally there should be none.
- Use `caplog` to assert log content.
- Parametrize the exception type (timeout, retry-after, generic).

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Handler does not crash on Telegram failure.
- [x] Typing-indicator task is cancelled.
- [x] Logs are sanitized.

## Affected Files / Components
- `tests/test_telegram_failures.py` (new)
- `src/handlers.py` (read-only; small defensive try/except may be added if not already present).

## Risks / Dependencies
- Depends on TF-02.

## Validation Steps
1. `pytest -q tests/test_telegram_failures.py` — passes.
2. Force `message.answer` to raise once in a manual run — bot logs and continues.
3. Full suite green.

## Follow-ups (optional)
- Backoff/retry on `TelegramRetryAfter` is a separate, scoped task.
