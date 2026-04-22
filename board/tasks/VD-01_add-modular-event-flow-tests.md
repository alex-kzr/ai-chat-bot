# VD-01 - Add modular event-flow tests

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Protect the new modular event-driven architecture with focused automated tests.

## Context
Existing tests cover config, conversation state, LLM streaming, context logging, parser behavior, and agent tools. New tests should verify module boundaries and event-driven history updates.

## Requirements
- Add unit tests for Users, Chat/AI, History, and event bus public interfaces.
- Add an integration-style test for user message flow through events into history.
- Verify failed event handlers do not prevent other handlers from running.
- Use fakes for Ollama and Telegram-facing dependencies.

## Implementation Notes
- Follow pytest Arrange/Act/Assert structure.
- Keep tests deterministic and isolated from real network services.
- Prefer behavior-focused tests over asserting private implementation details.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- `tests/`
- `src/modules/`
- `src/events/`

## Risks / Dependencies
- Tests may overfit early implementation details if public contracts are not stable.
- Depends on MM and EB implementation tasks.

## Validation Steps
1. Run `pytest`.
2. Run targeted tests for events and module services.
3. Expected result: tests pass without requiring Telegram, Ollama, or network access.
