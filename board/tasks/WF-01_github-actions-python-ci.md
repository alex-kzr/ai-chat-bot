# WF-01 - Create GitHub Actions Python CI workflow

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Create the baseline GitHub Actions workflow that automatically validates the repository on every push to `main` and every pull request.

## Context
The feature prompt requires a production-quality CI pipeline built on GitHub Actions with Python 3.12, automatic execution, zero manual steps, and deterministic behavior in a clean environment. The repository already has `requirements.txt`, `requirements-dev.txt`, and an existing pytest suite, but it does not yet define the required workflow file.

## Requirements
- Create `.github/workflows/python-ci.yml` with triggers for pushes to `main` and pull requests.
- Use `actions/checkout@v4` and `actions/setup-python@v5` with Python `3.12`.
- Install the required dependencies and run the automated test suite with a failing exit code on test failures.

## Implementation Notes
- Start from the workflow structure provided in the prompt and adapt only where the repository needs small practical changes.
- Keep the first version intentionally simple and maintainable before adding optional quality gates in later tasks.
- Prefer commands that contributors can reproduce locally with the same dependency inputs.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] `.github/workflows/python-ci.yml` exists and is valid YAML
- [ ] Pushes to `main` and pull requests trigger the workflow
- [ ] Test failures cause the job to fail immediately
- [ ] No manual setup steps are required in the workflow
- [ ] The workflow remains simple and maintainable

## Affected Files / Components
- `.github/workflows/python-ci.yml`
- `requirements.txt`
- `requirements-dev.txt`
- `pyproject.toml`

## Risks / Dependencies
- Dependency: the repository must install cleanly on Python 3.12.
- Risk: if the workflow installs the wrong dependency set, CI may pass locally but fail in GitHub Actions.

## Validation Steps
1. Inspect the workflow triggers and confirm `push` to `main` and `pull_request` are configured.
2. Validate that dependency installation and `pytest` invocation match the repository structure.
3. Push a branch or open a pull request and confirm the workflow starts automatically.

## Follow-ups (optional)
- Add quality or security steps once the baseline test job is stable.
