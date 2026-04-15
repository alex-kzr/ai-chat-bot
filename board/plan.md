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
