# RPL-02 - Remove uncertainty detection from llm.py

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
`llm.py` contains `_is_uncertain()` — the function that scans LLM responses for uncertainty keywords and triggers provocation phrase substitution. Removing it and simplifying `ask_llm()` eliminates the core runtime provocation mechanism.

## Context
- File: `llm.py`
- `_is_uncertain(answer, user_text) → bool` (lines 9–18): keyword scan + echo detection.
- `ask_llm()` (lines 21–46): calls `_is_uncertain()` and returns `random.choice(PROVOCATION_PHRASES)` when it returns `True`.
- Current import line: `from prompts import SYSTEM_PROMPT, ERROR_PHRASES, PROVOCATION_PHRASES, UNCERTAINTY_KEYWORDS`

## Requirements
- Delete the `_is_uncertain()` function.
- Remove `PROVOCATION_PHRASES` and `UNCERTAINTY_KEYWORDS` from the import statement.
- Remove the `if _is_uncertain(...)` branch inside `ask_llm()`.
- `ask_llm()` should always return `(llm_raw, llm_raw)` on a successful LLM call.
- Remove `import random` only if it is no longer used anywhere in the file (check `ERROR_PHRASES` usage — it still uses `random.choice`).
- Signature `ask_llm(user_text) → tuple[str, str]` must remain unchanged.

## Implementation Notes
- After the change `ask_llm()` flow: build payload → POST → extract content → return `(llm_raw, llm_raw)`.
- `random` is still needed for `random.choice(ERROR_PHRASES)` — do NOT remove the import.
- The return type tuple `(llm_raw, bot_reply)` stays the same; callers (`handlers.py`) are unaffected.

## Definition of Done
- [ ] `_is_uncertain()` function deleted
- [ ] Import no longer references `PROVOCATION_PHRASES` or `UNCERTAINTY_KEYWORDS`
- [ ] `ask_llm()` contains no provocation branch
- [ ] `import random` retained (still used for ERROR_PHRASES)
- [ ] `python -c "import llm"` runs without errors

## Affected Files / Components
- `llm.py`

## Risks / Dependencies
- Depends on RPL-01 (those symbols must be removed from `prompts.py` first, otherwise the old import line is valid and this task only removes dead imports).
- `handlers.py` calls `ask_llm()` — its signature is unchanged so no edits needed there.

## Validation Steps
1. Open `llm.py` — confirm `_is_uncertain` does not appear anywhere.
2. Confirm import line only references `SYSTEM_PROMPT` and `ERROR_PHRASES`.
3. Run `python -c "import llm"` — no import errors.
4. Manually trace `ask_llm()` logic — it should POST to Ollama and return `(llm_raw, llm_raw)` on success.

## Follow-ups (optional)
- RPL-03: Update welcome message to match the new neutral persona.
