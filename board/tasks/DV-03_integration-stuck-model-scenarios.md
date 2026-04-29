# DV-03 - Add integration scenarios for stuck-model failures

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Prove the full runtime behaves safely when a scripted model reproduces the exact infinite-loop failures described in the prompt.

## Context
The prompt defines four concrete scenarios: infinite repeated text, infinite identical tool calls, malformed JSON spam, and streams that never terminate. Unit tests cover isolated mechanisms, but these end-to-end scenarios verify that the protections work together in realistic runtime flows.

## Requirements
- Add scripted integration scenarios for each required stuck-model failure mode.
- Assert that each scenario aborts cleanly with the expected stop reason and controlled user-facing outcome.
- Verify diagnostics are present so the failure can be investigated after the run.

## Implementation Notes
- Build the scenarios on top of existing fake gateway / runtime scaffolding where possible.
- Keep the tests deterministic and offline; no real model backends or Telegram traffic.
- Focus assertions on termination behavior, retries, and diagnostics rather than on exact incidental log formatting.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Repeated-text loop scenario aborts correctly
- [ ] Repeated-tool loop scenario aborts correctly
- [ ] Malformed-JSON spam scenario aborts correctly
- [ ] Non-terminating stream scenario aborts correctly
- [ ] Code is clean and consistent

## Affected Files / Components
- `tests/`
- `src/agent/core.py`
- `src/ollama_gateway.py`

## Risks / Dependencies
- Dependency: `DV-02` and the runtime seams from earlier tasks make these scenarios practical to script.
- Risk: integration fixtures that are too coarse may become brittle if they encode internal implementation details.

## Validation Steps
1. Run the integration scenarios and confirm each one terminates with a controlled stop reason.
2. Check that no scenario hangs or requires manual interruption.
3. Verify logs or collected diagnostics include enough detail to explain the stop.

## Follow-ups (optional)
- Add provider-specific regression fixtures later if a real backend exposes a unique stuck pattern.
