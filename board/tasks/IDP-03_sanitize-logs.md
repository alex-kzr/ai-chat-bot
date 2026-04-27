# IDP-03 - Sanitize secrets in logs

## Status
- [ ] To Do
- [ ] In Progress
- [ ] Done

## Purpose
Prevent secrets pasted by users (or surfaced by tools) from being written to console or file logs. The current code logs raw message text in `src/handlers.py` (`logging.info(">>> %s: %s", user_display, message.text)`) and also logs full LLM input/output context in `src/context_logging.py`. A user who pastes a Telegram bot token, API key, OAuth bearer, or `Authorization: Bearer …` snippet into the chat will leak it to the operator's logs.

## Context
- `src/handlers.py` — user-facing log lines.
- `src/context_logging.py` — `extract_context`, `serialize_messages`, `log_agent_event` (used by the agent loop and chat service).
- Settings already gate logging destinations and formats; the sanitizer should run regardless of destination.

## Requirements
- Add a `sanitize_log_data(value)` helper that:
  - Masks Telegram bot tokens (`\d{8,10}:[A-Za-z0-9_-]{30,}`).
  - Masks generic API keys (long base64-ish or hex strings, common prefixes like `sk-`, `ghp_`, `xox[abp]-`).
  - Masks `Authorization: Bearer …` and `Authorization: Basic …` headers.
  - Masks `Cookie:` and `Set-Cookie:` values.
  - Walks dicts/lists recursively so structured logs are also sanitized.
- Replacement format: `[REDACTED:<kind>]` so operators see something happened without seeing the secret.
- Use the helper in:
  - `src/handlers.py` user-text log lines.
  - `src/context_logging.serialize_messages` (sanitize each message's `content`).
  - `src/context_logging.log_agent_event` (sanitize `**fields`).
- Never log the raw `bot_token` from settings under any condition.

## Implementation Notes
- Place the helper in a new module `src/security/log_sanitizer.py`.
- Keep regexes conservative: false positives are better than leaks. Add a unit-tested allowlist of known-safe patterns if needed.
- Avoid logging full prompts at INFO; downgrade verbose payload dumps to DEBUG (operators can opt in).

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] `sanitize_log_data()` handles strings, dicts, and lists.
- [ ] Bot tokens, API keys, bearer headers, and cookie values are masked.
- [ ] Handler log line uses the sanitizer.
- [ ] Context/agent structured logs use the sanitizer.
- [ ] Tests cover each redaction category and confirm non-secret strings pass through unchanged.

## Affected Files / Components
- New: `src/security/log_sanitizer.py`
- `src/handlers.py`
- `src/context_logging.py`
- `tests/test_security_log_sanitizer.py` (new)

## Risks / Dependencies
- Over-aggressive regexes may mangle legitimate messages — keep them targeted and unit-tested.
- Performance: sanitizer runs on every message. Keep it linear in input size and avoid catastrophic regex backtracking (no nested quantifiers without anchors).

## Validation Steps
1. Send a message containing a fake Telegram bot token (`123456789:AAFakeFakeFakeFakeFakeFakeFakeFakeFAKE`). Verify console log shows `[REDACTED:telegram_bot_token]`.
2. Send a message with `Authorization: Bearer abc.def.ghi`. Verify the bearer is masked.
3. Send an ordinary message — content is logged unchanged.
4. Trigger an agent run that fetches an HTML page containing `Set-Cookie:` and confirm the structured agent log masks it.

## Follow-ups (optional)
- Add an allowlist mode for projects that want to disable sanitization in dev environments.
