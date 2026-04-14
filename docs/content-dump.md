# Content Dump — Raw Project Inventory

Raw inventory of all source files, their purpose, key constants, and notable strings captured at audit time (2026-04-14).

---

## bot.py

Entry point. Responsibilities:
- Interactive model selection via `select_model()` — queries `GET /api/tags`, prints numbered list, reads stdin choice, mutates `config.OLLAMA_MODEL`.
- Initialises `Bot` and `Dispatcher` from aiogram, attaches `router` from `handlers.py`.
- Starts long-polling with `dp.start_polling(bot)`.
- Logging format: `%(asctime)s %(message)s`, level INFO.

Key startup log line:
```
Bot started: @<username> | LLM: <model> @ <ollama_url>
```

---

## config.py

Reads four environment variables (via `python-dotenv`):

| Variable | Default | Type |
|---|---|---|
| `BOT_TOKEN` | — (required) | `str` |
| `OLLAMA_URL` | `http://localhost:11434` | `str` |
| `OLLAMA_MODEL` | `qwen3:0.6b` | `str` |
| `OLLAMA_TIMEOUT` | `120` | `int` |

Raises `ValueError` on missing `BOT_TOKEN`.

---

## handlers.py

Defines `router = Router()` with two routes:

| Trigger | Handler | Action |
|---|---|---|
| `Command("start")` | `handle_start` | Sends `WELCOME_MESSAGE` |
| `F.text` | `handle_text` | Calls `ask_llm`, sends reply |

`WELCOME_MESSAGE` (Russian):
```
Привет! Я чат-бот на базе локальной языковой модели.

Задавай вопросы — постараюсь помочь.
```

Typing indicator: background asyncio task sends `ChatAction.TYPING` every 4 s while LLM is running; cancelled in `finally`.

Log lines:
- `>>> <user>: <text>` — incoming message
- `<<< LLM: <raw>` — LLM output (always logged, even when replaced by provocation)

---

## llm.py

Exports `ask_llm(user_text: str) -> tuple[str, str]` — returns `(llm_raw, bot_reply)`.

Ollama request payload:
```json
{
  "model": "<config.OLLAMA_MODEL>",
  "messages": [
    {"role": "system", "content": "<SYSTEM_PROMPT>"},
    {"role": "user", "content": "<user_text>"}
  ],
  "stream": false
}
```

Uncertainty check (`_is_uncertain`):
1. Empty response → uncertain
2. Any keyword from `UNCERTAINTY_KEYWORDS` in lowercased response → uncertain
3. Response (stripped of `?!. \n`) equals user text (stripped) → uncertain (echo detection)

---

## prompts.py

### SYSTEM_PROMPT
```
You are a helpful assistant.
Answer clearly and concisely in the user's language.
```

### PROVOCATION_PHRASES (10 items)
```
"You really don't know that? Are you messing with me!"
"Even first graders know that. Don't waste my time."
"Listen, if you don't know that, we have nothing to talk about."
"Let's not waste time on such simple questions, figure out the basics first."
"What nonsense. Looks like we're on different levels — no point in continuing."
"I'm not ready to explain such basic things from scratch."
"Are you serious right now or joking?"
"This is not the level of discussion I was expecting."
"No, I pass, count me out."
"Listen, you should Google it first, then come back to me."
```

### ERROR_PHRASES (3 items)
```
"The universe is temporarily not answering. Try later — or don't, I don't care."
"My thoughts are occupied with more important things. Come back later."
"Something went wrong, but it's definitely not my fault. Try again."
```

### UNCERTAINTY_KEYWORDS (27 entries, 1 duplicate)
Full list includes: `don't know`, `not sure`, `i'm unsure`, `cannot answer`, `can't help`, `cannot provide`, `no information`, `no data`, `hard to say`, `difficult to say`, `cannot`, `unable`, `clarify`, `please clarify` *(duplicate)*, `don't understand`, `unclear question`, `not related`, `i don't know`, `i'm not sure`, `i am not sure`, `i cannot`, `i can't`, `uncertain`, `could you clarify`.

---

## requirements.txt

```
aiogram==3.15.0
httpx==0.28.1
python-dotenv==1.1.0
```

---

## .env.example

```
BOT_TOKEN=your_telegram_bot_token_here
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:0.6b
OLLAMA_TIMEOUT=120
```
