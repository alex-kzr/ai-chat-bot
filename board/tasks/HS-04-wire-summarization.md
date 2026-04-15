# HS-04 - Wire summarization into handler pipeline

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Call `compress_history()` automatically before each LLM request in `src/handlers.py` so the context is always bounded and the summary is transparently included in every LLM call without the handler knowing summarization internals.

## Context
`src/handlers.py` currently: loads history → appends user message → calls `ask_llm()` → appends assistant reply. After this task, the flow becomes: load history → **compress if needed** → append user message → call `ask_llm()` → append assistant reply.

Compression must happen before the new user message is appended so the summary covers only prior turns, not the current one.

## Requirements
- Import `compress_history` and `needs_summarization` from `src.summarizer`.
- In `handle_text()`, call `await compress_history(user_id)` after loading history and BEFORE appending the new user message.
- The call must be guarded: only invoke `compress_history` when `needs_summarization(user_id)` returns `True`, to avoid an unnecessary LLM call every turn.
- No changes to the `ask_llm()` signature — it already receives the full history list which now contains the summary entry when present.
- The handler must not expose or log summary content to the user.

## Implementation Notes
- Placement in `handle_text()`:
  ```python
  user_id = message.from_user.id
  # compress before adding new message
  if needs_summarization(user_id):
      await compress_history(user_id)
  append_message(user_id, "user", message.text)
  history = get_history(user_id)
  reply, _ = await ask_llm(message.text, history)
  append_message(user_id, "assistant", reply)
  ```
- `compress_history` is async — `await` it.
- Keep the guard (`needs_summarization`) so normal short conversations have zero summarization overhead.

## Definition of Done
- [ ] `compress_history` and `needs_summarization` imported in `handlers.py`
- [ ] `compress_history` awaited before `append_message` for new user turn
- [ ] Guard condition prevents redundant LLM calls on short histories
- [ ] Existing handler behavior unchanged for histories below threshold
- [ ] No regressions: `/start` command, text messages still work end-to-end

## Affected Files / Components
- `src/handlers.py`

## Risks / Dependencies
- Depends on HS-03 (`compress_history`, `needs_summarization` must exist).
- Adds one async LLM call per threshold crossing — adds latency for that turn only; subsequent turns are fast again.
- If the summarization LLM call fails, `compress_history` returns early without modifying history, so the bot continues with the full (long) history for that turn. This is acceptable graceful degradation.

## Validation Steps
1. Start the bot. Send more than `SUMMARY_THRESHOLD` messages to a single user.
2. Check logs for "Compressing history for user …" message.
3. Confirm `get_history(user_id)` after compression has `SUMMARY_KEEP_RECENT + 1` entries (summary + recent).
4. Continue chatting — verify the bot still answers coherently (summary context preserved).
5. Send messages as a second user — verify their history is unaffected.
6. Restart the bot, send fewer than `SUMMARY_THRESHOLD` messages — confirm no summarization LLM call in logs.

## Follow-ups (optional)
- Expose a `/summary` debug command to show the current summary entry for the user (dev/admin feature).
- Emit a metric or counter each time summarization fires for observability.
