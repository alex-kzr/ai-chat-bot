# Architecture

## High-level data flow

```
User (Telegram)
      │  text message
      ▼
 aiogram polling
      │
      ▼
 handlers.py — handle_text()
      │  user text
      ▼
 llm.py — ask_llm()
      │  POST /api/chat  (system prompt + user text)
      ▼
 Ollama REST API
      │  JSON response → llm_raw
      │  (or ERROR_PHRASE on exception)
      ▼
 handlers.py — message.answer()
      │
      ▼
User (Telegram)
```

---

## Module responsibilities

### `bot.py` — Entry point

- Runs `select_model()` before the event loop starts (interactive CLI model selection).
- Creates `Bot` and `Dispatcher`, registers the router.
- Calls `dp.start_polling(bot)` — the main event loop.

### `config.py` — Configuration

- Single source of truth for all environment-driven settings.
- Loaded once at import time via `python-dotenv`.
- `OLLAMA_MODEL` is the only field mutated at runtime (by `select_model()`).

### `handlers.py` — Telegram layer

- Owns the aiogram `Router`.
- `handle_start`: responds to `/start` with a welcome message.
- `handle_text`: orchestrates the request pipeline, manages the typing indicator.
- `_keep_typing`: background coroutine that resends `TYPING` action every 4 s.
- `_log_response`: async log helper fired as a fire-and-forget task after reply is sent.

### `llm.py` — LLM integration

- `ask_llm(user_text)` → `(llm_raw, bot_reply)`: the only public interface.
- Builds the Ollama chat payload (system prompt + user message).
- Returns the LLM response and an error phrase on exception.

### `prompts.py` — Personality data

- `SYSTEM_PROMPT`: instructs the model to be helpful and concise.
- `ERROR_PHRASES`: 3 fallback messages used on LLM errors.

---

## Concurrency model

The bot is fully async (Python `asyncio`). aiogram drives the event loop. `httpx.AsyncClient` is used for all HTTP calls so Ollama requests do not block the event loop. The typing indicator runs as a separate `asyncio.Task` cancelled in the `finally` block of `handle_text`.

---

## Deployment topology

```
┌─────────────────────────────┐
│  Developer machine / server │
│                             │
│  python bot.py              │  ◄─── Telegram Bot API (polling)
│                             │
│  ollama serve               │
│  (localhost:11434)          │
└─────────────────────────────┘
```

No external database. No message queue. No webhook. Ollama and the bot process run on the same host.
