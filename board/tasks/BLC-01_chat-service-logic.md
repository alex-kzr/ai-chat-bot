# BLC-01 - Cover ChatService request/response cycle

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Lock in the contract of `ChatService.generate_response`: prompt assembly, single gateway call, and `LLMReply` propagation — so we can refactor the chat path without regressions.

## Context
- `src/modules/chat/service.py` builds the prompt from system prompt + history + new user message and calls `OllamaGateway`.
- An adjacent file `tests/test_chat_service.py` exists — extend, do not duplicate.

## Requirements
Add focused tests (in `tests/test_chat_service_logic.py` or extend the existing `test_chat_service.py`) that:
- Verify `generate_response` calls the gateway exactly once per invocation.
- Verify the prompt sent to the gateway contains the system prompt, every history message in order, and the new user message at the end.
- Verify the returned `LLMReply.text` matches the gateway's scripted reply.
- Verify the `thinking` field is preserved when `OLLAMA_THINK=true` and absent otherwise.
- Verify history is **not** mutated by `ChatService` (ownership is `HistoryService`).

## Implementation Notes
- Use `FakeOllamaGateway` (TF-02) with a single scripted `LLMReply`.
- Parametrize the thinking-on/thinking-off case.
- Use AAA structure; one behavior per test.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Five focused tests added, all passing.
- [x] No real Ollama call — `FakeOllamaGateway.calls` recorded.
- [x] Tests run in <1s.

## Affected Files / Components
- `tests/test_chat_service_logic.py` (new) or extend `tests/test_chat_service.py`.
- `src/modules/chat/service.py` (read-only for tests).

## Risks / Dependencies
- Depends on TF-02 (`FakeOllamaGateway`).

## Validation Steps
1. `pytest -q tests/test_chat_service_logic.py` — passes.
2. Mutate prompt assembly in `ChatService` (e.g. drop history) — at least one test fails.
3. `pytest -q` — full suite green.

## Follow-ups (optional)
- Add a property-based test for prompt structure if/when prompt formatting is centralized.
