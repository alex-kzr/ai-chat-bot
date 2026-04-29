# DV-01 - Add structured loop diagnostics and watchdog telemetry

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make loop-protection failures easy to diagnose by recording what the model produced, how the runtime interpreted it, and why execution stopped.

## Context
The prompt requires logging of prompts, raw LLM output, stream chunks, tool calls, loop iterations, similarity scores, parser errors, retry reasons, and the final termination reason. The project already has structured agent logging, so this task expands it specifically for the new guardrails.

## Requirements
- Log the key runtime events needed to diagnose loop and stream failures.
- Include enough structured detail to correlate prompts, outputs, retries, and stop reasons in one run.
- Keep logging safe and bounded so diagnostics do not become a new stability or privacy problem.

## Implementation Notes
- Extend `src/context_logging.py` and the agent runtime call sites rather than scattering free-form logs.
- Summarize or redact oversized payloads while still preserving the information needed for debugging.
- Align event names and fields with existing structured logging conventions in the repo.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Loop and watchdog diagnostics are emitted in structured form
- [ ] Retry reasons and termination reasons are visible in logs
- [ ] Logging remains bounded and safe for noisy model output
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/context_logging.py`
- `src/agent/core.py`
- `src/ollama_gateway.py`

## Risks / Dependencies
- Dependency: `GW-*` and `PF-*` tasks define the events and stop reasons worth logging.
- Risk: excessive raw-output logging could create oversized logs if truncation is not handled carefully.

## Validation Steps
1. Run a repeated-output failure scenario and confirm diagnostics include repeat counters and stop reason.
2. Run a parser-failure scenario and confirm raw output plus parser error metadata are logged.
3. Verify log records remain structured and bounded for long or noisy outputs.

## Follow-ups (optional)
- Add metrics or telemetry export once the event vocabulary stabilizes.
