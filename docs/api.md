# API Reference

The bot integrates with two external APIs: the Telegram Bot API (via aiogram) and the Ollama REST API (via httpx).

---

## Telegram Bot API

Accessed indirectly through the aiogram library. The bot uses **long-polling** only.

### Incoming updates handled

| Update type | Filter | Handler |
|---|---|---|
| Message with `/start` command | `Command("start")` | `handle_start` |
| Message with text content | `F.text` | `handle_text` |

All other update types (photos, voice, stickers, documents, etc.) are silently ignored — aiogram's default behaviour when no handler matches.

### Outgoing calls made

| Method | When | Content |
|---|---|---|
| `sendMessage` | After LLM responds | `bot_reply` text |
| `sendChatAction` | While LLM is running | `typing` action, repeated every 4 s |

### Bot commands (registered with BotFather)

| Command | Description |
|---|---|
| `/start` | Display welcome message |

---

## Ollama REST API

Base URL configured via `OLLAMA_URL` (default `http://localhost:11434`).

### `GET /api/tags`

Used once at startup by `select_model()` to enumerate available models.

**Request:** No body, no auth.

**Response:**
```json
{
  "models": [
    {"name": "qwen3:0.6b"},
    {"name": "gemma4:12b"}
  ]
}
```

Bot reads `response.json()["models"]` and extracts `name` from each item.

**Timeout:** 5 seconds (hardcoded in `bot.py`). On failure, startup continues with the default model.

---

### `POST /api/chat`

Called once per user message by `ask_llm()`.

**Request body:**
```json
{
  "model": "<config.OLLAMA_MODEL>",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant. Answer clearly and concisely in the user's language."
    },
    {
      "role": "user",
      "content": "<user message text>"
    }
  ],
  "stream": false
}
```

**Response body (success):**
```json
{
  "message": {
    "role": "assistant",
    "content": "<generated text>"
  }
}
```

Bot reads `response.json()["message"]["content"]` and strips whitespace.

**Timeout:** `config.OLLAMA_TIMEOUT` seconds (default 120).

**Error handling:** Any exception (connection error, timeout, non-2xx status) is caught; the bot replies with a random `ERROR_PHRASE` and logs the exception.

---

## Internal Python interface

### `ask_llm(user_text: str) -> tuple[str, str]`

The only public function in `llm.py`.

| Parameter | Type | Description |
|---|---|---|
| `user_text` | `str` | Raw message text from Telegram user |

**Returns** `(llm_raw, bot_reply)`:

| Field | Type | Description |
|---|---|---|
| `llm_raw` | `str` | Raw model output, or `"[error]"` on exception |
| `bot_reply` | `str` | Text sent to the user (may be a provocation or error phrase) |
