# TH-01 - Audit and refactor remaining hard-to-test runtime seams

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Improve testability where runtime or startup code still depends too directly on environment state, global configuration, or concrete integrations.

## Context
The prompt treats testability as an architectural concern, not just a testing concern. This repository already has modular boundaries and runtime wiring, but CI reliability depends on every critical path being invocable under test without talking to real services or depending on developer-specific machine state.

## Requirements
- Audit startup, runtime wiring, and service boundaries for hard-to-test dependencies.
- Refactor any identified hotspots toward explicit dependency injection or cleaner abstractions.
- Preserve existing behavior while making isolated testing easier.

## Implementation Notes
- Focus on the smallest set of changes that materially improve test isolation.
- Prefer constructor or function-parameter injection over hidden globals.
- Avoid broad refactors that are not needed for CI stability.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Hard-to-test runtime seams are identified and documented
- [x] Necessary refactors improve isolation without changing user-facing behavior
- [x] Tests can cover the affected paths without real network calls or local runtime assumptions
- [x] The architecture remains simple and modular

## Affected Files / Components
- `src/bootstrap.py`
- `src/runtime.py`
- `src/handlers.py`
- `src/services/chat_orchestrator.py`

## Risks / Dependencies
- Dependency: follow existing module boundaries and typed settings patterns.
- Risk: refactoring runtime wiring can introduce regressions if coverage is not added alongside the change.

## Validation Steps
1. Identify the runtime paths that were previously awkward to test.
2. Add or update tests that cover those paths with fakes or mocks only.
3. Verify production wiring still behaves the same after the refactor.

## Notes / Seams addressed
- `src.runtime.create_runtime()` now supports optional dependency injection for tests and experiments (no globals required).
- Added a typed `OllamaClient` Protocol (`src/contracts.py`) so deterministic fakes can be passed through wiring without `type: ignore`.
- `src.bootstrap.choose_model()` now supports injected `prompt`/`out` and `is_interactive` to make the startup selection path testable without a real TTY.

## Follow-ups (optional)
- Capture any larger architectural opportunities separately if they exceed CI scope.
