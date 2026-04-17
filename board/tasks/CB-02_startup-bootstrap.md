# CB-02 - Refactor startup and model selection flow

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make application startup predictable by separating synchronous bootstrap work from async bot runtime and removing hidden mutation from model selection.

## Context
`src/bot.py` currently performs model discovery with `httpx`, uses `print`, and calls blocking `input()` inside an async function. It also mutates `config.OLLAMA_MODEL` at runtime. The docs and legacy warnings already call this out as a design smell.

## Requirements
- Move blocking console interaction out of async code.
- Define a clear bootstrap path that loads settings, optionally resolves the active model, and then starts polling.
- Make runtime model selection explicit in a runtime state object or dependency container.

## Implementation Notes
- Keep operator-facing model selection behavior, but isolate it from the main event loop.
- Separate “discover available models” from “choose active model” so both can be tested independently.
- Ensure startup failures use structured logging rather than ad hoc `print` fallbacks.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- main.py
- src/bot.py
- src/config.py
- src/llm.py
- docs/usage-guide.md

## Risks / Dependencies
- Depends on CB-01 because bootstrap should receive a constructed settings object.
- Startup refactor may affect local operator workflow and must preserve existing usability.

## Validation Steps
1. Run the bot locally and verify model selection still works before polling starts.
2. Simulate unavailable Ollama and verify startup degrades gracefully with clear logs.
3. Confirm no blocking console calls remain inside async functions.

## Follow-ups (optional)
- Add a non-interactive mode for CI or service deployment.
