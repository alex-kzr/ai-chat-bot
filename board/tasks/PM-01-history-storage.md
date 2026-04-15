# PM-01 - Create history storage module

## Status
- [x] To Do
- [x] In Progress
- [x] Done

## Purpose
Provide a dedicated, isolated module for storing and retrieving per-user conversation history. Keeps history logic out of the handler and LLM layers.

## Context
The bot currently has no persistent state. User identity is available via `message.from_user.id` (Telegram numeric ID, always present). History will be stored in-memory as a plain Python dictionary for the prototype.

Related files:
- `src/handlers.py` — will call this module
- `src/llm.py` — will consume the history list returned by this module

## Requirements
- Create `src/history.py`
- Store history as `dict[int, list[dict]]` keyed by Telegram user ID
- Implement `get_history(user_id: int) -> list[dict]` — returns copy of current history (empty list if none)
- Implement `append_message(user_id: int, role: str, content: str) -> None` — adds `{"role": role, "content": content}` to the user's list
- Implement `clear_history(user_id: int) -> None` — removes user's history entry
- Handle missing/non-existent user gracefully (return `[]`, not raise)

## Implementation Notes
- Use a module-level `_store: dict[int, list[dict]] = {}` as the backing store
- `get_history` must return a **copy** (`list(...)` or `[*history]`) so callers cannot mutate stored state
- Roles must be `"user"` or `"assistant"` — no validation required at this layer (responsibility of callers)
- No file I/O or threading needed for this task

## Definition of Done
- [x] `src/history.py` created with all three functions
- [x] `get_history` returns `[]` for unknown user ID
- [x] `append_message` correctly accumulates messages in order
- [x] `clear_history` removes the entry without error
- [x] No import of handler or llm modules (no circular deps)
- [x] Code is clean and consistent

## Affected Files / Components
- `src/history.py` (new file)

## Risks / Dependencies
- None — this module has no external dependencies

## Validation Steps
1. Import `src.history` in a Python REPL or test script
2. Call `get_history(123)` → expect `[]`
3. Call `append_message(123, "user", "Hi")` then `get_history(123)` → expect `[{"role": "user", "content": "Hi"}]`
4. Call `append_message(123, "assistant", "Hello!")` then `get_history(123)` → expect list with both entries
5. Call `clear_history(123)` then `get_history(123)` → expect `[]`
6. Confirm user `456` has empty history while user `123` has entries

## Follow-ups (optional)
- PM-02, PM-03 depend on this task being done first
- Future: swap in-memory store for SQLite or JSON-file backend without changing the public API
