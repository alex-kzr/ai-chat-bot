# SR-02 - Move source modules to src/

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Relocate all executable source files from the project root into the `src/` package directory.

## Context
After SR-01 creates the `src/` package, the five source modules need to be physically moved. Imports will be broken after this step and will be fixed in SR-03.

## Requirements
- Move `config.py` → `src/config.py`
- Move `prompts.py` → `src/prompts.py`
- Move `llm.py` → `src/llm.py`
- Move `handlers.py` → `src/handlers.py`
- Move `bot.py` → `src/bot.py`
- Remove the original files from the project root

## Implementation Notes
- Use `git mv` to preserve file history
- After this step the bot will not yet run (imports are broken) — that is expected and fixed in SR-03

## Definition of Done
- [ ] All five files exist under `src/`
- [ ] Original root-level files are removed
- [ ] `src/__init__.py` is still present

## Affected Files / Components
- `config.py` → `src/config.py`
- `prompts.py` → `src/prompts.py`
- `llm.py` → `src/llm.py`
- `handlers.py` → `src/handlers.py`
- `bot.py` → `src/bot.py`

## Risks / Dependencies
- Depends on SR-01 (src/ package must exist)
- Bot will be non-functional until SR-03 is complete

## Validation Steps
1. Confirm each file exists under `src/`
2. Confirm root-level originals are gone
3. (Imports will be fixed in SR-03)

## Follow-ups (optional)
- SR-03: Fix internal imports
