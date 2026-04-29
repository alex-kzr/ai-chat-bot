# 📋 Tasks — Production CI Pipeline for Python Telegram AI Bot
---

## Phase 1 — Workflow Foundation

### WF-01 Create GitHub Actions Python CI workflow
Add `.github/workflows/python-ci.yml` so pushes to `main` and pull requests automatically run the project test suite in GitHub Actions using Python 3.12.
→ [WF-01_github-actions-python-ci.md](./tasks/WF-01_github-actions-python-ci.md)

### WF-02 Align dependencies and test commands for clean CI execution
Review and adjust dependency installation, Python version expectations, and pytest entrypoints so the repository installs and runs successfully in a fresh runner without relying on local setup drift.
→ [WF-02_ci-dependency-and-command-alignment.md](./tasks/WF-02_ci-dependency-and-command-alignment.md)

### WF-03 Document CI workflow usage and validation checklist
Update repository documentation with the workflow purpose, local reproduction steps, expected triggers, and a concise validation checklist for contributors and reviewers.
→ [WF-03_ci-documentation-and-validation.md](./tasks/WF-03_ci-documentation-and-validation.md)

## Phase 2 — Testability Hardening

### TH-01 Audit and refactor remaining hard-to-test runtime seams
Identify any startup or runtime paths that still couple tests to real environment state, then refactor them toward explicit dependency injection or clearer abstraction boundaries.
→ [TH-01_runtime-seam-audit-and-refactor.md](./tasks/TH-01_runtime-seam-audit-and-refactor.md)

### TH-02 Strengthen deterministic fakes for Telegram and LLM integrations
Improve or add shared fake implementations and fixtures so tests covering Telegram handlers, chat orchestration, and LLM flows remain deterministic and do not require external network access.
→ [TH-02_deterministic-telegram-and-llm-fakes.md](./tasks/TH-02_deterministic-telegram-and-llm-fakes.md)

### TH-03 Add CI-critical regression coverage for isolated execution
Fill any remaining test gaps around startup wiring, handler behavior, and failure paths that must be verified automatically before merge in a clean CI environment.
→ [TH-03_ci-critical-regression-coverage.md](./tasks/TH-03_ci-critical-regression-coverage.md)

## Phase 3 — Quality and Security Gates

### QS-01 Add fast static quality checks to CI
Integrate lightweight linting, typing, or targeted static checks that provide quick feedback without slowing the pipeline unnecessarily.
→ [QS-01_fast-static-quality-checks.md](./tasks/QS-01_fast-static-quality-checks.md)

### QS-02 Harden secret and configuration handling for CI
Ensure bot tokens and other sensitive settings are never committed, are loaded only from environment variables or GitHub Secrets, and are safely represented in tests and documentation.
→ [QS-02_ci-secret-and-config-hardening.md](./tasks/QS-02_ci-secret-and-config-hardening.md)

### QS-03 Optimize CI for reproducibility and speed
Tune the workflow for fast, repeatable execution by minimizing unnecessary installs, choosing stable commands, and documenting the intended tradeoffs of the final design.
→ [QS-03_ci-speed-and-reproducibility-optimization.md](./tasks/QS-03_ci-speed-and-reproducibility-optimization.md)

---
