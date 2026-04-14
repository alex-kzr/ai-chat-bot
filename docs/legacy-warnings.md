# Legacy Warnings

Known limitations, tricky behaviours, and technical debt to be aware of when maintaining or extending this project.

---

## WARN-01 — No conversation history

Each message is processed in complete isolation. The LLM receives only the system prompt and the single user message. There is no memory of previous turns, no context window accumulation.

**Impact:** The bot cannot answer follow-up questions ("what did you mean by that?"), cannot refer to earlier messages, and cannot maintain any conversational state.

---

## WARN-02 — Small model (0.6B) hallucinates confidently

`qwen3:0.6b` has 0.6 billion parameters. It frequently produces factually incorrect answers with high confidence. The system prompt instructs it to "never say I don't know", which amplifies this tendency. The uncertainty detector only fires on explicit doubt keywords — a hallucination delivered confidently passes straight through to the user.

**Impact:** Users may receive wrong information without any indication of uncertainty.

---

## WARN-03 — Uncertainty detector is keyword-only

`_is_uncertain()` scans for hardcoded English keywords. If the LLM responds in Russian (which it will, per the system prompt instruction to match the interlocutor's language), uncertainty phrases like "не знаю", "не уверен", "затрудняюсь ответить" are not detected.

**Impact:** Russian-language uncertainty from the LLM is passed through as a confident answer.

---

## WARN-04 — `config.OLLAMA_MODEL` is mutated at runtime

`select_model()` in `bot.py` overwrites `config.OLLAMA_MODEL` after the module is imported. All code that accesses `config.OLLAMA_MODEL` at call time (currently only `llm.py`) correctly picks up the change. Any future code that captures the value at import time (e.g., `from config import OLLAMA_MODEL`) will silently use the default.

---

## WARN-05 — Duplicate `"please clarify"` in `UNCERTAINTY_KEYWORDS`

`prompts.py` contains `"please clarify"` at positions 13 and 43 (0-indexed). This is harmless at runtime but will cause confusion when editing the keyword list.

---

## WARN-06 — `_log_response` logging behaviour nuance

`handlers.py:46-51`: both branches log `llm_raw`. The `else` branch additionally logs `bot_reply`. This is intentional — it means the raw LLM output is always logged, and the substituted phrase is logged only when it differs. However, the code reads as if both branches do the same thing, which is misleading. The distinction is the second `logging.info` line in the `else` branch.

---

## WARN-07 — No rate limiting or per-user queuing

All Telegram users share the same Ollama instance. A single user can flood the bot with requests and consume all available compute, stalling responses for everyone else.

---

## WARN-08 — Synchronous `input()` inside async function

`bot.py:26` calls `input()` (blocking) inside the `async def select_model()` coroutine. This works today because the call happens before the event loop processes any I/O, but it is an anti-pattern in async Python.

---

## WARN-09 — No `.gitignore` visible in repository root

The task plan (TASK-01) required a `.gitignore`, but the git status shows it is not tracked. Either it was not created, or it exists but the file was not staged. Verify its presence before committing secrets.
