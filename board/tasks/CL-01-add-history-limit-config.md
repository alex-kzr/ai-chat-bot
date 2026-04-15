# CL-01 - Add MAX_HISTORY_MESSAGES constant to config

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Centralise the history size limit in `src/config.py` so it can be adjusted in one place without touching business logic.

## Context
`src/config.py` already holds environment-driven settings (bot token, model name, etc.). Adding the limit constant here follows the existing pattern and makes it easy to override via environment variable in the future.

## Requirements
- Add `MAX_HISTORY_MESSAGES: int = 20` to `src/config.py`
- Add a comment stub for `MAX_HISTORY_CHARS` to document the future char-based strategy
- Default value must be 20 (keeps last 20 messages = ~10 turns)

## Implementation Notes
- Place constants near other tuneable parameters
- Use an `int` type annotation
- Do NOT read from env at this stage — a hardcoded default is sufficient

## Definition of Done
- [ ] `MAX_HISTORY_MESSAGES` exists in `src/config.py`
- [ ] Value is 20
- [ ] Stub comment for `MAX_HISTORY_CHARS` is present
- [ ] No other files changed

## Affected Files / Components
- `src/config.py`

## Risks / Dependencies
- None — purely additive change

## Validation Steps
1. Open `src/config.py`
2. Confirm `MAX_HISTORY_MESSAGES = 20` is present
3. Confirm `import` of the constant from another module succeeds without errors

## Follow-ups (optional)
- CL-02 depends on this constant being importable
