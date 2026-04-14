# RPL-03 - Update welcome message in handlers.py

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
The current `WELCOME_MESSAGE` in `handlers.py` reflects the arrogant bot persona ("I'm always right — that's not up for discussion"). After removing provocation logic the bot should present itself as a helpful assistant, so the welcome message must be updated to match.

## Context
- File: `handlers.py`, constant `WELCOME_MESSAGE` (lines 13–17).
- Current text: `"Привет. Я всегда прав — это не обсуждается.\n\nЗадавай вопросы. Если ответ существует — ты его получишь. Если нет — сам виноват, что спросил."`

## Requirements
- Replace `WELCOME_MESSAGE` with a neutral, friendly greeting.
- The message should tell the user what the bot does (answers questions via a local LLM).
- Language: keep Russian (matches original).

## Implementation Notes
- Example replacement: `"Привет! Я чат-бот на базе локальной языковой модели.\n\nЗадавай вопросы — постараюсь помочь."`
- No other logic in `handlers.py` needs to change for this task.

## Definition of Done
- [ ] `WELCOME_MESSAGE` no longer contains arrogant or dismissive language
- [ ] New message is friendly and accurately describes bot behavior
- [ ] `/start` command sends the new message (verified manually or via inspection)

## Affected Files / Components
- `handlers.py`

## Risks / Dependencies
- No code dependencies; purely a text change.
- Should be done after RPL-01 and RPL-02 so the described bot behavior is consistent.

## Validation Steps
1. Open `handlers.py` — read `WELCOME_MESSAGE` value.
2. Confirm no references to "всегда прав" or similar arrogant phrasing.
3. Send `/start` to the running bot and verify the new message appears.

## Follow-ups (optional)
- RPL-04 through RPL-07: update documentation to match the new behavior.
