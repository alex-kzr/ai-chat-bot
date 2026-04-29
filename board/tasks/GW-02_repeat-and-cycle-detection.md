# GW-02 - Detect repeated outputs and cyclic agent states

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Stop the agent when the model keeps producing the same answer, reasoning pattern, or state transition instead of making progress.

## Context
The prompt explicitly calls out repeated text, repeated JSON, repeated reasoning blocks, and cyclic states as failure modes. The current loop can stop on `max_steps`, but it needs earlier detection for cases where the agent is obviously stuck.

## Requirements
- Detect identical or near-identical answers across consecutive turns.
- Detect repeated reasoning blocks or recurring state signatures inside the loop.
- Abort with a controlled error once repeat or cycle thresholds are exceeded.

## Implementation Notes
- Add a small loop-state tracker in `src/agent/core.py` that records recent outputs, parsed actions, and state signatures.
- Use deterministic comparison first; add semantic similarity only if it can be kept simple and testable.
- Make the thresholds configurable through the safety settings introduced in `GW-01`.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Consecutive repeated answers are detected
- [x] Cyclic state transitions are detected before full step exhaustion
- [x] Controlled termination includes a specific repeat/cycle reason
- [x] Code is clean and consistent
- [x] Documentation is updated where needed

## Affected Files / Components
- `src/agent/core.py`
- `src/agent/parser.py`
- `docs/algorithms.md`

## Risks / Dependencies
- Dependency: `GW-01` defines repeat thresholds and stop-reason contracts.
- Risk: overly strict similarity rules could abort legitimate iterative reasoning.

## Validation Steps
1. Simulate repeated identical final-answer candidates and confirm the run aborts.
2. Simulate alternating repeated tool/observation states and confirm cycle detection triggers.
3. Verify normal multi-step agent runs still complete successfully.

## Follow-ups (optional)
- Introduce richer semantic similarity once a simple deterministic baseline is stable.
