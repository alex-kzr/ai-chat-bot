# SR-03 - Update internal imports in src/ modules

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Fix all `import` statements inside the moved modules so they resolve correctly within the `src/` package.

## Context
After SR-02, the modules are in `src/` but still import each other using bare names (e.g., `from llm import ask_llm`, `import config`). These bare names no longer resolve from inside a package — they must become relative imports.

## Requirements
- In `src/handlers.py`: change `from llm import ask_llm` → `from .llm import ask_llm`
- In `src/llm.py`: change `import config` → `from . import config`; change `from prompts import ...` → `from .prompts import ...`
- In `src/bot.py`: change `import config` → `from . import config`; change `from handlers import router` → `from .handlers import router`
- `src/config.py` and `src/prompts.py` have no intra-package imports — no changes needed

## Implementation Notes
- Use relative imports (`.module`) — they work regardless of how the package is installed or run
- Do not change any logic, only import lines

## Definition of Done
- [ ] All intra-package imports use relative syntax
- [ ] `python -c "from src import bot"` runs without ImportError
- [ ] No logic changes introduced

## Affected Files / Components
- `src/bot.py`
- `src/handlers.py`
- `src/llm.py`

## Risks / Dependencies
- Depends on SR-02 (files must be in src/)

## Validation Steps
1. Run `python -c "from src import bot"` — no ImportError
2. Run `python -c "from src.llm import ask_llm"` — no ImportError
3. Run `python -c "from src.handlers import router"` — no ImportError

## Follow-ups (optional)
- SR-04: Provide root-level entry point
