# STS-02 - Wire static analysis tooling

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make security and quality issues visible without depending on humans noticing them. `bandit` catches common Python security pitfalls (e.g. `subprocess` with shell, weak crypto, `pickle`), `pip-audit` flags vulnerable dependencies, and `ruff` keeps the codebase linted.

## Context
- Project layout uses `pyproject.toml` if present, otherwise stand-alone configs are fine. Confirm what exists at the repo root before deciding.
- Dependencies are managed via `requirements.txt` (or similar). The new tools must not become runtime deps.

## Requirements
- Add config for the three tools, scoped to this repo:
  - `ruff`: enable a sensible default ruleset (`E`, `F`, `W`, `B`, `I`, `UP`, `S` for security-focused checks). Configure line length to match the codebase. Exclude `tests/` from the most pedantic rules if needed.
  - `bandit`: target `src/`. Skip noisy rules that conflict with how the agent loop already handles errors (only after reviewing each skip).
  - `pip-audit`: no config needed; it just runs against `requirements.txt`.
- Add `requirements-dev.txt` (or extras in `pyproject.toml`) listing the three tools.
- Document in `README.md` how to run each tool locally:
  ```
  ruff check src tests
  bandit -r src
  pip-audit -r requirements.txt
  ```
- Do **not** wire these into CI as part of this task — that is a separate ops change. Just make them runnable by hand.

## Implementation Notes
- Run each tool once after configuring and either fix or explicitly suppress real findings, so the baseline is green. Document any suppressions inline with a comment explaining why.
- Keep changes scoped to tooling/config; do not refactor unrelated code to satisfy lints.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] `ruff check src tests` passes (or has documented, justified ignores).
- [ ] `bandit -r src` produces no high-severity findings (or has documented suppressions).
- [ ] `pip-audit -r requirements.txt` runs successfully and current findings are documented in the security report (PR description) — package upgrades are out of scope here.
- [ ] README has a "Static analysis" section.
- [ ] Dev-only tooling does not creep into runtime dependencies.

## Affected Files / Components
- `pyproject.toml` or new `ruff.toml` / `.bandit`
- `requirements-dev.txt` (or pyproject extras)
- `README.md` (new "Static analysis" section)

## Risks / Dependencies
- Initial `ruff`/`bandit` runs may surface dozens of pre-existing findings. Keep the scope tight: silence noisy rules, fix only real security issues, document the rest as follow-ups.
- `pip-audit` may report CVEs in transitive deps — document and prioritize separately.

## Validation Steps
1. Run `ruff check src tests` — green.
2. Run `bandit -r src` — no high-severity findings.
3. Run `pip-audit -r requirements.txt` — output captured in the report.
4. Confirm the README section explains all three commands and where their configs live.

## Follow-ups (optional)
- Wire the three commands into pre-commit and CI.
- Track and remediate `pip-audit` findings as a dedicated task.
