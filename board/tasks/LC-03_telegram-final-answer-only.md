# LC-03 - Enforce final-answer-only user replies

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Ensure the chatbot honours the product requirement that only the final answer is returned to the user, while intermediate reasoning stays internal.

## Context
The current agent integration exposes intermediate steps in chat for debugging, but `prompt_7_agentic_loop.xml` explicitly requires the system not to reply until `final_answer` is received.

## Requirements
- Remove user-facing streaming of intermediate tool and loop steps.
- Return only the final answer or a controlled fallback message if the loop stops early.
- Keep intermediate steps available through internal logs for debugging.

## Implementation Notes
- Update the Telegram handler integration in `src/handlers.py`.
- Keep typing indicators and cleanup behaviour correct while the loop is running.
- Make sure both direct text handling and any explicit agent entry points follow the same rule.

## Definition of Done
- [ ] Users see only the final answer or a controlled fallback
- [ ] Intermediate agent steps are no longer sent to chat
- [ ] Internal diagnostics remain available through logs
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/handlers.py`
- `src/agent/core.py`
- `docs/api.md`

## Risks / Dependencies
- Dependency: `LC-02` must provide a stable terminal result contract.
- Risk: hiding intermediate steps could reduce manual debugging clarity unless logging is strong enough.

## Validation Steps
1. Run an agent task that uses a tool and confirm the user receives only one final reply.
2. Trigger a controlled stop condition and confirm the fallback message is clean and non-technical.
3. Verify the typing indicator still stops correctly after completion or failure.

## Follow-ups (optional)
- Add a developer-only debug mode for step visibility outside normal user chats.
