# IDP-02 - Per-user rate limiting

## Status
- [ ] To Do
- [ ] In Progress
- [ ] Done

## Purpose
Stop a single Telegram user from monopolizing the local LLM or agent loop. The bot has no authentication, no per-user accounting, and the agent loop can run multiple expensive HTTP fetches per request — a single abusive client can degrade service for everyone.

## Context
- Handlers: `src/handlers.py` (`handle_text`, `handle_agent`).
- Users module: `src/modules/users` (already gives a stable `user_id`).
- Runtime container: `src/runtime.py` is the right place to construct and share the limiter instance.

## Requirements
- Add settings:
  - `RATE_LIMIT_REQUESTS_PER_MINUTE` (default e.g. 20, min 1).
  - `RATE_LIMIT_BURST` (default 5).
- Implement an in-memory token-bucket (or fixed-window) limiter keyed by Telegram user id, accessible via the runtime container.
- When a user exceeds the limit, reply with a short polite cool-down message and do not call the LLM/agent or modify history.
- Limiter must be thread/async safe (use `asyncio.Lock` or atomic operations).

## Implementation Notes
- Keep it stdlib-only — no `aiolimiter` or similar.
- Do not log full message content for rate-limit hits; log only `user_id` and the limiter state.
- Apply the limit before TSH-02 / IDP-01 checks so abusive callers cannot burn validation cycles either.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Settings added, validated, and documented in `.env.example`.
- [ ] Limiter wired through `Runtime` and used by both handlers.
- [ ] Exceeding the limit blocks the LLM/agent call and replies with a cool-down message.
- [ ] Limit is per-user, not global.
- [ ] Tests cover under-limit, at-limit, and over-limit behavior across two distinct users.

## Affected Files / Components
- `src/config.py`
- `src/runtime.py`
- `src/handlers.py`
- New module: `src/security/rate_limiter.py` (or `src/services/rate_limiter.py`)
- `tests/test_security_rate_limit.py` (new)

## Risks / Dependencies
- In-memory state resets on restart — acceptable for the current modular monolith (matches history's in-memory model).
- Avoid introducing a new shared global; route through `Runtime`.

## Validation Steps
1. From one user, send `RATE_LIMIT_REQUESTS_PER_MINUTE` messages quickly — all processed.
2. Send the next message immediately — receives cool-down reply, no LLM call (verify via test double / logs).
3. Send a message from a different user — processed normally.

## Follow-ups (optional)
- Add a stricter limit for `/agent` since each agent run can chain many tool calls.
