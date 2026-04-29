# PF-02 - Enforce final-answer completion with bounded retries

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Guarantee that successful agent completion always ends in a validated `final_answer` and that invalid terminal output cannot trigger endless repair loops.

## Context
The prompt explicitly requires final-answer enforcement, controlled retries for invalid output, and termination after repeated invalid responses. The architecture already states that the user should only see the final answer, so the runtime must make that rule mechanically reliable.

## Requirements
- Accept successful completion only through a valid `final_answer`.
- Convert invalid terminal outputs into bounded controlled retries.
- Terminate with a controlled failure after repeated invalid outputs or exhausted retries.

## Implementation Notes
- Update `src/agent/core.py` retry flow to consume explicit parser outcomes from `PF-01`.
- Review the agent prompt in `src/prompts.py` if a stronger completion instruction is needed.
- Keep the user-facing contract unchanged: either a final answer or a controlled fallback.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Successful runs always end through validated `final_answer`
- [ ] Invalid terminal outputs retry only within configured bounds
- [ ] Exhausted retries produce a clear controlled stop reason
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/core.py`
- `src/prompts.py`
- `src/services/chat_orchestrator.py`

## Risks / Dependencies
- Dependency: `PF-01` must provide unambiguous parser outcomes.
- Risk: prompt changes that are too strict could reduce model flexibility on valid multi-step tasks.

## Validation Steps
1. Simulate a valid final-answer output and confirm immediate successful completion.
2. Simulate repeated invalid terminal outputs and confirm retries stop at the configured limit.
3. Verify the user still receives only one final reply or one controlled fallback message.

## Follow-ups (optional)
- Add a dedicated final-answer repair prompt if repeated near-miss outputs become common.
