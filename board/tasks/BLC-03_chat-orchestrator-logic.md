# BLC-03 - Cover ChatOrchestrator routing and events

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Lock in the routing contract — URL-bearing text takes the URL path, plain text takes the chat path — and the event publication order, so future changes to orchestration cannot silently regress event consumers (history, observability).

## Context
- `src/services/chat_orchestrator.py` calls `ChatService` and publishes `MessageReceived` / `ResponseGenerated`.
- There is already `tests/test_chat_flow_events.py` — extend if coherent, otherwise add a sibling logic-focused file.

## Requirements
Add `tests/test_chat_orchestrator_logic.py`:
- Plain-text input: `MessageReceived` is published before the chat call; `ResponseGenerated` is published after a successful reply; reply text matches gateway script.
- URL-bearing input: routed through the URL/HTML path; plain chat path is not invoked.
- Failure path: when `ChatService.generate_response` raises, `MessageReceived` is still published; `ResponseGenerated` is **not** published; the exception propagates (or is mapped to a documented fallback — assert whichever the current contract is).
- User isolation: events are tagged with the correct `user_id`.

## Implementation Notes
- Use a real `EventBus` from TF-01; subscribe a recording subscriber.
- Mock `ChatService` and the URL flow.
- Assert event order via the recording subscriber's append-only log.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Routing covered for both text and URL inputs.
- [x] Event order asserted on the success path.
- [x] Failure path asserted: no `ResponseGenerated`.

## Affected Files / Components
- `tests/test_chat_orchestrator_logic.py` (new)
- `src/services/chat_orchestrator.py` (read-only)

## Risks / Dependencies
- Depends on TF-01.

## Validation Steps
1. `pytest -q tests/test_chat_orchestrator_logic.py` — passes.
2. Swap event order in orchestrator — test fails.
3. Full suite green.

## Follow-ups (optional)
- Extend coverage to `agent_orchestrator` event flow if it grows event-driven.
