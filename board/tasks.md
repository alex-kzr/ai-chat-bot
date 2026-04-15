# 📋 Tasks — Pseudo-Memory
---

## Phase 1 — Pseudo-Memory

### PM-01 Create history storage module
Create `src/history.py` with in-memory per-user history: `get_history()`, `append_message()`, `clear_history()`.
→ [PM-01-history-storage.md](./tasks/PM-01-history-storage.md)

### PM-02 Refactor ask_llm() to accept history
Update `src/llm.py` so `ask_llm()` accepts a `history` list and sends full context (system prompt + history + new message) to Ollama.
→ [PM-02-llm-history-support.md](./tasks/PM-02-llm-history-support.md)

### PM-03 Wire history into message handler
Update `src/handlers.py` to load user history before calling `ask_llm()` and save the assistant reply afterward.
→ [PM-03-handler-integration.md](./tasks/PM-03-handler-integration.md)

---

# 📋 Tasks — Source Restructuring
---

## Phase 1 — Source Restructuring

### SR-01 Create src/ package directory
Create the `src/` directory with an `__init__.py` to make it a proper Python package.
→ [SR-01-create-src-package.md](./tasks/SR-01-create-src-package.md)

### SR-02 Move source modules to src/
Move `config.py`, `prompts.py`, `llm.py`, `handlers.py`, and `bot.py` from the project root into `src/`.
→ [SR-02-move-source-modules.md](./tasks/SR-02-move-source-modules.md)

### SR-03 Update internal imports in src/ modules
Fix all `import` statements inside the moved modules to resolve correctly within the `src/` package (relative imports).
→ [SR-03-update-imports.md](./tasks/SR-03-update-imports.md)

### SR-04 Update project entry point
Replace root-level `bot.py` with a thin `main.py` launcher that delegates to `src.bot`, so the bot is started with `python main.py`.
→ [SR-04-update-entry-point.md](./tasks/SR-04-update-entry-point.md)

### SR-05 Validate end-to-end after refactoring
Run the bot, verify startup, test `/start` and a text message, confirm no import errors or regressions.
→ [SR-05-validate-end-to-end.md](./tasks/SR-05-validate-end-to-end.md)

---

## Phase 2 — Remove Provocation Logic

### RPL-01 Remove provocation data from prompts.py
Delete `PROVOCATION_PHRASES` and `UNCERTAINTY_KEYWORDS` from `prompts.py` and update `SYSTEM_PROMPT` to a neutral, helpful tone.
→ [RPL-01-remove-provocation-data.md](./tasks/RPL-01-remove-provocation-data.md)

### RPL-02 Remove uncertainty detection from llm.py
Delete `_is_uncertain()` function, remove its call from `ask_llm()`, update imports, simplify return path.
→ [RPL-02-remove-uncertainty-detection.md](./tasks/RPL-02-remove-uncertainty-detection.md)

### RPL-03 Update welcome message in handlers.py
Replace the arrogant `WELCOME_MESSAGE` with a neutral, friendly greeting.
→ [RPL-03-update-welcome-message.md](./tasks/RPL-03-update-welcome-message.md)

### RPL-04 Update docs/algorithms.md
Remove the "Uncertainty Detection" algorithm section; update "LLM Request / Response" section to reflect the simplified flow.
→ [RPL-04-update-docs-algorithms.md](./tasks/RPL-04-update-docs-algorithms.md)

### RPL-05 Update docs/architecture.md
Remove provocation branch from data-flow diagram; update module responsibilities for `llm.py` and `prompts.py`.
→ [RPL-05-update-docs-architecture.md](./tasks/RPL-05-update-docs-architecture.md)

### RPL-06 Update docs/project-overview.md
Remove provocation personality description; update goal and key design decisions sections.
→ [RPL-06-update-docs-project-overview.md](./tasks/RPL-06-update-docs-project-overview.md)

### RPL-07 Update README.md
Remove provocation from the "How it works" diagram and bot description.
→ [RPL-07-update-readme.md](./tasks/RPL-07-update-readme.md)

---

# 📋 Tasks — Context Limitation
---

## Phase 1 — Context Limitation

### CL-01 Add MAX_HISTORY_MESSAGES constant to config
Add `MAX_HISTORY_MESSAGES` (and stub `MAX_HISTORY_CHARS`) to `src/config.py` so limits are centrally configurable.
→ [CL-01-add-history-limit-config.md](./tasks/CL-01-add-history-limit-config.md)

### CL-02 Implement trim_history() in history.py
Add `trim_history(user_id)` to `src/history.py` that removes oldest messages (FIFO) until the list is within `MAX_HISTORY_MESSAGES`. Log when trimming occurs.
→ [CL-02-implement-trim-history.md](./tasks/CL-02-implement-trim-history.md)

