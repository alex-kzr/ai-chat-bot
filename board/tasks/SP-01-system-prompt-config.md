# SP-01 - Move SYSTEM_PROMPT to config.py

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Centralise the system prompt in `src/config.py` so it can be overridden via environment variables without editing source code. Remove the duplicate constant from `src/prompts.py`.

## Context
`SYSTEM_PROMPT` is currently hardcoded in `src/prompts.py` and imported directly into `src/llm.py`. All other runtime constants (model name, URL, timeouts, history limits) live in `src/config.py`. This task aligns system prompt configuration with that pattern.

## Requirements
- Add `SYSTEM_PROMPT: str` to `src/config.py`, read from the `SYSTEM_PROMPT` environment variable with a default of `"You are a helpful assistant. Answer clearly and concisely in the user's language."`
- Add `SYSTEM_PROMPT_ENABLED: bool` to `src/config.py`, read from the `SYSTEM_PROMPT_ENABLED` env var (default `True`)
- Remove the `SYSTEM_PROMPT` constant from `src/prompts.py`

## Implementation Notes
- Use `os.environ.get("SYSTEM_PROMPT", "...")` for the string constant
- Use `os.environ.get("SYSTEM_PROMPT_ENABLED", "true").lower() == "true"` for the boolean flag
- `src/prompts.py` should retain `ERROR_PHRASES` and `SUMMARIZATION_PROMPT`; only `SYSTEM_PROMPT` is moved

## Definition of Done
- [ ] `src/config.py` contains `SYSTEM_PROMPT` and `SYSTEM_PROMPT_ENABLED`
- [ ] `src/prompts.py` no longer defines `SYSTEM_PROMPT`
- [ ] No other file imports `SYSTEM_PROMPT` from `src/prompts`
- [ ] Code is clean and consistent

## Affected Files / Components
- `src/config.py`
- `src/prompts.py`

## Risks / Dependencies
- SP-02 depends on this task (it updates the import in `src/llm.py`)

## Validation Steps
1. Open `src/config.py` and confirm `SYSTEM_PROMPT` and `SYSTEM_PROMPT_ENABLED` are present
2. Start the bot with default env → confirm startup succeeds
3. Set `SYSTEM_PROMPT="Test prompt"` in env, restart, send a message → confirm new prompt is used

## Follow-ups (optional)
- Support loading the system prompt from an external file path via env var
