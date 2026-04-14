# SR-05 - Validate end-to-end after refactoring

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Confirm that the bot functions correctly after the full `src/` restructuring — no regressions, clean startup, correct message handling.

## Context
SR-01 through SR-04 moved files, fixed imports, and updated the entry point. This task verifies the result is a working system, not just code that compiles.

## Requirements
- Bot starts without errors from `python main.py`
- `/start` command returns welcome message
- A regular text message is proxied to LLM and returns a response
- When Ollama is unavailable, bot returns an error phrase (no crash)
- Bot shuts down cleanly on `Ctrl+C`

## Implementation Notes
- If Ollama is not running locally, test only import resolution and startup sequence (bot will print a warning and use default model)
- Check Python import resolution with `python -c "import src.bot"` as a minimum smoke test

## Definition of Done
- [ ] `python main.py` starts without ImportError or other startup errors
- [ ] Model selection prompt appears on startup
- [ ] `/start` handled correctly
- [ ] Text messages handled correctly
- [ ] Error handling works when Ollama is unavailable
- [ ] No regressions compared to pre-refactoring behavior

## Affected Files / Components
- All `src/` modules (read-only verification)
- `main.py`

## Risks / Dependencies
- Depends on SR-01 through SR-04 all being Done
- Requires Ollama running for full functional test (smoke test can skip this)

## Validation Steps
1. `python -c "import src.bot"` — no errors
2. `python main.py` — startup log appears, model selection shown
3. Send `/start` in Telegram — receive welcome message
4. Send a question — receive LLM or provocation response
5. Stop Ollama, send a message — receive error phrase, bot stays alive
6. `Ctrl+C` — clean shutdown

## Follow-ups (optional)
- Update `docs/overview.md` project structure section to reflect new `src/` layout
