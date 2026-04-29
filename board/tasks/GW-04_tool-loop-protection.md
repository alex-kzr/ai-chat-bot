# GW-04 - Prevent infinite tool-call retries

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Prevent the agent from calling the same tool forever with unchanged inputs or meaningless retry cycles.

## Context
The prompt identifies repeated tool calls and missing retry justification as core agent-loop failures. The current loop executes parsed tool calls, but it needs stronger policy checks before allowing the same action to repeat indefinitely.

## Requirements
- Detect identical consecutive tool calls, including unchanged arguments.
- Require retries to carry changed arguments or a clear retry reason in the loop state.
- Stop the run with a controlled failure after the configured tool retry limit is exceeded.

## Implementation Notes
- Track recent tool call signatures in `src/agent/core.py`.
- Keep tool-loop policy generic so it works for every registered tool in `src/agent/tools.py`.
- Decide whether retry justification belongs in parser output, loop metadata, or an internal policy layer, and keep the contract simple.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Identical tool-call retries are bounded
- [x] Legitimate changed-input retries remain possible
- [x] Controlled termination clearly identifies tool-loop exhaustion
- [x] Code is clean and consistent
- [x] Documentation is updated where needed

## Affected Files / Components
- `src/agent/core.py`
- `src/agent/tools.py`
- `docs/architecture.md`

## Risks / Dependencies
- Dependency: `GW-01` provides retry thresholds and stop reasons.
- Risk: overly rigid checks could block valid retry flows after transient tool failures.

## Validation Steps
1. Force repeated identical tool calls and confirm the run aborts.
2. Force a retry with changed arguments and confirm it is allowed.
3. Verify unknown-tool and tool-error paths still behave deterministically.

## Follow-ups (optional)
- Add per-tool retry policies if different tools need different thresholds later.
