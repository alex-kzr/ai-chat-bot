# CL-02 - Implement trim_history() in history.py

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Add a dedicated `trim_history()` function to `src/history.py` that enforces the message-count limit via FIFO removal and logs when trimming occurs.

## Context
`src/history.py` currently stores unlimited messages per user. The new function must be self-contained so it can be called from `append_message()` (CL-03) and potentially from other entry points in the future (e.g. a scheduled cleanup).

## Requirements
- Import `MAX_HISTORY_MESSAGES` from `src.config`
- Implement `trim_history(user_id: int) -> None`
  - If the user has no history, return immediately (no-op)
  - While `len(_store[user_id]) > MAX_HISTORY_MESSAGES`, remove the first element (`pop(0)`)
  - Log a `DEBUG`-level message each time a message is removed, including `user_id` and remaining count
- Keep history format unchanged: `[{"role": ..., "content": ...}, ...]`

## Implementation Notes
- Use Python's `logging` module (`logging.getLogger(__name__)`)
- `pop(0)` on a list is O(n); acceptable for the expected history sizes (<100 messages)
- Do NOT modify `get_history()` or `clear_history()`

## Definition of Done
- [ ] `trim_history(user_id)` exists in `src/history.py`
- [ ] Function is a no-op when history is within limit
- [ ] Oldest messages are removed first (index 0)
- [ ] DEBUG log emitted on each removed message
- [ ] History data format unchanged
- [ ] No errors when called on a user with no history

## Affected Files / Components
- `src/history.py`
- `src/config.py` (read-only import)

## Risks / Dependencies
- Depends on CL-01 (`MAX_HISTORY_MESSAGES` must exist in `src/config.py`)

## Validation Steps
1. Manually populate `_store[999]` with 25 mock messages
2. Call `trim_history(999)`
3. Assert `len(get_history(999)) == 20`
4. Assert first remaining message was previously at index 5 (oldest 5 removed)
5. Call `trim_history(0)` (unknown user) — no exception raised

## Follow-ups (optional)
- CL-03 wires this into `append_message()`
- Future: add char-based strategy branch inside `trim_history()`
