# Feature: Automated Test Suite

This plan adds a comprehensive automated test suite to the Telegram AI chatbot so the project becomes safe to change. The bot already has focused tests under `tests/` (security, events, services), but coverage is uneven: Telegram handlers, full LLM round-trips, and adverse-input paths are not consistently exercised, and there is no shared scaffolding for handler-level tests.

The goal is to cover business logic, Telegram message handling, and unexpected/error inputs with deterministic, offline tests. All external calls (Ollama LLM, Telegram Bot API, outbound HTTP) must be mocked; tests must be runnable with a single `pytest` invocation. Refactors are kept minimal and only introduced where current code is genuinely hard to test (e.g. handler-level access to `get_runtime()` global). The work preserves the existing modular monolith architecture (`src/modules/*`, `src/services/*`, `src/agent/*`) and the public bot contract.

## Phase 1: Test Foundations (TF-01 to TF-03)

Establish shared scaffolding for the new tests: pytest fixtures for a fake `Runtime` (settings, users, event bus, rate limiter, orchestrators), a `FakeOllamaGateway` that returns scripted replies without touching the network, and reusable Telegram `Message`/`Bot` builders so handler tests can be written declaratively without ad-hoc mocks in every file. Document the test layout, markers, and the canonical pytest command.

## Phase 2: Business Logic Coverage (BLC-01 to BLC-04)

Cover the core logic modules in isolation from Telegram. Tests target `ChatService` (system prompt + history → `LLMReply`), `HistoryService` (append, trim at `MAX_HISTORY_MESSAGES`, summarization trigger), `ChatOrchestrator` (URL vs normal-text routing, `MessageReceived`/`ResponseGenerated` publication), and the agent loop (`agent.core.run_agent`: parser → tool dispatch → `final_answer`, `max_steps` stop reason).

## Phase 3: Telegram Handler Coverage (THC-01 to THC-04)

Cover `src/handlers.py` end-to-end with a fake aiogram `Message` and a stubbed runtime. Tests verify `/start` welcome reply, `/agent` command parsing (missing task, valid task), `handle_text` happy path (user resolved, orchestrator called, reply delivered, response logged), and the message-splitting + typing-indicator lifecycle so long replies and the typing background task behave correctly.

## Phase 4: Failure & Edge Case Coverage (FEC-01 to FEC-04)

Cover adverse inputs and external-service failures. Empty / whitespace-only messages, non-text Telegram updates (photo, voice, sticker), LLM failures (timeout, HTTP error, raised exception → fallback phrase from `ERROR_PHRASES`), and Telegram API failures (`message.answer` raising) — none of which should crash the handler or leak secrets into logs.

## Phase 5: Tooling & Test Documentation (TTD-01 to TTD-02)

Add a thin testability seam for the `get_runtime()` global so handlers can be exercised without monkey-patching module internals, and finalize developer ergonomics: pytest markers (`unit`, `integration`, `handlers`), a single canonical run command, optional coverage reporting, and a short "How to run tests" section in `README.md`.
