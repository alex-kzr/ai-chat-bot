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
