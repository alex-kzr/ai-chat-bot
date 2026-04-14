# Algorithms

## 1. Model Selection (`select_model`)

**Location:** `bot.py:11-35`

**Purpose:** Let the operator choose which Ollama model to use before the bot starts.

**Algorithm:**

```
select_model() → None  (mutates config.OLLAMA_MODEL as side effect)

1. GET {OLLAMA_URL}/api/tags  (timeout 5 s)
   On exception → print warning, return (keep default)

2. Extract list of model names from response JSON

3. Print numbered list; mark the current default with "(default)"

4. Print prompt, read line from stdin
   - Empty string → return (keep default)
   - Digit d where 1 ≤ d ≤ len(models) → config.OLLAMA_MODEL = models[d-1]
   - Anything else → print warning, return (keep default)
```

---

## 2. Typing Indicator Loop (`_keep_typing`)

**Location:** `handlers.py:20-22`

**Purpose:** Show "bot is typing…" animation in Telegram while waiting for LLM.

**Algorithm:**

```
_keep_typing(message, stop_event) → None  (runs as background Task)

Loop until stop_event is set:
  send_chat_action(chat_id, TYPING)
  sleep 4 s

(Telegram typing indicator expires after ~5 s, so 4 s keeps it alive)
```

The task is created with `asyncio.create_task` before calling `ask_llm` and cancelled in the `finally` block so it stops even if `ask_llm` raises.

---

## 3. LLM Request / Response (`ask_llm`)

**Location:** `llm.py:9-31`

**Algorithm:**

```
ask_llm(user_text) → (llm_raw, bot_reply)

1. Build payload:
   {model, messages: [system_prompt, user_text], stream: false}

2. POST {OLLAMA_URL}/api/chat  (timeout = config.OLLAMA_TIMEOUT)
   On any exception:
     log error
     return ("[error]", random(ERROR_PHRASES))

3. llm_raw = response.json()["message"]["content"].strip()

4. return (llm_raw, llm_raw)
```

`random.choice` is Python's built-in uniform random selection from a list — no weights, no seeds.
