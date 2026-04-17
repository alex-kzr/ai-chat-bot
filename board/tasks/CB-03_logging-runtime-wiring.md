# CB-03 - Centralize logging and runtime wiring

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Create one consistent place for logging setup and runtime dependency construction so observability is predictable across the whole app.

## Context
Logging is currently configured partly in `src/bot.py` via `logging.basicConfig()` and partly in `src/context_logging.py` via a custom singleton logger. This splits responsibilities between bootstrap, context formatting, and agent event logging.

## Requirements
- Move root logging setup into a dedicated bootstrap/logging module.
- Keep context logging behavior, but separate logger construction from message formatting and token utilities.
- Introduce explicit runtime wiring for shared dependencies such as settings, clients, and services.

## Implementation Notes
- Favor dependency injection through factory functions or a lightweight application container.
- Avoid duplicate handlers and preserve current console/file modes.
- Keep structured agent events compatible with existing logs wherever practical.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- src/bot.py
- src/context_logging.py
- src/agent/core.py
- main.py

## Risks / Dependencies
- Depends on CB-01 and CB-02 because wiring should be anchored in the new bootstrap path.
- Logging behavior is user-visible during debugging, so accidental noise or missing handlers would be costly.

## Validation Steps
1. Start the bot with console logging and verify startup, context, and agent logs still appear.
2. Switch to file logging and verify files are created and populated correctly.
3. Confirm repeated initialization does not duplicate handlers.

## Follow-ups (optional)
- Split `context_logging.py` into smaller modules once the wiring is stable.
