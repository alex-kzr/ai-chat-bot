# API Reference

The bot integrates with three runtime interfaces:

1. Telegram Bot API (via `aiogram`)
2. Ollama REST API (via `httpx`)
3. Internal agent tool interface (`src/agent/tools.py`)

---

## Telegram Bot API

### Incoming updates handled

| Update type | Filter | Handler |
|---|---|---|
| `/start` command | `Command("start")` | `handle_start` |
| `/agent <task>` command | `Command("agent")` | `handle_agent` |
| Text message | `F.text` | `handle_text` |

Notes:
- URL-containing text is routed through the agent loop.
- Non-text updates are ignored by default (no matching handler).

### Outgoing calls made

| Method | Purpose |
|---|---|
| `sendMessage` | Sends final response to user |
| `sendChatAction` | Sends typing indicator while processing |

Agent-mode user response contract:
- User sees only `final_answer`
- If loop ends without `final_answer`, user receives a controlled fallback message

---

## Ollama REST API

### `GET /api/tags`

Used at startup (`select_model`) to list available models.

### `POST /api/chat`

Used by regular chat path (`ask_llm`) for non-agent text handling.

### `POST /api/generate`

Used by the agent loop (`src/agent/core.py`) with a prompt assembled from:
- system instructions
- user task
- iterative observations

The model must return one JSON object per turn:

```json
{"tool":"tool_name","args":{}}
```

or

```json
{"final_answer":"..."}
```

---

## Internal Agent Contract

Parser output types (`src/agent/parser.py`):
- `ActionStep(action, args)` for `{"tool","args"}`
- `FinalStep(final_answer)` for `{"final_answer"}`
- `ParseError(reason, raw)` for malformed/invalid output

Loop stop conditions (`src/agent/core.py`):
- `final` (got `final_answer`)
- `max_steps` (reached `AGENT_MAX_STEPS`)
- `error` (terminal parse/LLM failure)

---

## `http_request` Tool Output

`http_request` returns a structured JSON observation string with stable top-level fields:

```json
{
  "url": "https://example.com",
  "request": {"method": "GET"},
  "status": {"code": 200, "reason": "OK"},
  "title": "Example Domain",
  "main_text": "...",
  "main_text_truncated": false,
  "html": {
    "content_type": "text/html; charset=utf-8",
    "encoding": "utf-8",
    "bytes_read": 12345,
    "truncated": false
  },
  "resources": {
    "policy": {
      "origin": "https://example.com",
      "same_origin_only": true,
      "max_resource_count": 8,
      "max_resource_bytes": 120000,
      "max_total_resource_bytes": 400000
    },
    "discovered_count": 3,
    "loaded": [],
    "skipped": [],
    "failed": []
  }
}
```

Tool error format:

```text
[tool_error] <deterministic reason>
```

---

## Key Config Knobs

- `AGENT_MAX_STEPS`
- `AGENT_TOOL_TIMEOUT`
- `AGENT_TOOL_USER_AGENT`
- `AGENT_TOOL_FOLLOW_REDIRECTS`
- `AGENT_TOOL_MAX_HTML_BYTES`
- `AGENT_TOOL_MAX_RESOURCE_COUNT`
- `AGENT_TOOL_MAX_RESOURCE_BYTES`
- `AGENT_TOOL_MAX_TOTAL_RESOURCE_BYTES`
- `AGENT_TOOL_MAX_MAIN_TEXT_CHARS`
- `AGENT_TOOL_MAX_OBSERVATION_CHARS`
