# RPL-05 - Update docs/architecture.md

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
`docs/architecture.md` contains a data-flow diagram that shows the provocation branch (`uncertain? → PROVOCATION_PHRASE`). After the feature is removed the diagram and module descriptions must be updated to reflect the simplified flow.

## Context
- File: `docs/architecture.md`
- Data-flow diagram (lines 5–28): contains `llm.py — _is_uncertain()` node with YES/NO branches.
- Module responsibilities section for `llm.py` (lines 59–63): mentions `_is_uncertain()`.
- Module responsibilities section for `prompts.py` (lines 65–69): lists `PROVOCATION_PHRASES` and `UNCERTAINTY_KEYWORDS`.

## Requirements
- Update the data-flow diagram: remove the `_is_uncertain()` decision node and its YES branch; the flow goes directly from Ollama response to `handlers.py — message.answer()`.
- Update `llm.py` module description: remove mention of `_is_uncertain()`.
- Update `prompts.py` module description: remove `PROVOCATION_PHRASES` and `UNCERTAINTY_KEYWORDS` entries; update count ("2 items" instead of "4 items" if counts are mentioned).
- All other sections (concurrency model, deployment topology) remain unchanged.

## Implementation Notes
- Simplified data-flow after the change:
  ```
  llm.py — ask_llm()
        │  POST /api/chat
        ▼
  Ollama REST API
        │  JSON response → llm_raw
        ▼  (or ERROR_PHRASE on exception)
  handlers.py — message.answer()
  ```

## Definition of Done
- [ ] Data-flow diagram no longer contains `_is_uncertain`, `PROVOCATION_PHRASE`, or YES/NO uncertainty branches
- [ ] `llm.py` module description updated
- [ ] `prompts.py` module description updated
- [ ] Document is internally consistent

## Affected Files / Components
- `docs/architecture.md`

## Risks / Dependencies
- Depends on RPL-01 and RPL-02 being done first.

## Validation Steps
1. Open `docs/architecture.md`.
2. Search for `_is_uncertain`, `PROVOCATION`, `UNCERTAINTY` — none should appear.
3. Verify the data-flow diagram is readable and accurate.

## Follow-ups (optional)
- RPL-06: Update `docs/project-overview.md`.
