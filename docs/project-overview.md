# Project Overview — AI Chat Bot

## What it is

A Telegram chatbot that forwards user messages to a locally-running language model (via Ollama) and returns the response. On LLM errors it responds with a fallback error phrase.

---

## Goal

Demonstrate a production-lean Telegram ↔ local-LLM integration with explicit runtime wiring, typed settings, and a shared Ollama gateway.

---

## Tech stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.10+ |
| Telegram API | aiogram | 3.15.0 |
| HTTP client | httpx (async) | 0.28.1 |
| LLM runtime | Ollama (local) | any |
| Default model | qwen3:0.6b | — |
| Config | python-dotenv | 1.1.0 |

---

## Key design decisions

**In-memory conversation state.** Per-user history is kept in memory with deterministic trimming and optional summarization of older turns.

**Modular monolith + in-process events.** Feature modules (Users, Chat/AI, History) communicate via an in-memory `EventBus` with typed contracts (`UserCreated`, `MessageReceived`, `ResponseGenerated`) instead of direct cross-module calls.

**Explicit startup bootstrap.** Startup runs in a synchronous bootstrap stage that validates settings, discovers models, selects an active runtime model, and then starts async polling.

**Polling, not webhooks.** Simplifies deployment — no public HTTPS endpoint required.

**Model-agnostic agent termination.** The agent loop relies on explicit runtime limits (timeouts, output-size caps, repeat detection) and conservative stop-sequences on the Ollama boundary to prevent endless generation across different model backends.

---

## Boundaries / non-features

- No persistent storage (history is in-memory only)
- Text messages only (media, voice, files are silently ignored)
- Single Ollama instance, no load balancing
- No user authentication or per-user rate limiting
