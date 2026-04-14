# RPL-06 - Update docs/project-overview.md

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
`docs/project-overview.md` describes the bot as having a "deliberately arrogant personality" and explains the hybrid uncertainty detection as a key design decision. Both descriptions are obsolete after removing provocation logic and must be updated.

## Context
- File: `docs/project-overview.md`
- "What it is" section (lines 3–7): describes arrogant personality and provocation phrase substitution.
- "Key design decisions" section — "Hybrid uncertainty detection" paragraph (lines 32–36): explains `_is_uncertain()` as an intentional design choice.
- "Boundaries / non-features" section (lines 42–47): includes "English-only uncertainty keyword list" as a known limitation.

## Requirements
- Update "What it is" description to reflect the bot's new neutral, helpful behavior.
- Remove the "Hybrid uncertainty detection" design decision paragraph entirely.
- Remove the "English-only uncertainty keyword list" bullet from "Boundaries / non-features".
- Keep all other sections (Goal, Tech stack, Runtime model switching, Polling, other boundaries) unchanged.

## Implementation Notes
- New "What it is" example: "A Telegram chatbot that forwards user messages to a locally-running language model (via Ollama) and returns the response. On LLM errors it replies with a fallback error phrase."

## Definition of Done
- [ ] "What it is" no longer references arrogant personality or provocation
- [ ] "Hybrid uncertainty detection" design decision removed
- [ ] "English-only uncertainty keyword list" limitation removed
- [ ] Document reads consistently with the new bot behavior

## Affected Files / Components
- `docs/project-overview.md`

## Risks / Dependencies
- Depends on RPL-01 and RPL-02 being done first (doc should reflect actual code).

## Validation Steps
1. Open `docs/project-overview.md`.
2. Search for "provocation", "arrogant", "uncertainty", "keyword" — none should appear.
3. Read the document end-to-end and confirm it accurately describes the post-refactor bot.

## Follow-ups (optional)
- RPL-07: Update `README.md`.
