# IDP-01 - Enforce maximum user input length

## Status
- [ ] To Do
- [ ] In Progress
- [ ] Done

## Purpose
Cap user-supplied text at a known size before it reaches the LLM, the agent, or history storage. Without a cap, an attacker can submit megabytes of text per message and force the bot to spend tokens, time, and memory — a cheap denial-of-service.

## Context
- Telegram entry points: `src/handlers.py` (`handle_text`, `handle_agent`).
- Telegram already caps inbound messages at 4096 chars per message, but a single user can chain many large messages, and `/agent <task>` strips the command leaving the rest unbounded.
- History service appends every user turn (`ConversationService.append_message`) — long messages also bloat token counts (see `src/context_logging.count_context_tokens`).

## Requirements
- Add a setting `MAX_USER_INPUT_CHARS` (default e.g. 4000, min 100) in `src/config.py`.
- In handlers, if `message.text` (or the `/agent` task body) exceeds the cap, reply with a polite error and skip the LLM/agent invocation entirely.
- Do not append the rejected message to history.
- Apply the same limit to the `/agent` task body separately so users cannot bypass with `/agent <huge>`.

## Implementation Notes
- Validate after stripping leading/trailing whitespace.
- Keep the rejection message short and language-agnostic so it does not require translations.
- Log a structured warning so operators can tune the limit.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] `MAX_USER_INPUT_CHARS` setting added, validated, and documented in `.env.example`.
- [ ] `handle_text` and `handle_agent` reject oversized input with a polite reply.
- [ ] Rejected messages are not added to conversation history.
- [ ] Tests cover at-limit (accepted) and over-limit (rejected) cases.

## Affected Files / Components
- `src/config.py`
- `src/handlers.py`
- `.env.example`
- `tests/test_security_input_limits.py` (new)

## Risks / Dependencies
- Default limit must be generous enough that normal chat is unaffected.

## Validation Steps
1. Send a message of `MAX_USER_INPUT_CHARS - 1` chars — must be processed normally.
2. Send a message of `MAX_USER_INPUT_CHARS + 1` chars — must receive the polite rejection and not appear in history (verify via `ConversationService.get_history`).
3. Repeat with `/agent` and a huge task body.

## Follow-ups (optional)
- Consider limiting per-conversation cumulative size, not just per-message.
