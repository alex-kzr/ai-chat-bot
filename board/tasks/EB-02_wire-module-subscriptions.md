# EB-02 - Wire module subscriptions

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Connect module event handlers through bootstrap/runtime wiring instead of direct imports between feature modules.

## Context
The History module must subscribe to chat events and save messages without the Chat/AI module calling it directly. Runtime wiring already centralizes shared dependencies in `src/runtime.py`.

## Requirements
- Register event subscriptions during runtime creation.
- Subscribe History handlers to `MessageReceived` and `ResponseGenerated`.
- Keep subscription wiring outside module internals.
- Ensure modules receive dependencies through constructors or public registration functions.

## Implementation Notes
- Add a dedicated function such as `register_event_handlers(runtime)` or keep registration inside `create_runtime`.
- Avoid circular imports between users, chat, history, and events packages.
- Keep subscription wiring testable with a fake or real in-memory event bus.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- `src/runtime.py`
- `src/modules/history/`
- `src/events/`
- `tests/`

## Risks / Dependencies
- Hidden global runtime access would weaken the modular boundary.
- Depends on EB-01 event bus implementation and MM-04 History public interface.

## Validation Steps
1. Build a runtime with the event bus and History module.
2. Publish message events through the bus.
3. Expected result: History stores messages through subscriptions without Chat/AI importing History internals.
