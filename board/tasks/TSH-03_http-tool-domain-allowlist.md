# TSH-03 - Optional outbound domain allowlist for http_request

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide an opt-in deny-by-default control for environments that want to restrict the agent's outbound web access to a known set of domains. Useful in production deployments where the bot only needs to read a handful of internal documentation sites.

## Context
- Tool: `src/agent/tools.py` (`http_request`)
- Settings: `src/config.py` (`AgentToolSettings`) and `.env.example`
- Companion to TSH-01 (SSRF block); allowlist is layered on top of network-level guards.

## Requirements
- Add a new setting `AGENT_TOOL_HTTP_DOMAIN_ALLOWLIST` parsed as a comma-separated list of domains/suffixes (e.g. `example.com, docs.internal.example`).
- Empty / unset = current behavior (open Internet, still subject to TSH-01).
- When non-empty, `http_request` must reject any URL whose host does not match an entry (exact match or `*.suffix` semantics).
- Apply the same check to redirect targets and same-origin resource loads (although same-origin already restricts them, the allowlist applies first).
- Log a structured event when a request is blocked by the allowlist, without including secrets.

## Implementation Notes
- Parse the env var inside `load_settings`. Trim whitespace, lowercase entries, drop empties.
- Add a small helper `_host_matches(host: str, allowlist: list[str]) -> bool` in `src/agent/tools.py`.
- Update the README/`.env.example` with the new variable and an example.

## Testing
- [x] Unit tests
- [x] Integration tests
- [x] Manual testing

## Definition of Done
- [x] New setting validated and surfaced through `Settings`.
- [x] When unset, tool behavior is unchanged.
- [x] When set, requests to non-allowlisted hosts return a deterministic `[tool_error] blocked_target: not_in_allowlist`.
- [x] Suffix matching (`*.example.com`) works.
- [x] Tests cover allowlisted, non-allowlisted, suffix-match, and case-insensitive hostnames.

## Affected Files / Components
- `src/config.py`
- `src/agent/tools.py`
- `.env.example`
- `tests/test_agent_tools_contract.py` (or `tests/test_security_ssrf.py`)
- `README.md` (configuration table)

## Risks / Dependencies
- Misconfiguration could break legitimate agent use; keep default empty.
- Coordinate with TSH-01 so error messages remain consistent.

## Validation Steps
1. With the variable unset, fetch `https://example.com` — succeeds.
2. Set `AGENT_TOOL_HTTP_DOMAIN_ALLOWLIST=example.com` and fetch `https://example.com` — succeeds; `https://google.com` — `[tool_error] blocked_target: not_in_allowlist`.
3. Set `AGENT_TOOL_HTTP_DOMAIN_ALLOWLIST=*.example.com` and fetch `https://docs.example.com` — succeeds.

## Follow-ups (optional)
- Add a denylist counterpart for environments where allowlisting is too restrictive.
