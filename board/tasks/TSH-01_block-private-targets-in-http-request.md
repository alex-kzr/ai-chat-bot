# TSH-01 - Block private and metadata targets in http_request

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Prevent server-side request forgery (SSRF) through the agent's `http_request` tool. Without a guard, an attacker can ask the bot to fetch internal services, the cloud metadata endpoint (169.254.169.254), or loopback addresses — exfiltrating credentials, scanning the internal network, or pivoting from a public-looking URL via redirects.

## Context
- Tool implementation: `src/agent/tools.py` (`http_request`, `_normalize_url`, `_fetch_text`)
- `httpx.AsyncClient` is constructed with `follow_redirects=settings.agent.tools.follow_redirects` — currently enabled by default, so even if the original URL is public, redirects to private hosts are unchecked.
- Linked-resource loading (`_load_resources`) already enforces same-origin, but the initial fetch and its redirects do not.
- Settings live in `src/config.py` (`AgentToolSettings`).

## Requirements
- Reject URLs whose resolved host is in any of:
  - Loopback: 127.0.0.0/8, ::1
  - Private RFC1918: 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16
  - Link-local: 169.254.0.0/16 (must include 169.254.169.254 cloud metadata)
  - Unique-local IPv6: fc00::/7
  - Multicast and reserved ranges
  - Hosts that resolve only to such IPs after DNS lookup
- Re-validate every redirect target with the same checks (do not rely on `follow_redirects=True` blindly).
- Restrict schemes strictly to `http` and `https` (already partially enforced — keep and strengthen).
- Return a deterministic `[tool_error] blocked_target: <reason>` observation; never raise to the user.

## Implementation Notes
- Use `ipaddress.ip_address` against the resolved host. For hostnames, perform DNS resolution (e.g. `socket.getaddrinfo`) and check every returned address; if any is private/loopback/link-local, refuse.
- The cleanest place to enforce redirects is to disable `httpx`'s automatic redirects for the initial fetch and the resource fetch, then implement a small bounded redirect loop that re-validates each `Location` header (cap at e.g. 5 hops).
- Keep DNS lookups inside the existing async client (use `asyncio.get_running_loop().getaddrinfo`) so timeouts still apply.
- No new heavy dependencies — `ipaddress` and `socket` are stdlib.

## Testing
- [x] Unit tests
- [x] Integration tests
- [x] Manual testing

## Definition of Done
- [x] SSRF guard applied to initial fetch and every redirect hop.
- [x] Loopback, RFC1918, link-local (incl. 169.254.169.254), and IPv6 unique-local hosts are blocked.
- [x] Non-http(s) schemes return a deterministic `[tool_error]`.
- [x] Existing public-Internet behavior is preserved when targets are public.
- [x] No regressions in current `tests/test_agent_tools_contract.py`.
- [x] New unit tests cover each blocked category.

## Affected Files / Components
- `src/agent/tools.py`
- `src/config.py` (optional new setting `AGENT_TOOL_MAX_REDIRECTS`)
- `tests/test_agent_tools_contract.py` (or new `tests/test_security_ssrf.py`)

## Risks / Dependencies
- DNS resolution adds latency and a possible failure mode; ensure timeouts cover it.
- Some legitimate targets (CDN edges) resolve to many IPs — block on *any* private IP, not all.
- Local development against `localhost` Ollama is unaffected because Ollama is reached directly via httpx, not via the agent tool.

## Validation Steps
1. Call the tool with `http://127.0.0.1/`, `http://169.254.169.254/latest/meta-data/`, `http://10.0.0.1/`. Each must return `[tool_error] blocked_target: …`.
2. Call with `https://example.com` — must succeed as before.
3. Stand up a tiny test server that returns `302 Location: http://127.0.0.1/` and verify the tool refuses the redirect.
4. Confirm `file://` and `ftp://` still produce a deterministic error.

## Follow-ups (optional)
- Consider extending the same guard to any future outbound-HTTP tools.
- Emit a `security_event` structured log on every blocked attempt for monitoring.
