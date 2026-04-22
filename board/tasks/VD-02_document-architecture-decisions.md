# VD-02 - Document architecture decisions

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Explain the modular monolith and event-driven flow for future maintainers.

## Context
The assignment deliverables require a README explanation, architecture decisions, and an example flow where a user sends a message, events are triggered, a response is generated, and history is updated via events.

## Requirements
- Update architecture documentation with module responsibilities.
- Document public interfaces and dependency direction.
- Add an example event flow for a normal user message.
- Note that the event bus is in-memory and not a durable message broker.
- Update README with the architectural summary and validation commands.

## Implementation Notes
- Keep documentation aligned with the final file layout.
- Include the three required modules: Users, Chat/AI, and History.
- Mention future scaling path from in-memory event bus to external broker without implementing it.

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
- `README.md`
- `docs/architecture.md`
- `docs/project-overview.md`
- `docs/domain-model.md`

## Risks / Dependencies
- Documentation can drift if written before implementation is complete.
- Depends on final MM and EB implementation details.

## Validation Steps
1. Read README and architecture docs after implementation.
2. Compare documented module names and event names with source code.
3. Expected result: docs match the implemented architecture and include the required example flow.
