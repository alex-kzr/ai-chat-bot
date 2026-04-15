# SP-02 - Update ask_llm() to read system prompt from config

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make `ask_llm()` use the centrally-configured `SYSTEM_PROMPT` and `SYSTEM_PROMPT_ENABLED` values from `src/config.py` instead of the now-removed constant in `src/prompts.py`.

## Context
After SP-01, `SYSTEM_PROMPT` is moved to `src/config.py`. `src/llm.py` currently imports it from `src/prompts`. This task updates that import and adds a conditional check so the system message is only injected when `SYSTEM_PROMPT_ENABLED` is `True`.

## Requirements
- Replace `from .prompts import SYSTEM_PROMPT, ERROR_PHRASES` with `from .prompts import ERROR_PHRASES`
- Read `config.SYSTEM_PROMPT` and `config.SYSTEM_PROMPT_ENABLED` inside `ask_llm()`
- Only build the `{"role": "system", "content": config.SYSTEM_PROMPT}` entry when `config.SYSTEM_PROMPT_ENABLED` is `True`

## Implementation Notes
- Build the `system_messages` list conditionally before constructing `payload["messages"]`
- Keep the existing history-appending logic untouched

## Definition of Done
- [ ] `src/llm.py` no longer imports `SYSTEM_PROMPT` from `src/prompts`
- [ ] System message is injected only when `SYSTEM_PROMPT_ENABLED` is `True`
- [ ] Bot starts and responds correctly with default config
- [ ] Code is clean and consistent

## Affected Files / Components
- `src/llm.py`

## Risks / Dependencies
- Depends on SP-01 (config constants must exist first)

## Validation Steps
1. Start the bot → send a message → confirm response is normal (system prompt active)
2. Set `SYSTEM_PROMPT_ENABLED=false`, restart → confirm system message is absent in logged payload
3. Set a custom `SYSTEM_PROMPT`, restart → confirm logged payload reflects the custom prompt

## Follow-ups (optional)
- None
