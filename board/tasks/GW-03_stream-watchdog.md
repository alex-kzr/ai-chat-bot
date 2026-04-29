# GW-03 - Add stream watchdog and timeout aborts

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Ensure streaming generation cannot hang forever when chunks stop changing or the provider never closes the stream.

## Context
The prompt requires a watchdog that aborts if the stream stalls, repeats chunks excessively, or never terminates. The chatbot already streams through the shared LLM transport path, so the watchdog must integrate with the gateway and agent loop without being tied to one provider.

## Requirements
- Abort when no new stream content arrives within the configured timeout.
- Abort when identical chunks or tokens repeat beyond a threshold.
- Surface watchdog aborts as controlled runtime failures with deterministic cleanup.

## Implementation Notes
- Review the streaming boundary in `src/ollama_gateway.py` and any agent-side consumption path.
- Keep the timeout handling centralized so both response-level and stream-level aborts are distinguishable.
- Preserve partial diagnostics for failed streams without leaking incomplete output to the user.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Non-terminating streams are aborted reliably
- [x] Repeated chunk loops are detected
- [x] Stream cleanup does not leave dangling tasks or ambiguous state
- [x] Code is clean and consistent
- [x] Documentation is updated where needed

## Affected Files / Components
- `src/ollama_gateway.py`
- `src/agent/core.py`
- `src/modules/chat/service.py`

## Risks / Dependencies
- Dependency: `GW-01` supplies timeout configuration and stop reasons.
- Risk: watchdog timing must not break legitimate slow local-model responses.

## Validation Steps
1. Simulate a stream that stops emitting new chunks and confirm timeout abort.
2. Simulate duplicated chunk delivery and confirm the watchdog stops the run.
3. Verify successful streams still return a final result without extra latency.

## Follow-ups (optional)
- Consider a dedicated watchdog helper if the logic needs to be shared across chat and agent paths.
