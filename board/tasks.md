# 📋 Tasks — Automated Test Suite
---

## Phase 1 — Test Foundations

### TF-01 Shared pytest fixtures for runtime and settings
Add a `tests/conftest.py` (or extend the existing one) with fixtures that build a fake `Runtime` — typed `Settings`, in-memory `EventBus`, `UserService`, `RateLimiter`, and orchestrator stubs — so handler/service tests can request a ready-to-use runtime instead of constructing it ad hoc.
→ [TF-01_shared-pytest-fixtures.md](./tasks/TF-01_shared-pytest-fixtures.md)

### TF-02 FakeOllamaGateway and Telegram message builders
Add reusable test doubles: a `FakeOllamaGateway` returning scripted `LLMReply` objects (and configurable failure modes), and helpers (`make_message`, `make_bot`) that build aiogram `Message` instances with mocked `answer`/`send_chat_action` for handler tests.
→ [TF-02_fake-gateway-and-message-builders.md](./tasks/TF-02_fake-gateway-and-message-builders.md)

### TF-03 Document test layout and markers
Document the `tests/` layout (unit / handlers / integration), introduce pytest markers in `pyproject.toml`, and confirm `asyncio_mode = "auto"` works for the new async tests. No new dependencies.
→ [TF-03_document-test-layout-and-markers.md](./tasks/TF-03_document-test-layout-and-markers.md)

## Phase 2 — Business Logic Coverage

### BLC-01 Cover ChatService request/response cycle
Add `tests/test_chat_service_logic.py` — verify `ChatService.generate_response` builds the prompt from system prompt + history + new user message, calls the gateway exactly once, and returns the `LLMReply` (text + thinking when enabled). Use `FakeOllamaGateway`.
→ [BLC-01_chat-service-logic.md](./tasks/BLC-01_chat-service-logic.md)

### BLC-02 Cover HistoryService trim and summarization
Add `tests/test_history_service_logic.py` — verify `append_message` enforces `MAX_HISTORY_MESSAGES`, that trimming preserves the most recent turns, and that crossing the summarization threshold triggers the summarizer with the expected payload (summarizer mocked).
→ [BLC-02_history-service-logic.md](./tasks/BLC-02_history-service-logic.md)

### BLC-03 Cover ChatOrchestrator routing and events
Add `tests/test_chat_orchestrator_logic.py` — verify `process_text` routes URL-bearing messages to the URL flow and plain text to the chat flow, and that `MessageReceived` and `ResponseGenerated` are published in order on success. Failures must not publish `ResponseGenerated`.
→ [BLC-03_chat-orchestrator-logic.md](./tasks/BLC-03_chat-orchestrator-logic.md)

### BLC-04 Cover agent loop end-to-end
Add `tests/test_agent_loop_logic.py` — drive `agent.core.run_agent` with a stubbed gateway whose scripted outputs walk through `tool` → observation → `final_answer`. Assert the resulting `AgentResult.steps`, `final_answer`, and `stopped_reason`. Cover the `max_steps` cutoff path.
→ [BLC-04_agent-loop-logic.md](./tasks/BLC-04_agent-loop-logic.md)

## Phase 3 — Telegram Handler Coverage

### THC-01 Test handle_start
Add `tests/test_handlers_start.py` — assert `/start` replies with the exact `WELCOME_MESSAGE` and does not invoke the LLM or orchestrators.
→ [THC-01_handle-start.md](./tasks/THC-01_handle-start.md)

### THC-02 Test handle_text happy path
Add `tests/test_handlers_text.py` — `handle_text` resolves the user (publishing `UserCreated` on first seen), passes through rate limit and length checks, calls `chat_orchestrator.process_text`, and delivers the reply via `message.answer`. Use the fixtures from TF-01/TF-02.
→ [THC-02_handle-text-happy-path.md](./tasks/THC-02_handle-text-happy-path.md)

### THC-03 Test handle_agent command parsing
Add `tests/test_handlers_agent.py` — `/agent` with no task body returns the usage hint, `/agent <task>` runs the agent orchestrator and replies with its result, and oversize tasks are rejected before the agent is invoked.
→ [THC-03_handle-agent-command.md](./tasks/THC-03_handle-agent-command.md)

### THC-04 Test message splitting and typing indicator
Add `tests/test_handlers_chunking.py` — `_split_message` splits replies longer than 4096 characters into ordered chunks; `_keep_typing` is started and cancelled cleanly around the orchestrator call (verify via a controllable async stub).
→ [THC-04_message-splitting-and-typing.md](./tasks/THC-04_message-splitting-and-typing.md)

## Phase 4 — Failure & Edge Case Coverage

### FEC-01 Empty and whitespace-only input
Add `tests/test_handlers_empty_input.py` — empty / whitespace-only text and `/agent` bodies do not invoke the LLM or agent and produce a deterministic, polite reply (or no-op as appropriate).
→ [FEC-01_empty-input.md](./tasks/FEC-01_empty-input.md)

### FEC-02 Unsupported message types ignored
Add `tests/test_handlers_unsupported_types.py` — photo, voice, sticker, document updates do not trigger LLM or agent calls. Confirm the `F.text` filter contract via direct handler inspection.
→ [FEC-02_unsupported-message-types.md](./tasks/FEC-02_unsupported-message-types.md)

### FEC-03 LLM failure handling
Add `tests/test_llm_failures.py` — when `OllamaGateway` raises (`httpx.TimeoutException`, `httpx.HTTPStatusError`, generic `Exception`), the handler still responds with a fallback phrase from `ERROR_PHRASES` and logs the error. No exception propagates out of the handler.
→ [FEC-03_llm-failure-handling.md](./tasks/FEC-03_llm-failure-handling.md)

### FEC-04 Telegram API failure handling
Add `tests/test_telegram_failures.py` — when `message.answer` raises (simulated network error from aiogram), the handler logs and exits cleanly without leaking secrets, and the typing-indicator background task is cancelled.
→ [FEC-04_telegram-api-failure.md](./tasks/FEC-04_telegram-api-failure.md)

## Phase 5 — Tooling & Test Documentation

### TTD-01 Inject runtime override seam
Add a small `set_runtime_for_testing(runtime)` / `reset_runtime_for_testing()` pair (or context-managed override) in `src/runtime.py` so handler tests can swap in a fake runtime without monkey-patching `get_runtime` directly. Public app behavior unchanged.
→ [TTD-01_runtime-override-seam.md](./tasks/TTD-01_runtime-override-seam.md)

### TTD-02 Test markers, coverage, and README section
Register pytest markers (`unit`, `handlers`, `integration`) in `pyproject.toml`, add an optional `pytest --cov=src` command (no new runtime deps; coverage stays optional via `pytest-cov` in dev extras), and add a "Running tests" section to `README.md` with the canonical commands.
→ [TTD-02_markers-coverage-readme.md](./tasks/TTD-02_markers-coverage-readme.md)

---
