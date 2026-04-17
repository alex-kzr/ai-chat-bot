# CB-01 - Introduce typed settings object

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Replace implicit module-level configuration with an explicit, validated settings model that is easier to reason about, safer to import, and friendlier to typing and tests.

## Context
Current configuration is spread across module globals in `src/config.py`. The module reads environment variables and raises validation errors at import time, and `src/history.py` imports `MAX_HISTORY_MESSAGES` directly, which hard-codes a runtime value into another module. The `python-configuration`, `python-type-safety`, and `python-anti-patterns` skills all point to typed settings and reduced import-time side effects.

## Requirements
- Replace module-level config constants with a typed settings object or dataclass-based settings container.
- Move validation logic out of import-time side effects and into explicit settings construction.
- Remove direct constant imports like `from src.config import MAX_HISTORY_MESSAGES` in favor of dependency access through settings.

## Implementation Notes
- Prefer a single `Settings` entry point with grouped sections for Ollama, logging, history, and agent settings.
- Keep default values compatible with current `.env.example` behavior unless a stricter validation rule is clearly needed.
- Preserve runtime model override support, but make the mutable runtime state explicit instead of mutating a loose module variable.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- src/config.py
- src/history.py
- src/bot.py
- src/llm.py
- src/summarizer.py
- src/agent/core.py
- src/agent/tools.py

## Risks / Dependencies
- Runtime code currently expects config values to be importable as plain globals.
- Refactoring config access will touch many files and should happen before wider service extraction.

## Validation Steps
1. Start the app with a valid `.env` and verify settings load successfully.
2. Start the app with invalid numeric or boolean settings and verify errors are explicit and actionable.
3. Confirm dependent modules read values through the new settings layer without import-order issues.

## Follow-ups (optional)
- Add environment variable documentation comments or a generated settings reference.
