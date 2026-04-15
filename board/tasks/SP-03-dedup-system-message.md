# SP-03 - Add deduplication guard in ask_llm()

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Prevent the system prompt from being injected twice if the caller's `history` list already begins with a `role: system` entry (e.g., a compressed summary stored as a system message by the summarizer).

## Context
`src/summarizer.py` stores compressed history as `{"role": "system", "content": "[Summary] ..."}` entries. If such an entry is already the first element of `history` when `ask_llm()` is called, the current code would produce two consecutive system messages, which can confuse the LLM or cause unexpected behavior.

## Requirements
- Before prepending the configured system prompt, check whether `history[0]["role"] == "system"`
- If a system message is already present, skip injection
- The guard must only apply when `SYSTEM_PROMPT_ENABLED` is `True` (no-op otherwise)

## Implementation Notes
- Condition: `if config.SYSTEM_PROMPT_ENABLED and not (history and history[0].get("role") == "system")`
- This keeps the logic in a single readable condition inside `ask_llm()`
- No changes needed outside `src/llm.py`

## Definition of Done
- [ ] Deduplication guard is implemented in `ask_llm()`
- [ ] When history starts with a system message, the configured prompt is NOT prepended
- [ ] When history is empty or starts with a non-system role, the prompt IS prepended
- [ ] No regressions in normal chat flow
- [ ] Code is clean and consistent

## Affected Files / Components
- `src/llm.py`

## Risks / Dependencies
- Depends on SP-02 (conditional injection logic must be in place first)

## Validation Steps
1. Normal chat (no summary in history) → system prompt appears first in logged payload
2. Trigger summarization (send >SUMMARY_THRESHOLD messages) → confirm only one system message in logged payload after compression
3. Disable system prompt (`SYSTEM_PROMPT_ENABLED=false`) → confirm no system message at all

## Follow-ups (optional)
- Consider logging a warning when deduplication fires, to aid debugging
