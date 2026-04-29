# GW-01 - Define runtime safety settings and stop reasons

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Establish one shared set of safety limits so every agent run has deterministic upper bounds and clear stop reasons.

## Context
The prompt requires hard limits for steps, retries, repeated answers, repeated tool calls, response length, and both request and stream timeouts. The current runtime already exposes `max_steps`, but the remaining protections need to be promoted into explicit settings and surfaced in the agent result model.

## Requirements
- Add typed settings or constants for all required loop-safety limits.
- Extend the agent result / stop-reason contract to represent each controlled termination path.
- Keep the configuration model backend-agnostic so the same settings work with Ollama and other OpenAI-compatible runtimes.

## Implementation Notes
- Update `src/config.py` with runtime safety settings and defaults.
- Extend `src/agent/core.py` result metadata so callers can distinguish `max_steps`, `repeat_detected`, `tool_loop`, `stream_timeout`, `parser_retry_exhausted`, and related cases.
- Reuse existing typed configuration patterns rather than introducing ad-hoc module globals.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] All safety limits are configurable from one runtime contract
- [x] Agent termination reasons are explicit and machine-readable
- [x] Existing agent callers continue to work with the expanded result model
- [x] Code is clean and consistent
- [x] Documentation is updated where needed

## Affected Files / Components
- `src/config.py`
- `src/agent/core.py`
- `src/runtime.py`

## Risks / Dependencies
- Dependency: existing agent result consumers may assume a smaller stop-reason set.
- Risk: inconsistent defaults could make the agent too aggressive or too permissive if not calibrated centrally.

## Validation Steps
1. Inspect the runtime configuration and confirm all required loop-safety limits exist.
2. Run an agent scenario that hits a limit and confirm the stop reason is explicit.
3. Verify the result contract remains consumable by the Telegram-facing orchestrator.

## Follow-ups (optional)
- Add per-environment overrides once the defaults stabilize in real usage.
