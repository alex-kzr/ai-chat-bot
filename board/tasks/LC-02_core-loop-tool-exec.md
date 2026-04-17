# LC-02 - Refactor the core loop to execute tool calls until `final_answer`

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make the agent runtime follow the required iterative flow: execute tools, send the observation back to the LLM, and stop only when a final answer is produced.

## Context
The target flow is `User -> LLM -> Agent -> Tool -> Result -> LLM -> ... -> User`. The current core loop was built around an earlier contract and must be aligned with the new `tool` / `final_answer` protocol.

## Requirements
- Trigger tool execution from the `tool` field rather than the legacy action field.
- Feed each tool result back into the next LLM turn as the new observation.
- Stop the loop only on `final_answer`, `max_steps`, or a controlled terminal error.

## Implementation Notes
- Update the state transition logic in `src/agent/core.py` to use the new parser output types.
- Preserve deterministic behaviour for unknown tools and parse failures.
- Make sure the loop never returns a user-facing reply before a final answer is available.

## Definition of Done
- [ ] Tool calls are executed through the new contract
- [ ] Observations are fed back into the next LLM iteration
- [ ] The loop exits only on approved terminal conditions
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/core.py`
- `src/agent/parser.py`
- `src/agent/tools.py`

## Risks / Dependencies
- Dependency: `LC-01` must define stable parser behaviour first.
- Risk: loop regressions could break the current experimental agent path or hang until max steps.

## Validation Steps
1. Run a simple tool scenario and confirm the loop executes the tool before returning a final answer.
2. Trigger an unknown tool and confirm a deterministic tool error is fed back into the loop.
3. Force the loop to reach `AGENT_MAX_STEPS` and confirm a controlled stop path.

## Follow-ups (optional)
- Add unit tests for state transitions and stop conditions.
