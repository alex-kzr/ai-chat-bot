# HS-01 - Add summarization config constants

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Expose `SUMMARY_THRESHOLD` and `SUMMARY_KEEP_RECENT` as top-level constants in `src/config.py` so the summarization trigger and retention window are configurable without touching any logic.

## Context
`src/config.py` already holds `MAX_HISTORY_MESSAGES`. Summarization needs two additional values:
- `SUMMARY_THRESHOLD` — how many messages in history trigger a summarization pass.
- `SUMMARY_KEEP_RECENT` — how many of the most recent messages to leave untouched after summarization.

## Requirements
- Add `SUMMARY_THRESHOLD: int = 10` (default: trigger when history exceeds 10 messages).
- Add `SUMMARY_KEEP_RECENT: int = 4` (default: keep last 4 messages verbatim).
- Both values must be readable from environment variables (`SUMMARY_THRESHOLD`, `SUMMARY_KEEP_RECENT`) with the defaults above as fallback.
- Add inline comments explaining each constant.

## Implementation Notes
- Pattern matches existing `MAX_HISTORY_MESSAGES` entry.
- Use `int(os.getenv("SUMMARY_THRESHOLD", "10"))` style.
- `SUMMARY_KEEP_RECENT` must always be less than `SUMMARY_THRESHOLD`; add an assertion to enforce this at startup.

## Definition of Done
- [ ] `SUMMARY_THRESHOLD` and `SUMMARY_KEEP_RECENT` present in `src/config.py`
- [ ] Both readable via env vars with documented defaults
- [ ] Assertion guards `SUMMARY_KEEP_RECENT < SUMMARY_THRESHOLD`
- [ ] No regressions in existing config usage

## Affected Files / Components
- `src/config.py`

## Risks / Dependencies
- None. Pure config addition.

## Validation Steps
1. Import `src.config` in a Python REPL.
2. Check `config.SUMMARY_THRESHOLD == 10` and `config.SUMMARY_KEEP_RECENT == 4`.
3. Set `SUMMARY_THRESHOLD=3` and `SUMMARY_KEEP_RECENT=1` via env and confirm values are picked up.
4. Set `SUMMARY_KEEP_RECENT >= SUMMARY_THRESHOLD` and confirm `AssertionError` is raised at import.

## Follow-ups (optional)
- HS-02 depends on this task being complete before the summarizer module can reference these constants.
