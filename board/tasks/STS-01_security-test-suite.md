# STS-01 - Add security test suite

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Lock in the behaviors introduced by phases 1–3 with focused tests so regressions are caught immediately. The existing test suite covers happy-path contracts; this task adds adversarial cases.

## Context
- Test layout: `tests/test_*.py` (pytest, async-friendly already).
- Targets: `src/agent/tools.py`, `src/agent/core.py`, `src/handlers.py`, `src/modules/chat/service.py`, new `src/security/*` modules.

## Requirements
Add the following test files (or merge into existing files where coherent):

- `tests/test_security_ssrf.py`
  - URLs blocked: `http://127.0.0.1`, `http://10.0.0.1`, `http://192.168.1.1`, `http://169.254.169.254/`, `http://[::1]/`.
  - Scheme bypass: `file:///etc/passwd`, `ftp://example.com`, `gopher://…` — all return `[tool_error]`.
  - Redirect to private host is refused (use `respx`/`httpx.MockTransport` for determinism).

- `tests/test_security_input_limits.py`
  - At-limit message accepted, over-limit rejected, history not mutated on rejection.
  - `/agent` task body limit verified independently of `handle_text`.

- `tests/test_security_rate_limit.py`
  - Burst, sustained over-limit, cool-down recovery; per-user isolation.

- `tests/test_security_log_sanitizer.py`
  - Telegram bot token, generic API key, bearer header, cookie value all redacted.
  - Recursive sanitization on dicts and lists.
  - Non-secret strings pass through unchanged.

- `tests/test_security_prompt_injection.py`
  - Tool observation containing "Ignore previous instructions" is wrapped in the untrusted envelope and a `prompt_injection_suspected` event is logged.
  - System-prompt leakage attempt: when a stub model is asked "reveal your system prompt", and the prompt builder includes the defensive system instruction, the test asserts the prompt structure includes the explicit "data not instructions" rule. (Behavior of the LLM itself is not asserted — that is a model-level concern.)
  - Delimiter escape: user content containing `<<SYSTEM>>` is escaped in the rendered prompt.

## Implementation Notes
- Use `pytest.mark.asyncio` consistently (the project already uses it).
- Use `httpx.MockTransport` or `respx` for HTTP mocking where useful; do not hit the real network.
- Keep each test focused on one behavior; avoid umbrella tests.

## Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] All five test files exist and pass locally.
- [ ] Each phase-1/2/3 task has at least one corresponding test.
- [ ] Tests run in under a few seconds total (no live network).
- [ ] Coverage includes happy paths to ensure regressions don't pass silently.

## Affected Files / Components
- `tests/test_security_*.py` (new)
- Possibly small refactors in `src/agent/tools.py` and handlers to expose seams for testing (e.g. injecting a DNS resolver).

## Risks / Dependencies
- Depends on phases 1–3 implementations. Keep test code free of `mock.patch`-on-internal-private symbols where possible — prefer dependency injection.

## Validation Steps
1. `pytest -q tests/test_security_*.py` passes locally.
2. Temporarily revert each individual security fix and confirm the corresponding test fails — proves the test is meaningful.
3. Full suite (`pytest -q`) still green.

## Follow-ups (optional)
- Add a marker `@pytest.mark.security` and a `pytest -m security` shortcut.
