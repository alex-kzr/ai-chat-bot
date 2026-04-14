# RPL-07 - Update README.md

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
`README.md` is the first thing a developer or user sees. It currently contains an incomplete description ("A Telegram chatbot with .") and a "How it works" diagram that shows the provocation branch. Both must be fixed to accurately reflect the bot after refactoring.

## Context
- File: `README.md`
- Line 3: `"A Telegram chatbot with . It answers questions via a local language model (Ollama)."` — description has a broken sentence ("with .").
- "How it works" diagram (lines 39–44): shows `uncertain? → provocation phrase` branch.

## Requirements
- Fix the broken bot description on line 3.
- Update the "How it works" ASCII diagram to remove the provocation branch.
- The diagram should show the simple flow: `User message → Ollama LLM → reply`.
- The `error? → sardonic error phrase` path may be kept as it still exists in the code.

## Implementation Notes
- New description example: `"A Telegram chatbot that answers questions via a local language model (Ollama)."`
- New diagram example:
  ```
  User message → Ollama LLM → reply
                     │
               error? → error phrase
  ```

## Definition of Done
- [ ] Bot description on line 3 is complete and accurate
- [ ] "How it works" diagram contains no provocation branch
- [ ] README is consistent with the post-refactor codebase
- [ ] No broken sentences or leftover stubs

## Affected Files / Components
- `README.md`

## Risks / Dependencies
- No code dependencies; doc-only change.
- Should be done last (after all code and other doc tasks) so the README matches the final state.

## Validation Steps
1. Open `README.md`.
2. Search for "provocation" — not found.
3. Read "How it works" section — diagram shows simple LLM pass-through flow.
4. Read the full README for any broken sentences or inconsistencies.

## Follow-ups (optional)
- None — this is the final task in the RPL phase.
