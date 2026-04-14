# RPL-04 - Update docs/algorithms.md

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
`docs/algorithms.md` documents the "Uncertainty Detection" algorithm (`_is_uncertain`) in detail. After removing the function this section becomes stale and misleading. It must be removed and the "LLM Request / Response" section updated to reflect the simplified flow.

## Context
- File: `docs/algorithms.md`
- Section 1 "Uncertainty Detection (`_is_uncertain`)" (lines 1–29): full description of the removed function.
- Section 4 "LLM Request / Response (`ask_llm`)" (lines 84–108): references `_is_uncertain()` in step 4 of the algorithm pseudocode.

## Requirements
- Delete Section 1 "Uncertainty Detection" entirely.
- Update Section 4 pseudocode: remove step 4 (`If _is_uncertain(...): return provocation`) — `ask_llm` now returns `(llm_raw, llm_raw)` directly after extracting the content.
- Renumber remaining sections if needed to keep them sequential.
- Do not change sections for Model Selection or Typing Indicator — they are unaffected.

## Implementation Notes
- Updated `ask_llm` pseudocode after the change:
  ```
  1. Build payload: {model, messages: [system_prompt, user_text], stream: false}
  2. POST {OLLAMA_URL}/api/chat  (timeout = config.OLLAMA_TIMEOUT)
     On any exception:
       log error
       return ("[error]", random(ERROR_PHRASES))
  3. llm_raw = response.json()["message"]["content"].strip()
  4. return (llm_raw, llm_raw)
  ```

## Definition of Done
- [ ] "Uncertainty Detection" section removed from `algorithms.md`
- [ ] `ask_llm` pseudocode no longer references `_is_uncertain` or `PROVOCATION_PHRASES`
- [ ] Remaining sections renumbered sequentially
- [ ] Document is consistent with actual code after RPL-01 and RPL-02

## Affected Files / Components
- `docs/algorithms.md`

## Risks / Dependencies
- Depends on RPL-01 and RPL-02 being done first (so the doc reflects actual code state).

## Validation Steps
1. Open `docs/algorithms.md`.
2. Confirm no mention of `_is_uncertain`, `UNCERTAINTY_KEYWORDS`, or `PROVOCATION_PHRASES`.
3. Verify `ask_llm` pseudocode matches the simplified implementation in `llm.py`.

## Follow-ups (optional)
- RPL-05: Update `docs/architecture.md` data-flow diagram.
