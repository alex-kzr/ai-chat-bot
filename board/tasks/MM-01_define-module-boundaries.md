# MM-01 - Define module boundaries and shared contracts

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Create a clear target structure for the modular monolith before moving runtime behavior.

## Context
The project already has service boundaries in `src/runtime.py`, `src/services/chat_orchestrator.py`, `src/conversation.py`, and `src/llm.py`, but users, chat/AI, history, and events are not expressed as independent feature modules.

## Requirements
- Define package boundaries for users, chat/AI, history, and shared event contracts.
- Keep internal implementation details private to each module.
- Expose only public service functions, service classes, or package-level interfaces through `__init__.py`.
- Avoid changing runtime behavior in this task.

## Implementation Notes
- Prefer a shallow structure such as `src/modules/users`, `src/modules/chat`, `src/modules/history`, and `src/events`.
- Use typed dataclasses or typed dictionaries for public contracts.
- Add `__all__` exports for public module APIs.
- Keep dependency direction explicit: handlers/runtime wire modules; modules do not import Telegram handlers.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [x] Manual testing

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- `src/modules/`
- `src/events/`
- `src/contracts.py`
- `src/runtime.py`

## Risks / Dependencies
- Existing imports may become ambiguous if public interfaces are not defined before code moves.
- This task should not move behavior that belongs in later module-isolation tasks.

## Validation Steps
1. Inspect new package layout and public exports.
2. Run import-focused checks or the existing test suite.
3. Expected result: new boundaries exist without changing bot behavior.

## Follow-ups (optional)
- Move concrete behavior into the new packages in MM-02 through MM-04.
