# Domain Model

The project is small and has no persistent entities or database. The domain is defined entirely by the data flowing through the pipeline.

---

## Concepts

### UserMessage

A text string sent by a Telegram user.

| Field | Type | Description |
|---|---|---|
| `text` | `str` | Raw message content |
| `user` | `str \| int` | Telegram username or numeric user ID (for logging) |
| `chat_id` | `int` | Telegram chat ID (used to send reply) |

UserMessage is not stored. It is consumed once and discarded.

---

### OllamaRequest

The JSON payload sent to `POST /api/chat`.

| Field | Value |
|---|---|
| `model` | `config.OLLAMA_MODEL` (runtime) |
| `messages[0].role` | `"system"` |
| `messages[0].content` | `SYSTEM_PROMPT` |
| `messages[1].role` | `"user"` |
| `messages[1].content` | user text |
| `stream` | `false` |

---

### OllamaResponse

The JSON object returned by Ollama.

| Field | Type | Description |
|---|---|---|
| `message.content` | `str` | Generated text (stripped whitespace) |

All other fields in the response are ignored.

---

### LLMResult

The internal return value of `ask_llm()`.

| Field | Type | Description |
|---|---|---|
| `llm_raw` | `str` | Raw model output (or `"[error]"` on failure) |
| `bot_reply` | `str` | Text actually sent to the user |

`bot_reply` equals `llm_raw` when the response passes uncertainty detection.  
`bot_reply` is a random `PROVOCATION_PHRASE` when uncertainty is detected.  
`bot_reply` is a random `ERROR_PHRASE` when an exception occurs.

---

### ResponseClass (enum-like)

Not a code entity, but a conceptual classification of every bot reply:

| Class | Condition | Source |
|---|---|---|
| `NORMAL` | LLM responded, `_is_uncertain` returned `False` | `llm_raw` |
| `PROVOCATION` | LLM responded, `_is_uncertain` returned `True` | `PROVOCATION_PHRASES` |
| `ERROR` | HTTP/API exception | `ERROR_PHRASES` |

---

## Relationships

```
UserMessage
    │
    └──► OllamaRequest  (constructed in ask_llm)
              │
              └──► OllamaResponse  (from Ollama REST API)
                        │
                        └──► LLMResult  (llm_raw + bot_reply)
                                  │
                                  └──► Telegram reply (bot_reply only)
```
