# Pseudo-Memory: Per-User Conversation History

This plan describes the addition of conversational memory to the AI Chat Bot. The bot currently processes every message in isolation, sending only the system prompt and the current user message to the LLM. The goal is to preserve context across turns on a per-user basis.

## Phase 1: Pseudo-Memory (PM-01 to PM-03)

We introduce an in-memory conversation history store, refactor the LLM call to accept history, and wire everything together in the message handler. Each user gets an independent conversation context identified by their Telegram numeric user ID.

- **Storage**: In-memory Python dictionary `{user_id: [messages]}`. Simple and zero-dependency for this prototype; can be swapped for SQLite or Redis later.
- **Isolation**: User IDs are always Telegram's `message.from_user.id` (int, always present), so histories never mix.
- **LLM integration**: `ask_llm()` is refactored to accept a history list. It prepends the system prompt and appends the new user message before sending the full context to Ollama.
- **Handler wiring**: `handle_text()` loads history before the LLM call, then saves the assistant reply afterward.

---

# Refactoring: Move Executable Code to src/

This plan covers moving all executable Python source files from the project root into a `src/` package directory, updating imports, and verifying the system runs correctly afterwards.

## Phase 1: Source Restructuring (SR-01 to SR-05)

Move `bot.py`, `handlers.py`, `llm.py`, `prompts.py`, and `config.py` into `src/` package. Update all internal imports to resolve correctly inside the package. Provide a clean entry point at the project root. Validate end-to-end functionality.

---

# ## Phase 2: Remove Provocation Logic (RPL-01 to RPL-07)

This plan describes the removal of all provocation-related behavior from the chatbot. The bot currently intercepts LLM uncertainty signals and replaces responses with dismissive, harmful phrases. After this change the bot will always return the LLM's actual answer and behave as a standard helpful assistant.

Remove all code, data, and documentation that implements or describes the provocation/uncertainty-replacement feature. Update the bot's personality to neutral and helpful. Verify the system still runs correctly end-to-end.

- **Scope:** `prompts.py`, `llm.py`, `handlers.py`, `docs/`, `README.md`
- **Goal:** Zero references to `PROVOCATION_PHRASES`, `UNCERTAINTY_KEYWORDS`, or `_is_uncertain` remain in code or docs after this phase.

---

# Context Limitation: Bounded Per-User History

This plan introduces a trimming mechanism to `src/history.py` that prevents conversation histories from growing unboundedly. Without a limit, long sessions would overflow LLM context windows and degrade performance.

## Phase 1: Context Limitation (CL-01 to CL-03)

Add a configurable `MAX_HISTORY_MESSAGES` constant, implement a `trim_history()` function that removes the oldest messages (FIFO), and wire it into `append_message()` so every write automatically enforces the limit.

- **Strategy**: Limit by message count (Option A). FIFO removal — oldest messages dropped first.
- **Config**: `MAX_HISTORY_MESSAGES` in `src/config.py`; easily extended later with `MAX_HISTORY_CHARS`.
- **Isolation**: Trimming operates on a single user's history slice — no cross-user effects.
- **Extensibility**: `trim_history()` is a standalone function, making future strategy additions (char limit, summarization) straightforward.

---

# History Summarization: LLM-based Context Compression

This plan introduces LLM-powered summarization to replace the blunt FIFO trim. Instead of silently dropping old messages, the bot detects when history grows too long, asks the LLM to produce a concise summary of the older portion, and stores that summary alongside the most recent messages. This preserves conversation meaning while keeping context bounded.

## Phase 1: History Summarization (HS-01 to HS-04)

Add configurable thresholds, a dedicated summarization prompt, an isolated `src/summarizer.py` module, and wire everything into the existing handler pipeline. Each user's summarization runs independently with no cross-user effects.

- **Trigger**: `SUMMARY_THRESHOLD` (default 10 messages) — when history exceeds this, summarization fires.
- **Retention**: `SUMMARY_KEEP_RECENT` (default 4 messages) — last N messages are kept verbatim; everything older is summarized.
- **History structure**: A special `{"role": "system", "content": "[Summary] ..."}` entry is prepended so the LLM always sees prior context.
- **Summarization prompt**: Dedicated prompt in `src/prompts.py` instructs the LLM to produce a structured, fact-preserving summary without hallucination.
- **Isolation**: Summarization operates on a single user's slice of `_store` — histories never mix.

---

# System Prompt: Configurable LLM Behavior

This plan makes the system prompt a first-class, configurable feature. A `SYSTEM_PROMPT` and its `role: system` injection already exist in `src/prompts.py` and `src/llm.py`, but the value is hardcoded and cannot be changed without editing source. The goal is to expose it through `config.py` (env-var override) and add a deduplication guard so the prompt is never injected twice.

## Phase 1: System Prompt (SP-01 to SP-03)

Move `SYSTEM_PROMPT` into `src/config.py` as an env-configurable constant, update `ask_llm()` to read from config, and guard against duplicate system messages in the history payload.

- **Config**: `SYSTEM_PROMPT` in `src/config.py` reads from `SYSTEM_PROMPT` env var with a sensible default; `SYSTEM_PROMPT_ENABLED` flag allows disabling it entirely.
- **LLM integration**: `ask_llm()` reads the prompt from config instead of importing from `prompts.py` directly.
- **Deduplication**: Before prepending, `ask_llm()` checks whether history already starts with a `role: system` entry and skips injection if so.
