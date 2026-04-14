# Project Overview — AI Chat Bot

## What it is

A Telegram chatbot that forwards user messages to a locally-running language model (via Ollama) and returns the response. On LLM errors it responds with a fallback error phrase.

---

## Goal

Demonstrate a minimal, stateless Telegram ↔ LLM integration in Python with a layer of post-processing that shapes the bot's personality at the application level, independent of the model's own behaviour.

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

**Stateless processing.** No database, no session store. Every message is a self-contained request to the LLM. This keeps the bot simple and horizontally scalable at the cost of no conversational memory.

**Runtime model switching.** On startup the bot queries Ollama for available models and lets the operator pick one interactively. The selected model name is stored in `config.OLLAMA_MODEL` and read by `llm.py` on every request, so no restart is needed after selection.

**Polling, not webhooks.** Simplifies deployment — no public HTTPS endpoint required.

---

## Boundaries / non-features

- No chat history or multi-turn context
- Text messages only (media, voice, files are silently ignored)
- Single Ollama instance, no load balancing
- No user authentication or per-user rate limiting
