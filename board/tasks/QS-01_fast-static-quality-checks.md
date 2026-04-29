# QS-01 - Add fast static quality checks to CI

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Expand the CI pipeline with fast code-quality checks that catch obvious issues early without adding unnecessary complexity or runtime cost.

## Context
The repository already documents `ruff`, `mypy`, `bandit`, and `pip-audit`, but the prompt emphasizes speed and practicality. The CI design should choose a lightweight set of checks that materially improve confidence and fit a production-oriented workflow.

## Requirements
- Decide which static checks belong in CI by default.
- Integrate the chosen checks into GitHub Actions with clear failure behavior.
- Keep the workflow fast and maintainable.

## Implementation Notes
- Favor tools that run quickly and have low setup overhead.
- Separate baseline test execution from optional heavier checks if that keeps feedback faster.
- Reuse existing tool configuration in `pyproject.toml` where possible.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Selected static checks are justified and documented
- [x] The workflow fails when those checks fail
- [x] CI runtime remains reasonably fast
- [x] No redundant or low-value quality steps are added

## Affected Files / Components
- `.github/workflows/python-ci.yml`
- `pyproject.toml`
- `README.md`

## Risks / Dependencies
- Dependency: local tooling configuration must be stable enough for CI reuse.
- Risk: too many checks in one job can slow feedback and reduce developer trust in CI.

## Validation Steps
1. Run the selected static checks locally.
2. Confirm the workflow surfaces failures clearly in GitHub Actions.
3. Measure whether the added checks stay within acceptable runtime expectations.

## Follow-ups (optional)
- Split checks into separate jobs later if the team wants parallel feedback.
