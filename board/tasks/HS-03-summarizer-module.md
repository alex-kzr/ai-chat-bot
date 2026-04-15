# HS-03 - Create summarizer module

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Isolate all summarization logic in a dedicated `src/summarizer.py` module so the handler only calls a single high-level function and the rest of the system has no knowledge of summarization internals.

## Context
`src/history.py` already manages per-user message lists. `src/llm.py` already has `ask_llm()` for LLM calls. `src/config.py` will expose `SUMMARY_THRESHOLD` and `SUMMARY_KEEP_RECENT` after HS-01. This module sits between them and implements the summarization lifecycle.

## Requirements

### Functions to implement

**`needs_summarization(user_id: int) -> bool`**
- Returns `True` if `len(get_history(user_id)) > SUMMARY_THRESHOLD`.
- Pure check, no side effects.

**`get_messages_to_summarize(user_id: int) -> list[dict]`**
- Returns the slice of history that will be replaced: all messages except the last `SUMMARY_KEEP_RECENT`.
- Returns empty list if history is not long enough.

**`call_llm_for_summary(messages: list[dict]) -> str`**
- Sends `messages` to the LLM with `SUMMARIZATION_PROMPT` as the system prompt.
- Returns the summary string.
- On LLM error, logs the error and returns an empty string (caller must handle gracefully).
- Must be `async`.

**`compress_history(user_id: int) -> None`**
- Orchestrates the full summarization flow:
  1. Call `get_messages_to_summarize()`.
  2. If list is empty, return early.
  3. Call `call_llm_for_summary()`.
  4. If summary is empty (LLM error), return early without modifying history.
  5. Retain `get_history(user_id)[-SUMMARY_KEEP_RECENT:]` as the recent messages.
  6. Replace `_store[user_id]` with `[summary_entry] + recent_messages` where `summary_entry = {"role": "system", "content": f"[Conversation summary]\n{summary}"}`.
- Log when compression happens and how many messages were replaced.
- Must be `async`.

## Implementation Notes
- Import `get_history` from `src.history`; do NOT import `_store` directly — expose a new `replace_history(user_id, messages)` helper in `src/history.py` instead (see Affected Files).
- `call_llm_for_summary` must not use the regular `ask_llm()` (which appends the system prompt + user history). Build a minimal `httpx` call or a dedicated thin wrapper to avoid circular context injection.
- `compress_history` is the only public entry point the handler needs.

## Definition of Done
- [ ] `src/summarizer.py` created with all four functions
- [ ] `needs_summarization` uses `SUMMARY_THRESHOLD` from config
- [ ] `call_llm_for_summary` uses `SUMMARIZATION_PROMPT` and handles LLM errors gracefully
- [ ] `compress_history` replaces old messages with `[summary_entry] + recent`
- [ ] Per-user isolation: no shared state between users
- [ ] `replace_history()` helper added to `src/history.py`
- [ ] Logged appropriately at INFO level

## Affected Files / Components
- `src/summarizer.py` (new)
- `src/history.py` — add `replace_history(user_id: int, messages: list[dict]) -> None`
- `src/config.py` — `SUMMARY_THRESHOLD`, `SUMMARY_KEEP_RECENT` (HS-01)
- `src/prompts.py` — `SUMMARIZATION_PROMPT` (HS-02)

## Risks / Dependencies
- Depends on HS-01 and HS-02 being complete.
- `call_llm_for_summary` makes an async HTTP call — treat LLM errors as non-fatal.
- Summary entry uses `role: "system"` which some models may handle differently. Chosen to keep it distinct from user/assistant turns.

## Validation Steps
1. Unit-test `needs_summarization`: create a fake `_store` with 11 messages → `True`; 9 messages → `False`.
2. Unit-test `get_messages_to_summarize`: 11 messages, `SUMMARY_KEEP_RECENT=4` → returns first 7 messages.
3. Integration-test `compress_history`: after call, `get_history(user_id)` has 5 entries (1 summary + 4 recent); first entry has `role == "system"` and content starts with `[Conversation summary]`.
4. Verify second `compress_history` call on same user produces a new summary entry rather than duplicating.

## Follow-ups (optional)
- Recursive summarization: if summary entry itself is very long, future task can summarize the summary.
- Char-count based threshold as an alternative to message count.
