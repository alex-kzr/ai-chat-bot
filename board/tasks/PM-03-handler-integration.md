# PM-03 - Wire history into message handler

## Status
- [x] To Do
- [x] In Progress
- [x] Done

## Purpose
Connect the history storage (PM-01) and the updated LLM call (PM-02) in `handle_text()`, completing the pseudo-memory feature end-to-end.

## Context
After PM-01 and PM-02 are done:
- `src/history.py` provides `get_history()`, `append_message()`, `clear_history()`
- `src/llm.py:ask_llm()` accepts an optional `history` list

This task updates `src/handlers.py` to:
1. Identify the user by `message.from_user.id` (not username)
2. Load history before calling the model
3. Append the new user message to history before the call
4. Call `ask_llm()` with the history
5. Append the assistant reply to history after the call

Related files:
- `src/handlers.py` — file to modify
- `src/history.py` — to import and use
- `src/llm.py` — called with history

## Requirements
- Use `message.from_user.id` (int) as the user key — always present, unlike username
- Before calling `ask_llm`:
  1. `history = get_history(user_id)`
  2. `append_message(user_id, "user", message.text)`
- Call `ask_llm(message.text, history=history)`
- After receiving response: `append_message(user_id, "assistant", bot_reply)`
- Logging may still use `message.from_user.username or message.from_user.id` for human-readable logs
- `/start` handler is unchanged — no history interaction needed

## Implementation Notes
- Import `get_history`, `append_message` from `src.history`
- The history passed to `ask_llm` is the state **before** the current user message (the new message is added inside `ask_llm` as the final entry) — OR — append the user message to history first, then pass the full list and let `ask_llm` use it as-is without appending again. Choose one approach and keep it consistent with PM-02's implementation.
  - **Recommended**: append user message to history **before** passing, and in PM-02 do NOT append the user message again — just use `[system] + history` (where history already contains the new user message as its last entry).
  - Alternative: pass history without the new message and let `ask_llm` append it. Either is valid; document the choice.
- Error path: if `ask_llm` returns an error tuple, still save nothing (or save the error) — decision: **do not save error replies** to avoid polluting history with fallback phrases.

## Definition of Done
- [x] `handle_text()` loads history for the current user before calling the model
- [x] New user message is appended to history
- [x] `ask_llm()` is called with history
- [x] Assistant reply is appended to history after successful response
- [x] Error replies are NOT saved to history
- [x] Two different Telegram users have fully independent histories
- [x] `/start` command behavior is unchanged
- [x] No regressions to typing indicator or async logging
- [x] Code is clean and consistent

## Affected Files / Components
- `src/handlers.py`
- `src/history.py` (read-only dependency)

## Risks / Dependencies
- Depends on PM-01 (history module) and PM-02 (updated ask_llm signature)
- Must complete PM-01 and PM-02 before starting this task

## Validation Steps
1. Start the bot and send "Hi" from User A → bot replies
2. Send "What did I just say?" from User A → bot should correctly reference "Hi"
3. Send "Hi" from User B (different Telegram account) → bot replies without referencing User A's history
4. Send "What did I just say?" from User B → bot should only reference User B's own "Hi"
5. Trigger an Ollama error (e.g., stop Ollama) → confirm fallback reply is sent and history is not corrupted
6. Restart the bot → confirm history resets (in-memory, expected behavior)

## Follow-ups (optional)
- Add `/forget` command that calls `clear_history(user_id)` to let users reset their own context
- Future: persist history to disk so it survives bot restarts
