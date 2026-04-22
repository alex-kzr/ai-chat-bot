# MM-03 - Isolate Chat/AI module

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Move AI response generation behind a dedicated Chat/AI module interface.

## Context
The current response flow is split across `src/services/chat_orchestrator.py`, `src/llm.py`, `src/ollama_gateway.py`, and runtime wiring. The Chat/AI module should own response generation while exposing a small public API to orchestration.

## Requirements
- Create a Chat/AI module with its own folder and public interface.
- Keep LLM calls and response formatting behind the module boundary.
- Preserve existing behavior for standard text messages and thinking output.
- Avoid direct History module access from Chat/AI internals.

## Implementation Notes
- Introduce a service such as `ChatService.generate_response(...)`.
- Inject `OllamaGateway`, settings, and event bus dependencies instead of reading runtime globals from module internals where practical.
- Keep URL/agent routing in orchestration unless explicitly moved behind a public interface.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- `src/modules/chat/`
- `src/llm.py`
- `src/services/chat_orchestrator.py`
- `src/runtime.py`
- `tests/`

## Risks / Dependencies
- Streaming and thinking-output behavior must not regress.
- Existing tests around LLM streaming should remain meaningful after the move.

## Validation Steps
1. Run chat service tests with a fake Ollama gateway.
2. Exercise a normal text message through the orchestrator.
3. Expected result: reply generation works without Chat/AI importing History internals.
