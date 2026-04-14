# SR-04 - Update project entry point

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide a clean root-level entry point so users can start the bot with a simple command from the project root.

## Context
After SR-02/SR-03, `src/bot.py` contains `main()` but users previously ran `python bot.py` from the root. That file no longer exists. A thin launcher at the root restores the familiar invocation pattern.

## Requirements
- Create `main.py` at the project root
- `main.py` must import `asyncio` and `src.bot.main`, then call `asyncio.run(main())`
- Update `README.md` run command from `python bot.py` to `python main.py`

## Implementation Notes
- `main.py` should be minimal — no logic, just delegation:
  ```python
  import asyncio
  from src.bot import main

  if __name__ == "__main__":
      try:
          asyncio.run(main())
      except KeyboardInterrupt:
          pass
  ```
- README update is part of this task's DoD

## Definition of Done
- [ ] `main.py` exists at project root
- [ ] `python main.py` starts the bot without errors
- [ ] `README.md` updated to reference `python main.py`
- [ ] No logic duplicated — `main.py` only delegates to `src.bot`

## Affected Files / Components
- `main.py` (new file)
- `README.md`

## Risks / Dependencies
- Depends on SR-03 (imports must be working inside src/)

## Validation Steps
1. Run `python main.py` — bot starts, prints startup log
2. Bot connects to Telegram and responds to `/start`
3. `Ctrl+C` shuts down cleanly

## Follow-ups (optional)
- SR-05: Full end-to-end validation
