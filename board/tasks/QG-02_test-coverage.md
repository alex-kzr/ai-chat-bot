# QG-02 - Expand automated test coverage for critical flows

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Protect the refactoring with meaningful automated tests around the modules most likely to regress.

## Context
The repository currently contains only `tests/test_context_logging.py`, and `pytest` is not installed in the current environment by default. Critical paths such as config parsing, history trimming, summarization decisions, parser contracts, tool behavior, and handler orchestration are untested.

## Requirements
- Add unit tests for settings parsing and validation.
- Add tests for history/state management and summarization thresholds.
- Add tests for parser/tool contracts and high-value orchestration paths.

## Implementation Notes
- Keep tests behavior-focused and avoid over-mocking internal details.
- Mock network boundaries at the Ollama gateway level instead of patching every caller.
- Separate pure unit tests from integration-style tests for async orchestration.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- tests/
- src/config.py
- src/history.py
- src/summarizer.py
- src/agent/parser.py
- src/agent/tools.py
- src/handlers.py

## Risks / Dependencies
- Depends on refactoring boundaries from earlier phases; otherwise tests will lock in legacy structure.
- Async tests may need new fixtures or test utilities.

## Validation Steps
1. Run the test suite locally and verify new tests cover refactored modules.
2. Simulate failure paths for parsing, timeouts, and summarization errors.
3. Confirm tests remain deterministic and do not require real network access.

## Follow-ups (optional)
- Add coverage reporting once the baseline suite is stable.
