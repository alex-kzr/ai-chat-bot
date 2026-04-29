# WF-02 - Align dependencies and test commands for clean CI execution

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make installation and test execution reliable in a fresh CI runner by aligning dependency files, Python-version expectations, and command entrypoints.

## Context
The prompt explicitly requires isolated execution in a clean environment with no dependency on local developer machines. The current repository documents Python 3.10+ in some places while the requested CI target is Python 3.12, and the workflow must use commands that work consistently in a fresh runner.

## Requirements
- Audit dependency files and test commands used by CI.
- Resolve any mismatches between documented Python support and the required CI runtime.
- Ensure the chosen install path provides everything needed for tests without unnecessary packages.

## Implementation Notes
- Compare `requirements.txt`, `requirements-dev.txt`, and `pyproject.toml` to decide the cleanest CI install strategy.
- Keep the dependency story simple: tests should run from one deterministic install path.
- If Python 3.12 requires code or metadata adjustments, make those changes explicit instead of masking them in CI.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] CI install commands are deterministic and documented
- [ ] The project’s Python version expectations are internally consistent
- [ ] `pytest` runs successfully in a clean environment using the selected dependency set
- [ ] No local-only assumptions remain in the chosen test command path

## Affected Files / Components
- `requirements.txt`
- `requirements-dev.txt`
- `pyproject.toml`
- `README.md`
- `.github/workflows/python-ci.yml`

## Risks / Dependencies
- Dependency: some transitive packages may behave differently on Python 3.12.
- Risk: choosing multiple install paths can create drift between local and CI execution.

## Validation Steps
1. Recreate the CI install sequence in a clean environment.
2. Run the selected test command and verify it passes without extra manual setup.
3. Confirm repository metadata and docs match the supported Python version strategy.

## Follow-ups (optional)
- Consider consolidating dependency declarations further if maintenance overhead remains high.