### CL-03 Call trim_history() inside append_message()
Update `append_message()` in `src/history.py` to call `trim_history()` after every append, enforcing the limit automatically on every write.
→ [CL-03-wire-trim-into-append.md](./tasks/CL-03-wire-trim-into-append.md)

---

# 📋 Tasks — History Summarization
---

## Phase 1 — History Summarization

### HS-01 Add summarization config constants
Add `SUMMARY_THRESHOLD` and `SUMMARY_KEEP_RECENT` to `src/config.py` so summarization thresholds are centrally configurable.
→ [HS-01-summarization-config.md](./tasks/HS-01-summarization-config.md)

### HS-02 Add summarization prompt to prompts.py
Add a `SUMMARIZATION_PROMPT` template to `src/prompts.py` that instructs the LLM to produce a structured, fact-preserving summary (topics, goals, constraints, open questions) without hallucination.
→ [HS-02-summarization-prompt.md](./tasks/HS-02-summarization-prompt.md)

### HS-03 Create summarizer module
Create `src/summarizer.py` with: `needs_summarization(user_id)`, `get_messages_to_summarize(user_id)`, `call_llm_for_summary(messages)`, and `compress_history(user_id)`.
→ [HS-03-summarizer-module.md](./tasks/HS-03-summarizer-module.md)

### HS-04 Wire summarization into handler pipeline
Update `src/handlers.py` to call `compress_history()` before each LLM request, ensuring the context stays bounded and the summary is included in every subsequent call.
→ [HS-04-wire-summarization.md](./tasks/HS-04-wire-summarization.md)

---

# 📋 Tasks — System Prompt
---

## Phase 1 — System Prompt

### SP-01 Move SYSTEM_PROMPT to config.py
Add `SYSTEM_PROMPT` and `SYSTEM_PROMPT_ENABLED` to `src/config.py`, reading values from environment variables with sensible defaults. Remove the `SYSTEM_PROMPT` constant from `src/prompts.py`.
→ [SP-01-system-prompt-config.md](./tasks/SP-01-system-prompt-config.md)

### SP-02 Update ask_llm() to read system prompt from config
Change `src/llm.py` to import `SYSTEM_PROMPT` and `SYSTEM_PROMPT_ENABLED` from `src/config` instead of `src/prompts`. Only inject the system message when `SYSTEM_PROMPT_ENABLED` is `True`.
→ [SP-02-llm-use-config-prompt.md](./tasks/SP-02-llm-use-config-prompt.md)

### SP-03 Add deduplication guard in ask_llm()
Before prepending the system message, check whether `history` already starts with a `{"role": "system", ...}` entry. If it does, skip injection to avoid duplicate system messages.
→ [SP-03-dedup-system-message.md](./tasks/SP-03-dedup-system-message.md)

---

# 📋 Tasks — Model Request Context Logging
---

## Phase 1 — Logging Infrastructure Setup

### LIS-01 Create logging configuration and utilities
Create `src/context_logging.py` with configurable logger setup, log output options (console/file), and utility functions for log formatting. Add logging configuration constants to `src/config.py`.
→ [LIS-01-logging-infrastructure.md](./tasks/LIS-01-logging-infrastructure.md)

### LIS-02 Implement context extraction and serialization
Add functions to extract model request context (messages list, roles, order) and serialize it into a readable format. Support both human-readable and structured (JSON) output formats.
→ [LIS-02-context-extraction.md](./tasks/LIS-02-context-extraction.md)

### LIS-03 Add token counting mechanism
Implement or integrate token counting to measure the size of the context being logged. Support multiple tokenization strategies (heuristic estimation, actual tokenizer if available).
→ [LIS-03-token-counting.md](./tasks/LIS-03-token-counting.md)

---

## Phase 2 — Integration with Model Requests

### IMR-01 Identify LLM request boundary and injection points
Analyze `src/llm.py` to identify where requests are constructed and sent. Document the exact point where logging should be injected without breaking the flow.
→ [IMR-01-request-boundary.md](./tasks/IMR-01-request-boundary.md)

### IMR-02 Integrate logging into request pipeline
Update `src/llm.py` to call the logging infrastructure immediately before sending each request to the LLM. Ensure logging covers all code paths (direct calls, retries, different models).
→ [IMR-02-logging-integration.md](./tasks/IMR-02-logging-integration.md)

### IMR-03 Implement validation and testing
Create test suite verifying that context is logged for all request types, token counts are accurate, log output is readable, and no regressions occur in the bot's response flow.
→ [IMR-03-validation-testing.md](./tasks/IMR-03-validation-testing.md)
