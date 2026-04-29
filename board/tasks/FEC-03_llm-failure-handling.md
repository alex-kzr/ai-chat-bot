# FEC-03 - LLM failure handling

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
The bot must keep working when the LLM does not. Verify timeouts, HTTP errors, and unexpected exceptions all result in a graceful fallback reply rather than a crashed handler or a leaking exception.

## Context
- `src/ollama_gateway.py` raises `httpx.TimeoutException`, `httpx.HTTPStatusError`, etc.
- `src/handlers.py:handle_text` wraps the orchestrator call; `chat_orchestrator.process_text` decides how failures surface.
- `ERROR_PHRASES` provides fallback strings.

## Requirements
Add `tests/test_llm_failures.py`:
- `FakeOllamaGateway.script = [httpx.TimeoutException("...")]` → handler replies with one of `ERROR_PHRASES`; the exception does not propagate.
- `FakeOllamaGateway.script = [httpx.HTTPStatusError("500", request=..., response=...)]` → same fallback behavior; error logged once.
- `FakeOllamaGateway.script = [RuntimeError("boom")]` → same fallback behavior.
- Sensitive details (like an API key, if accidentally present) do not appear in logs — verify via caplog and `sanitize_log_data`.

## Implementation Notes
- Drive the test through `ChatService` + `ChatOrchestrator` if the handler-level mock can't reach the gateway — otherwise replace `chat_orchestrator.process_text` with one that re-raises and assert the handler's catch.
- Use `caplog` to assert the error log line.
- Parametrize the three failure modes for compactness.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Three failure modes covered.
- [x] Fallback reply asserted in each case.
- [x] No exception propagates out of the handler.

## Affected Files / Components
- `tests/test_llm_failures.py` (new)
- `src/handlers.py` and/or `src/services/chat_orchestrator.py` (read-only; but if the handler currently has no try/except around the orchestrator call and crashes, **add one** as part of this task — keep the change minimal and document it).

## Risks / Dependencies
- Depends on TF-02 (`FakeOllamaGateway` failure mode).

## Validation Steps
1. `pytest -q tests/test_llm_failures.py` — passes.
2. Comment out the fallback path — at least one test fails.
3. Full suite green.

## Follow-ups (optional)
- Add a circuit-breaker once failure rates need observability beyond logs.
