# HS-02 - Add summarization prompt to prompts.py

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide a dedicated `SUMMARIZATION_PROMPT` in `src/prompts.py` that the summarizer module will inject as a system instruction when asking the LLM to compress dialogue history.

## Context
`src/prompts.py` already contains `SYSTEM_PROMPT` and `ERROR_PHRASES`. A separate summarization prompt is needed so the LLM receives clear, structured instructions to produce a fact-preserving summary rather than a freeform continuation.

The prompt must:
- Preserve main topic and user goals.
- Preserve key technical details, decisions, and constraints.
- Capture any open questions or unresolved items.
- Avoid hallucinating facts not present in the input.
- Output a compact, structured block (not a long narrative).

## Requirements
- Add `SUMMARIZATION_PROMPT: str` to `src/prompts.py`.
- The prompt must instruct the LLM to output a summary covering: topic, user goals, key technical details, decisions / constraints, open questions.
- Must explicitly tell the LLM NOT to add information absent from the input.
- Must be written in the same language policy as `SYSTEM_PROMPT` (English system instruction; LLM responds in the user's language).
- The constant name must be `SUMMARIZATION_PROMPT` (imported by `src/summarizer.py` in HS-03).

## Implementation Notes
Example structure for the prompt:

```
You are a conversation summarizer. Given the following chat history between a user and an assistant, produce a concise summary.

Include:
- Main topic of the conversation
- User's goals and intent
- Key technical details, tools, or technologies mentioned
- Decisions made and constraints agreed upon
- Any open questions or unresolved items

Rules:
- Do NOT add any information not present in the provided messages.
- Be concise: aim for 5–10 bullet points or a short structured paragraph.
- Write in the same language the user is using.

Output only the summary — no preamble, no closing remarks.
```

## Definition of Done
- [ ] `SUMMARIZATION_PROMPT` constant added to `src/prompts.py`
- [ ] Covers all required fields (topic, goals, details, decisions, open questions)
- [ ] Explicitly prohibits hallucination
- [ ] Importable from `src.prompts`
- [ ] No changes to existing constants

## Affected Files / Components
- `src/prompts.py`

## Risks / Dependencies
- HS-03 imports `SUMMARIZATION_PROMPT` — must exist before HS-03 is implemented.

## Validation Steps
1. `from src.prompts import SUMMARIZATION_PROMPT` — no ImportError.
2. Inspect the string; confirm it mentions topic, goals, constraints, open questions.
3. Confirm existing `SYSTEM_PROMPT` and `ERROR_PHRASES` are unchanged.

## Follow-ups (optional)
- The prompt can be refined iteratively based on observed summary quality without touching any logic files.
