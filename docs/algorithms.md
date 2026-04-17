# Algorithms

## 1. Agent Loop (`run_agent`)

**Location:** `src/agent/core.py`

Flow:

1. Build system prompt with available tools.
2. Send task to LLM.
3. Parse response:
   - `{"tool":"...","args":{...}}` -> execute tool
   - `{"final_answer":"..."}` -> stop with final answer
   - invalid output -> one retry, then terminal error
4. Append tool `observation` into the next turn context.
5. Repeat until `final_answer`, `max_steps`, or controlled terminal error.

Stop reasons:
- `final`
- `max_steps`
- `error`

---

## 2. Parser Contract (`parse_agent_output`)

**Location:** `src/agent/parser.py`

Extraction order:
1. Fenced JSON block (```json ... ```)
2. First balanced JSON object in text
3. Parse error if nothing valid extracted

Validation:
- top-level JSON must be an object
- allowed terminal keys are `final_answer` or `tool`
- `final_answer` must be `str`
- `tool` must be non-empty `str`
- `args` must be an object when `tool` is present

---

## 3. Deterministic HTTP Tool (`http_request`)

**Location:** `src/agent/tools.py`

Pipeline:

1. Normalize and validate URL (`http`/`https` only).
2. Perform deterministic HTML fetch (fixed timeout, redirects, headers, byte limit).
3. Parse HTML and extract:
   - `title`
   - visible `main_text` (scripts/styles excluded)
   - linked resources (`script`, `link`, `img`)
4. Load linked resources under policy:
   - same-origin only
   - max resource count
   - per-resource byte limit
   - total-resource byte limit
5. Build bounded structured observation JSON.
6. Return `[tool_error] ...` on controlled failures.

---

## 4. Structured Logging

**Locations:** `src/agent/core.py`, `src/context_logging.py`

Each agent run gets a `run_id`.  
Structured events include:
- `run_started`
- `loop_step_started`
- `tool_call_started`
- `tool_call_finished` (status + duration)
- `run_completed`
- parse/LLM failure events

All events are emitted as deterministic JSON lines.

---

## 5. Validation Scenarios

### Malformed JSON
- Force model output like `{not-json`
- Expect parser `ParseError`
- Expect one retry then controlled stop on repeated failure

### Unknown tool
- Output `{"tool":"unknown_tool","args":{}}`
- Expect deterministic `[tool_error] unknown tool: ...`
- Expect observation fed back to next turn

### Max steps
- Force tool-only outputs with no `final_answer`
- Expect loop stop with `stopped_reason = "max_steps"`

### Multi-step HTTP flow
- Use URL task requiring web retrieval
- Expect at least one `http_request` step
- Expect final answer only in user-visible Telegram reply
- Expect resource summary in `http_request` observation
