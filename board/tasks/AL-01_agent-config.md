# AL-01 - Add agent config constants

## Status

* [ ] To Do
* [ ] In Progress
* [x] Done

## Purpose

Centralize all agentic loop settings in `src/config.py` so that model parameters, step limits, and timeouts can be overridden via environment variables without code changes.

## Context

All runtime constants already live in `src/config.py` (e.g., `OLLAMA_MODEL`, `MAX_HISTORY_MESSAGES`). The agentic loop requires its own constants, isolated from the main chatbot.

## Requirements

* `AGENT_MAX_STEPS: int` (default `8`, range 5–10) — hard limit for loop iterations.
* `AGENT_MODEL: str` (default `"qwen3:4b"`) — Ollama model for the agent; may differ from `OLLAMA_MODEL`.
* `AGENT_TEMPERATURE: float` (default `0.2`) — low temperature for deterministic JSON output.
* `AGENT_TOOL_TIMEOUT: int` (default `30`) — timeout in seconds for tool calls (separate from `OLLAMA_TIMEOUT`).
* All four constants must be overridable via environment variables with the same names.
* On invalid value — log a warning and use the default.

## Implementation Notes

* Follow the existing pattern in `src/config.py` (`os.getenv(...)` with type casting and defaults).
* Use helper functions `_parse_*` for safe type casting (already exists for `AGENT_MAX_STEPS` and `AGENT_TEMPERATURE`).
* Add `AGENT_TOOL_TIMEOUT` аналогично `AGENT_TEMPERATURE`.

## Definition of Done

* [x] All 4 constants are present in `src/config.py` with correct types and defaults
* [x] Overriding via env vars is manually verified
* [x] No regressions in existing modules depending on config
* [x] Code is clean and consistent with surrounding style

## Affected Files / Components

* `src/config.py`

## Risks / Dependencies

* None — purely additive change.

## Validation Steps

1. `python -c "from src import config; print(config.AGENT_MAX_STEPS, config.AGENT_MODEL, config.AGENT_TEMPERATURE, config.AGENT_TOOL_TIMEOUT)"` — defaults match.
2. `AGENT_MAX_STEPS=5 python -c "from src import config; print(config.AGENT_MAX_STEPS)"` → `5`.
3. `AGENT_MAX_STEPS=abc python -c "from src import config"` → warning in logs, value `8`.
4. Run the bot — no startup errors.
