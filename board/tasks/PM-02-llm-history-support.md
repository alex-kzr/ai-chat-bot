# PM-02 - Refactor ask_llm() to accept history

## Status
- [x] To Do
- [x] In Progress
- [x] Done

## Purpose
Update the LLM integration layer so it receives the full per-user conversation history and sends it to Ollama together with the new user message. This enables multi-turn context without changing any other module's public surface beyond the function signature.

## Context
Current `src/llm.py` signature:
```python
async def ask_llm(user_text: str) -> tuple[str, str]
```
Current Ollama payload:
```python
"messages": [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user",   "content": user_text},
]
```

After this task the payload must be:
```python
"messages": [
    {"role": "system", "content": SYSTEM_PROMPT},
    # ...all previous messages from history...
    {"role": "user",   "content": user_text},
]
```

Related files:
- `src/llm.py` — file to modify
- `src/handlers.py` — caller, will be updated in PM-03
- `src/prompts.py` — source of `SYSTEM_PROMPT`

## Requirements
- Change signature to `ask_llm(user_text: str, history: list[dict] | None = None) -> tuple[str, str]`
- Default `history=None` (treated as empty list) so the call from handlers remains backward-compatible until PM-03
- Build the messages list as: `[system_prompt_message] + history + [new_user_message]`
- Do not mutate the `history` list passed in
- Return value remains `(llm_raw, bot_reply)` — no change
- Error handling behavior unchanged

## Implementation Notes
- `history or []` handles both `None` and empty list
- The system message is always first, the new user message is always last
- No size/token limiting required at this stage

## Definition of Done
- [x] `ask_llm` accepts optional `history` parameter
- [x] Ollama payload includes system prompt + history + new user message in correct order
- [x] Empty/None history behaves identically to current implementation
- [x] Return type unchanged
- [x] No regressions to error handling path
- [x] Code is clean and consistent

## Affected Files / Components
- `src/llm.py`

## Risks / Dependencies
- Depends on PM-01 being conceptually understood (history list format must match)
- If `history` contains malformed dicts, Ollama will reject the request — caller's responsibility to pass valid data
- `handlers.py` must be updated in PM-03 to actually pass history; until then, function defaults to empty history

## Validation Steps
1. Import `src.llm` and confirm `ask_llm` accepts the new parameter without error
2. Call `ask_llm("Hello")` (no history) → confirm single-turn behavior unchanged
3. Call `ask_llm("What did I say?", history=[{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}])` → confirm history is included in the Ollama request payload (log or inspect the constructed messages list)
4. Confirm error handling still returns a fallback phrase on Ollama failure

## Follow-ups (optional)
- PM-03 wires the handler to pass real history to this function
- Future: add token-count-based truncation of history if context window is exceeded
