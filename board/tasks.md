# 📋 Tasks — Security Hardening
---

## Phase 1 — Tool & SSRF Hardening

### TSH-01 Block private and metadata targets in http_request
Add an SSRF guard to `src/agent/tools.py` that rejects URLs whose resolved host is loopback (127.0.0.0/8, ::1), private RFC1918, link-local (169.254.0.0/16 — including the cloud metadata endpoint 169.254.169.254), or otherwise non-public, both before the initial request and on every redirect hop.
→ [TSH-01_block-private-targets-in-http-request.md](./tasks/TSH-01_block-private-targets-in-http-request.md)

### TSH-02 Validate tool-call arguments with explicit schemas
Add deterministic argument validation in the agent loop so each tool's `args_schema` is enforced before `run()` is called. Reject unknown tools, unknown keys, and wrong types with a structured `[tool_error]` observation instead of letting the tool see arbitrary input.
→ [TSH-02_validate-tool-arguments.md](./tasks/TSH-02_validate-tool-arguments.md)

### TSH-03 Optional outbound domain allowlist for http_request
Introduce an optional comma-separated `AGENT_TOOL_HTTP_DOMAIN_ALLOWLIST` setting; when configured, `http_request` only contacts hosts in the list. Empty/unset preserves current open-Internet behavior for development.
→ [TSH-03_http-tool-domain-allowlist.md](./tasks/TSH-03_http-tool-domain-allowlist.md)

## Phase 2 — Input & DoS Protection

### IDP-01 Enforce maximum user input length
Add `MAX_USER_INPUT_CHARS` to settings and reject Telegram messages and `/agent` tasks longer than the limit with a polite reply. Prevents prompt-stuffing DoS and runaway token cost.
→ [IDP-01_max-user-input-length.md](./tasks/IDP-01_max-user-input-length.md)

### IDP-02 Per-user rate limiting
Add a lightweight in-memory rate limiter (token-bucket or fixed-window) keyed by Telegram user id. Configurable via `RATE_LIMIT_REQUESTS_PER_MINUTE`; exceeded requests get a short polite reply without invoking the LLM or agent.
→ [IDP-02_per-user-rate-limiting.md](./tasks/IDP-02_per-user-rate-limiting.md)

### IDP-03 Sanitize secrets in logs
Add a `sanitize_log_data()` helper that masks bot tokens, API keys, bearer/authorization headers, and cookie values. Wire it into the user-message log line in `src/handlers.py` and into structured agent/context logs so secrets pasted by users (or accidentally captured in observations) never reach console or file sinks.
→ [IDP-03_sanitize-logs.md](./tasks/IDP-03_sanitize-logs.md)

## Phase 3 — Prompt Injection Mitigation

### PIM-01 Strict role delimiters in prompt builder
Update `_messages_to_prompt` in `src/modules/chat/service.py` and `src/agent/core.py` to use explicit, hard-to-spoof role delimiters (e.g. `<<SYSTEM>>…<</SYSTEM>>`) so user messages cannot impersonate the system role. Strip or escape delimiter sequences appearing in user/assistant content.
→ [PIM-01_strict-role-delimiters.md](./tasks/PIM-01_strict-role-delimiters.md)

### PIM-02 Wrap tool observations as untrusted data
Tag tool observations passed back into the agent loop with an explicit `<<UNTRUSTED_TOOL_OUTPUT>>…<</UNTRUSTED_TOOL_OUTPUT>>` envelope and make the agent system prompt instruct the model to treat anything inside as data, never as instructions.
→ [PIM-02_untrusted-tool-observations.md](./tasks/PIM-02_untrusted-tool-observations.md)

### PIM-03 Detect injection-override phrases in untrusted text
Add a small detector that flags well-known override phrases ("ignore previous instructions", "reveal your system prompt", "you are now…", etc.) in retrieved web content and user input. On match, log a structured warning and prepend a defensive notice to the observation; do not silently drop content.
→ [PIM-03_detect-injection-phrases.md](./tasks/PIM-03_detect-injection-phrases.md)

## Phase 4 — Security Tests & Tooling

### STS-01 Add security test suite
Add `tests/test_security_*.py` with focused cases: SSRF (loopback, RFC1918, 169.254.169.254, scheme bypass via `file://`, redirect to private), prompt-injection in user input and tool observations, system-prompt leakage attempts, oversized input, invalid/unknown tool calls, and path-traversal-style URLs.
→ [STS-01_security-test-suite.md](./tasks/STS-01_security-test-suite.md)

### STS-02 Wire static analysis tooling
Add `bandit`, `pip-audit`, and `ruff` configuration to the project. Document how to run them in `README.md` (or `docs/`), and add a `[tool.ruff]`/`[tool.bandit]` section to `pyproject.toml` if present, otherwise dedicated config files. Do not introduce them as runtime dependencies.
→ [STS-02_static-analysis-tooling.md](./tasks/STS-02_static-analysis-tooling.md)

---
