# SR-01 - Create src/ package directory

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Establish `src/` as a proper Python package so that all source modules can be moved into it and imported using package-qualified paths.

## Context
Currently all executable modules (`bot.py`, `handlers.py`, `llm.py`, `prompts.py`, `config.py`) live in the project root. The refactoring goal is to place them under `src/` for a cleaner project layout.

## Requirements
- Create directory `src/`
- Create empty `src/__init__.py`

## Implementation Notes
- `__init__.py` can be completely empty
- No existing files should be modified in this task

## Definition of Done
- [ ] Directory `src/` exists
- [ ] File `src/__init__.py` exists (may be empty)
- [ ] No other files are modified

## Affected Files / Components
- `src/` (new directory)
- `src/__init__.py` (new file)

## Risks / Dependencies
- None — purely additive step

## Validation Steps
1. Confirm `src/` directory exists
2. Confirm `src/__init__.py` is present
3. Run `python -c "import src"` from project root — should succeed without errors

## Follow-ups (optional)
- SR-02: Move source modules into the new package
