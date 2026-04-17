# TM-01 - Add OLLAMA_THINK config constant

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Replace the hardcoded `"think": False` in `src/llm.py` with an env-driven config constant so thinking mode can be toggled without touching code.

## Context
When we added support for Ollama thinking models, `"think": False` was hardcoded directly in the payload dict in `src/llm.py:21`. All other tuneable parameters (`OLLAMA_MODEL`, `OLLAMA_URL`, `OLLAMA_TIMEOUT`) live in `src/config.py`. This task brings `think` into alignment with that pattern.

## Requirements
- Add `OLLAMA_THINK: bool` to `src/config.py`, read from the `OLLAMA_THINK` env var.
- Default must be `False` (safe for non-thinking models).
- The constant must be env-overridable (e.g. `OLLAMA_THINK=true` in `.env`).
- Remove the hardcoded `"think": False` from `src/llm.py` payload and replace with `config.OLLAMA_THINK`.

## Implementation Notes
- Use `os.getenv("OLLAMA_THINK", "false").lower() == "true"` for parsing.
- Place the constant near the other `OLLAMA_*` constants in `config.py`.
- No other files need to change in this task.

## Definition of Done
- [ ] `OLLAMA_THINK` constant exists in `src/config.py` with default `False`.
- [ ] `src/llm.py` payload uses `config.OLLAMA_THINK` instead of the literal `False`.
- [ ] Setting `OLLAMA_THINK=true` in `.env` and restarting the bot changes the flag passed to Ollama.
- [ ] No regressions in normal (non-thinking) model usage.

## Affected Files / Components
- `src/config.py`
- `src/llm.py`
- `.env.example` (add `OLLAMA_THINK=false`)

## Risks / Dependencies
- None. Pure config change.

## Validation Steps
1. Set `OLLAMA_THINK=false` in `.env`, start bot, confirm payload contains `"think": false`.
2. Set `OLLAMA_THINK=true` in `.env`, start bot, confirm payload contains `"think": true`.
3. Send a message and confirm the bot still replies correctly.
