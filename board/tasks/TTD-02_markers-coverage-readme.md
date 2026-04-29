# TTD-02 - Test markers, coverage, and README section

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make the test suite a single, predictable command for new contributors and CI: registered markers, optional coverage, and a short README section pointing at all of it.

## Context
- `pyproject.toml` already configures pytest (`asyncio_mode = "auto"`, `testpaths = ["tests"]`).
- Dev extras already include `pytest`, `pytest-asyncio`. Coverage is not currently wired.

## Requirements
- In `pyproject.toml`:
  - Register `markers` under `[tool.pytest.ini_options]`: `unit`, `handlers`, `integration`, plus the existing `security` (if used).
  - Add `pytest-cov>=5.0` to `[project.optional-dependencies].dev`. Do **not** make it a runtime dependency.
- In `README.md`, add a "Running tests" section with:
  - `pytest -q` — full suite.
  - `pytest -q -m unit` — unit tests only.
  - `pytest -q -m handlers` — handler tests only.
  - `pytest --cov=src --cov-report=term-missing` — coverage (optional).
- Confirm `pytest -q` finishes in under a few seconds locally and in CI.
- No real-network test slips in (`-m "not integration"` should be a no-op or near-no-op).

## Implementation Notes
- Keep README section under ~25 lines.
- Do not introduce a Makefile unless an existing one is present (the repo currently doesn't ship one).

## Testing
- [x] Unit tests
- [ ] Integration tests
- [x] Manual testing

## Definition of Done
- [x] Markers registered, no warnings.
- [x] `pytest --cov=src` works after `pip install -e .[dev]`.
- [x] README updated.
- [x] Suite still green.

## Affected Files / Components
- `pyproject.toml`
- `README.md`

## Risks / Dependencies
- None at runtime; coverage stays optional.

## Validation Steps
1. `pip install -e .[dev]` in a clean venv — succeeds.
2. `pytest -q` — passes.
3. `pytest --cov=src --cov-report=term-missing` — produces a report; failures printed clearly if coverage drops.
4. README "Running tests" section visible at top level of the docs.

## Follow-ups (optional)
- Wire `pytest --cov` into CI with a coverage floor once the suite has matured.
