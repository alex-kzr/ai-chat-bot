# RPL-01 - Remove provocation data from prompts.py

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
`prompts.py` contains `PROVOCATION_PHRASES` (10 dismissive phrases) and `UNCERTAINTY_KEYWORDS` (27 keywords) that power the harmful response-replacement feature. Removing them is the first step to eliminating provocation behavior from the system.

## Context
- File: `prompts.py`
- `PROVOCATION_PHRASES` — list of 10 dismissive/hostile reply strings used when the LLM seems uncertain.
- `UNCERTAINTY_KEYWORDS` — list of 27 English keywords whose presence in the LLM reply triggers provocation.
- `SYSTEM_PROMPT` in the same file currently instructs the model to "never say I don't know" with an arrogant persona — this should be replaced with a neutral, helpful instruction.

## Requirements
- Delete the `PROVOCATION_PHRASES` list entirely.
- Delete the `UNCERTAINTY_KEYWORDS` list entirely.
- Replace `SYSTEM_PROMPT` with a neutral, helpful instruction that does not enforce an arrogant persona.
- `ERROR_PHRASES` list must remain (it is used for LLM errors, which is acceptable behavior).

## Implementation Notes
- New `SYSTEM_PROMPT` example: `"You are a helpful assistant. Answer clearly and concisely in the user's language."`
- No other files need changes in this task — `llm.py` imports are handled in RPL-02.

## Definition of Done
- [ ] `PROVOCATION_PHRASES` removed from `prompts.py`
- [ ] `UNCERTAINTY_KEYWORDS` removed from `prompts.py`
- [ ] `SYSTEM_PROMPT` updated to neutral/helpful tone
- [ ] `ERROR_PHRASES` still present and unchanged
- [ ] File is syntactically valid Python

## Affected Files / Components
- `prompts.py`

## Risks / Dependencies
- RPL-02 depends on this task: after removing the lists, `llm.py` imports will break until RPL-02 updates them.

## Validation Steps
1. Open `prompts.py` — confirm `PROVOCATION_PHRASES` and `UNCERTAINTY_KEYWORDS` are gone.
2. Confirm `SYSTEM_PROMPT` no longer references arrogance or "always right".
3. Confirm `ERROR_PHRASES` is still present.
4. Run `python -c "import prompts"` — no errors.

## Follow-ups (optional)
- RPL-02: Update `llm.py` to remove the import and usage of the deleted lists.
