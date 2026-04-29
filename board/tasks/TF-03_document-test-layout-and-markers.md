# TF-03 - Document test layout and markers

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make it obvious where each kind of test belongs, register pytest markers cleanly so they are not "unknown marker" warnings, and confirm async support is set up correctly for the new tests.

## Context
- `pyproject.toml` already has `[tool.pytest.ini_options]` with `asyncio_mode = "auto"`.
- Existing test files are flat under `tests/`; introducing subfolders would invalidate paths in commit history. Keep flat layout, distinguish via filename prefix and markers.

## Requirements
- Register markers in `pyproject.toml`:
  - `unit` — pure logic, no I/O.
  - `handlers` — exercises `src/handlers.py`.
  - `integration` — wires multiple modules together.
- Confirm `asyncio_mode = "auto"` already covers async tests; document it.
- Add a brief comment in `tests/conftest.py` or a `tests/README.md` explaining the file-prefix convention:
  - `test_*_logic.py` — business logic
  - `test_handlers_*.py` — handler-level
  - `test_security_*.py` — security
- No new dependencies.

## Implementation Notes
- Use `[tool.pytest.ini_options].markers` array.
- Do not enforce strict marker mode yet — keep it informative.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [x] Manual testing

## Definition of Done
- [x] Markers registered, no "unknown marker" warnings.
- [x] `tests/README.md` (or equivalent) describes the layout in under 30 lines.
- [x] `pytest -q -m unit` and `pytest -q -m handlers` filter correctly once tests use markers.

## Affected Files / Components
- `pyproject.toml`
- `tests/README.md` or `tests/conftest.py` (header comment)

## Risks / Dependencies
- None.

## Validation Steps
1. `pytest -q` — passes, no marker warnings.
2. `pytest -q -m unit` — runs only unit-marked tests (initially zero; will populate as tasks land).

## Follow-ups (optional)
- Reorganize into `tests/unit/`, `tests/handlers/`, `tests/integration/` once the suite is large enough to warrant the move.
