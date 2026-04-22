# EB-01 - Implement in-memory event bus

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Add a lightweight event bus that modules can use for loose in-process communication.

## Context
The assignment requires events such as `UserCreated`, `MessageReceived`, and `ResponseGenerated` without external systems. The current runtime already wires shared services explicitly, which is the right place to add an event bus.

## Requirements
- Implement a simple in-memory publish/subscribe event bus.
- Define typed event contracts for `UserCreated`, `MessageReceived`, and `ResponseGenerated`.
- Support multiple handlers per event type.
- Add structured logging for event publishing and handler failures.
- Keep handler errors contained so one failed subscriber does not prevent other subscribers from running.

## Implementation Notes
- Prefer explicit event classes with dataclasses and typed handler protocols.
- Decide whether handlers are sync, async, or both; keep the first implementation simple and consistent with the async app.
- Avoid retries unless they can be implemented without hiding persistent failures.

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
- `src/events/`
- `src/runtime.py`
- `tests/`

## Risks / Dependencies
- Async handler execution order must be deterministic enough for tests.
- Logging should not leak message content at inappropriate levels.

## Validation Steps
1. Subscribe two handlers to one event.
2. Publish the event.
3. Expected result: both handlers run, event logging is emitted, and failures are captured without crashing unrelated handlers.
