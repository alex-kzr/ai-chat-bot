# Usage Guide

## Prerequisites

- Python 3.10+
- CI runs the test suite on Python 3.12 (GitHub Actions)
- Ollama running locally
- Telegram bot token

Install:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and set at least:

```env
BOT_TOKEN=...
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:0.6b
OLLAMA_TIMEOUT=120
```

Configuration is validated through a typed settings layer at startup (`src/config.py`).
If a value is invalid, startup fails with an explicit `SettingsError` message.

---

## Run

```bash
python main.py
```

Startup behavior:
1. model selection prompt (from available Ollama tags)
2. Telegram polling loop starts
3. selected model is stored in explicit runtime state (no hidden global mutation)

---

## Telegram Usage

- `/start` -> welcome message
- regular text -> standard LLM response
- text containing URL -> routed through agent loop
- `/agent <task>` -> force agent loop

Agent reply behavior:
- user receives only final answer
- no intermediate tool/observation messages are sent to chat

---

## Agent/HTTP Tuning

Useful environment variables:

- `MAX_HISTORY_MESSAGES`
- `AGENT_MAX_STEPS`
- `AGENT_TOOL_TIMEOUT`
- `AGENT_TOOL_USER_AGENT`
- `AGENT_TOOL_MAX_HTML_BYTES`
- `AGENT_TOOL_MAX_RESOURCE_COUNT`
- `AGENT_TOOL_MAX_RESOURCE_BYTES`
- `AGENT_TOOL_MAX_TOTAL_RESOURCE_BYTES`
- `AGENT_TOOL_MAX_MAIN_TEXT_CHARS`
- `AGENT_TOOL_MAX_OBSERVATION_CHARS`

---

## Validation Runbook

### 1. Malformed JSON handling
- Simulate model output with invalid JSON.
- Expected: parser retry path, then controlled stop if still invalid.

### 2. Unknown tool handling
- Simulate `{"tool":"unknown","args":{}}`.
- Expected: deterministic `[tool_error] unknown tool` observation and continued loop.

### 3. Max-step stop
- Simulate tool-only outputs without `final_answer`.
- Expected: stop with `max_steps`, user receives controlled fallback.

### 4. Multi-step HTTP scenario
- Send `/agent summarize https://example.com`.
- Expected:
  - at least one `http_request` step in logs
  - structured observation with page fields and resource summary
  - only final answer shown in Telegram

---

## Quality Checks

Install dev tooling:

```bash
pip install -r requirements-dev.txt
```

Run checks:

```bash
pytest
ruff check src tests
mypy src
```

CI reproduction (matches `.github/workflows/python-ci.yml`):

```bash
# Use Python 3.12 locally if you want to match CI exactly
python -m pip install -r requirements-dev.txt
pytest
```

---

## Debugging

- Enable context logging via existing logging config (`CONTEXT_LOGGING_ENABLED`, `LOG_DESTINATION`, `LOG_FORMAT`).
- For agent runs, search for JSON-line events containing `"kind":"agent_event"` and same `run_id`.
