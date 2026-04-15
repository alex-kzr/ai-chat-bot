# CL-03 - Call trim_history() inside append_message()

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Automatically enforce the history limit on every write so callers never need to remember to trim manually.

## Context
`append_message()` in `src/history.py` is the single point where messages enter the store. Adding one `trim_history()` call here guarantees the limit is always applied regardless of which handler or future module appends a message.

## Requirements
- After `_store[user_id].append(...)` in `append_message()`, call `trim_history(user_id)`
- No other changes to the function signature or return value
- Behavior must be transparent to callers — existing code in `src/handlers.py` must not require any updates

## Implementation Notes
- One-line addition: `trim_history(user_id)` at the end of `append_message()`
- `trim_history` is defined in the same module — no new imports needed

## Definition of Done
- [ ] `trim_history(user_id)` is called at the end of `append_message()`
- [ ] `append_message()` signature and return type unchanged
- [ ] `src/handlers.py` requires no changes
- [ ] Sending 25 messages via the bot retains only the last 20

## Affected Files / Components
- `src/history.py`

## Risks / Dependencies
- Depends on CL-02 (`trim_history()` must be implemented first)

## Validation Steps
1. Start the bot
2. Send 25 messages from the same user
3. Inspect history length — must be ≤ 20
4. The first message in history must be the 6th message sent (oldest 5 removed)
5. Send messages as a second user — their history is unaffected

## Follow-ups (optional)
- None; this completes the context limitation feature
