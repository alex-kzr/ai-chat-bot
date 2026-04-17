# TM-02 - Handle thinking field in ask_llm()

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make `ask_llm()` produce a valid reply even when the model is a thinking model: prefer `content`, fall back to `thinking`, never silently return an error phrase when the model actually generated output.

## Context
Thinking models (qwen3, deepseek-r1) place their chain-of-thought in `response["message"]["thinking"]` and may return an empty `response["message"]["content"]`. The current code reads only `content`, resulting in an empty-response error even though the model produced useful text. TM-01 must be done first (so `config.OLLAMA_THINK` exists).

## Requirements
- After parsing `data = response.json()`, extract both fields:
  - `content = data["message"].get("content", "").strip()`
  - `thinking = data["message"].get("thinking", "").strip()`
- Return `content` if non-empty; fall back to `thinking` if `content` is empty.
- If both are empty, keep the existing empty-response warning and error-phrase path.
- Return the `thinking` value alongside `content` so downstream callers (TM-03, TM-04) can use it — update the return type to `tuple[str, str, str]`: `(llm_raw, bot_reply, thinking)`.
- Update the caller in `src/handlers.py` to unpack the new third element (can be ignored with `_` for now).

## Implementation Notes
- Keep the change minimal: the fallback logic is a two-liner after the existing `.strip()` call.
- The `ask_llm` signature does not change; only the return tuple grows by one element.
- `handlers.py` unpacks as `llm_raw, bot_reply, _ = await ask_llm(...)` until TM-04 uses it.

## Definition of Done
- [ ] `ask_llm()` returns `(llm_raw, bot_reply, thinking)`.
- [ ] When `content` is empty and `thinking` is non-empty, the bot replies with the thinking text.
- [ ] When both are empty, the error path is unchanged.
- [ ] `handlers.py` unpacks the three-tuple without error.
- [ ] No regressions on non-thinking models.

## Affected Files / Components
- `src/llm.py`
- `src/handlers.py`

## Risks / Dependencies
- Depends on TM-01 (`config.OLLAMA_THINK`).
- Any other caller of `ask_llm()` (e.g. agent loop) must also be updated to unpack three values.

## Validation Steps
1. Set `OLLAMA_THINK=true`, send "расскажи анекдот" — bot should reply with the joke (from `thinking` field).
2. Set `OLLAMA_THINK=false`, send the same message — bot replies normally from `content`.
3. Check logs: no "LLM returned empty response" warning when thinking model is active.
