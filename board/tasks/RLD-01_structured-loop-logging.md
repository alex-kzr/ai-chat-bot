# RLD-01 - Add deterministic structured logging for loop and tool calls

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make every agent run traceable so loop decisions and tool executions can be debugged and analyzed after the fact.

## Context
The prompt explicitly requires all tool interactions to be deterministic and logged. The project already has logging utilities, but the agent loop needs stronger structure and correlation across steps.

## Requirements
- Log every loop step with step index, branch type, and outcome.
- Log every tool call with tool name, arguments or a safe summary, duration, and status.
- Use a consistent log format that supports correlation across one agent run.

## Implementation Notes
- Add or extend a shared logging helper for the agent runtime.
- Redact or summarize sensitive request data where needed.
- Include a run identifier so multi-step traces remain easy to follow.

## Definition of Done
- [ ] Loop steps are logged in a consistent structured format
- [ ] Tool calls are logged with outcome and timing
- [ ] One agent run can be traced end to end in logs
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/core.py`
- `src/agent/tools.py`
- `src/context_logging.py`

## Risks / Dependencies
- Dependency: `LC-02` and `HT-03` define the execution flow worth logging.
- Risk: overly verbose logs may add noise or leak too much request detail if not summarized carefully.

## Validation Steps
1. Run a multi-step agent task and confirm every loop iteration is visible in logs.
2. Check both successful and failed tool calls for timing and status fields.
3. Confirm all records from one run can be correlated with a shared identifier.

## Follow-ups (optional)
- Add an optional JSON log mode for downstream analysis.
