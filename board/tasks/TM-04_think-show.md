# TM-04 - Show thinking block in Telegram reply

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Give users optional visibility into the model's reasoning by prepending a formatted thinking section to the bot reply when `SHOW_THINKING=true`.

## Context
After TM-02, `handlers.py` receives the `thinking` string as the third return value of `ask_llm()`. This task wires it into the Telegram reply. The feature is off by default so existing users see no change. Depends on TM-01 and TM-02.

## Requirements
- Add `SHOW_THINKING: bool` to `src/config.py` (env var `SHOW_THINKING`, default `False`).
- In `src/handlers.py`, unpack `llm_raw, bot_reply, thinking = await ask_llm(...)`.
- When `config.SHOW_THINKING` is `True` and `thinking` is non-empty, prepend the thinking block to `bot_reply` using this format:
  ```
  💭 <thinking>
  {thinking}
  </thinking>
  
  {bot_reply}
  ```
- When `SHOW_THINKING=false` or `thinking` is empty, behaviour is identical to today.

## Implementation Notes
- Format the thinking block as plain text (no HTML/Markdown parse mode needed since the bot uses default mode).
- Keep the formatting simple — no collapsible blocks (Telegram doesn't support them natively).
- The `bot_reply` variable used for `message.answer()` should be reassigned to the combined string.

## Definition of Done
- [ ] `SHOW_THINKING` constant in `src/config.py` with default `False`.
- [ ] When `SHOW_THINKING=true` and model returns thinking, the Telegram message starts with the thinking block.
- [ ] When `SHOW_THINKING=false`, no thinking block is prepended.
- [ ] No regressions when `OLLAMA_THINK=false` (thinking is empty string, block is never shown).
- [ ] `.env.example` updated with `SHOW_THINKING=false`.

## Affected Files / Components
- `src/config.py`
- `src/handlers.py`
- `.env.example`

## Risks / Dependencies
- Depends on TM-01, TM-02.
- Thinking traces can exceed Telegram's 4096-character message limit. If `len(bot_reply) > 4000`, truncate the thinking block with `...` rather than the answer.

## Validation Steps
1. Set `OLLAMA_THINK=true`, `SHOW_THINKING=true`, send a message — reply starts with `💭 <thinking>`.
2. Set `SHOW_THINKING=false` — reply contains only the answer.
3. Set `OLLAMA_THINK=false`, `SHOW_THINKING=true` — no thinking block (nothing to show).
4. Test with a very long thinking trace to confirm the message is not truncated mid-answer.
