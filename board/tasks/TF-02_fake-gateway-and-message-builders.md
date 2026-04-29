# TF-02 - FakeOllamaGateway and Telegram message builders

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide deterministic test doubles for the two external boundaries — Ollama and Telegram — so handler/service tests never touch the network and can be written declaratively.

## Context
- Real gateway: `src/ollama_gateway.py` (`generate`, `chat`, `tags`).
- LLM reply shape: `LLMReply` (text + optional thinking).
- aiogram `Message` is awkward to construct directly; existing tests use `MagicMock(spec=Message)`.

## Requirements
- `FakeOllamaGateway` (in `tests/_fakes.py`):
  - Configurable `script: list[LLMReply | Exception]` — each call pops the next item; if it is an exception, raise it; otherwise return it.
  - Records `calls: list[GatewayCall]` for assertion (prompt, model, options).
  - Implements every method handlers/services actually use (`generate`, `chat`).
- Telegram helpers:
  - `make_message(text="hi", user_id=42, username="alice", chat_id=42)` — returns a `MagicMock` with `text`, `from_user.id`, `from_user.username`, `chat.id`, `bot.send_chat_action = AsyncMock()`, `answer = AsyncMock()`.
  - `make_message_with_failing_answer(...)` — same, but `answer` raises a configurable exception.
- All builders are pure helpers (no fixture decorators); fixtures from TF-01 may compose them.

## Implementation Notes
- `LLMReply` already exists in the codebase — reuse, do not redefine.
- `AsyncMock` for any awaited methods.
- Keep the file dependency-light (no aiogram imports beyond `Message` for `spec=`).

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] `FakeOllamaGateway` returns scripted replies in order.
- [x] `FakeOllamaGateway` raises scripted exceptions in order.
- [x] `make_message` produces an aiogram-compatible mock that handler code can use.
- [x] No real network call possible from the fake gateway (no httpx import).

## Affected Files / Components
- `tests/_fakes.py` (new)

## Risks / Dependencies
- Depends on TF-01 for fixture wiring.
- Risk: `LLMReply` shape changes; mitigated by importing the real type.

## Validation Steps
1. Smoke test: instantiate `FakeOllamaGateway(script=[reply1, ValueError("boom")])`, call twice, assert behavior.
2. Smoke test: `make_message(text="x")` → handler can read `.text` and await `.answer(...)`.
3. `pytest -q` passes.

## Follow-ups (optional)
- Add a `FakeAgentRuntime` if BLC-04 ends up needing more than a stubbed gateway.
