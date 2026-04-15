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
