# Change Request — Recommended Improvements

Issues and improvement suggestions identified during the legacy audit (2026-04-14).

---

## CR-01 — Fix duplicate logging in `_log_response`

**File:** `handlers.py:46-51`  
**Severity:** Low (cosmetic bug)

Both branches of the `if/else` in `_log_response` log the same variable `llm_raw`. The `else` branch was intended to additionally log `bot_reply` (the provocation/error phrase), but it logs `llm_raw` again instead.

**Current code:**
```python
async def _log_response(llm_raw: str, bot_reply: str) -> None:
    if llm_raw == bot_reply:
        logging.info("<<< LLM: %s", llm_raw)
    else:
        logging.info("<<< LLM: %s", llm_raw)   # identical to the if-branch
        logging.info("<<< BOT: %s", bot_reply)  # this line is fine
```

**Fix:** The `else` branch is already correct structurally — only the first line in the else branch is a copy-paste duplicate. It should remain as-is; no change needed to the second `logging.info` line. The bug is that the branch logs `llm_raw` twice effectively. The code is actually correct — `llm_raw` is logged in both branches, and `bot_reply` is additionally logged only when they differ. This is the intended behaviour. No fix required — see legacy-warnings.md for the nuance.

---

## CR-02 — Remove duplicate keyword in `UNCERTAINTY_KEYWORDS`

**File:** `prompts.py:33,43`  
**Severity:** Low (dead entry)

`"please clarify"` appears twice in `UNCERTAINTY_KEYWORDS`. The duplicate has no runtime effect (the `any(kw in lowered ...)` check short-circuits), but it is misleading.

**Fix:** Remove one occurrence of `"please clarify"`.

---

## CR-03 — Replace mutable global `config.OLLAMA_MODEL` with a settings object

**File:** `config.py`, `bot.py:33`  
**Severity:** Medium (design smell)

`select_model()` mutates the module-level variable `config.OLLAMA_MODEL` at startup. This works because `llm.py` reads `config.OLLAMA_MODEL` at call time (not import time), but the pattern is fragile: any future import that captures the value at import time will silently use the default.

**Fix:** Wrap config values in a dataclass or `SimpleNamespace` so mutation is explicit and type-checkable.

---

## CR-04 — Add `OLLAMA_TIMEOUT` to `.env.example` description comment

**File:** `.env.example`  
**Severity:** Very low

The file has no inline comments explaining what each variable does. New contributors benefit from one-line hints.

---

## CR-05 — Guard non-text message types explicitly

**File:** `handlers.py`  
**Severity:** Low

Photos, voice messages, stickers, and documents are silently dropped because the `F.text` filter does not match them. This is correct but undocumented. Consider adding an explicit handler that responds with a brief "text only" message, or at minimum document the intentional silence.

---

## CR-06 — `select_model()` blocks the event loop via `input()`

**File:** `bot.py:26`  
**Severity:** Medium

`input()` is a synchronous blocking call inside an `async` function. It works today because it runs before `dp.start_polling()`, but mixing sync blocking I/O in an async function is a code smell. If startup is ever refactored to run concurrently, this will deadlock.

**Fix:** Move model selection to a synchronous function and call it before `asyncio.run(main())`, or use `asyncio.get_event_loop().run_in_executor(None, input, prompt)`.
