# RS-02 - Encapsulate conversation state and summarization

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make conversation history and summarization behavior explicit behind a focused service instead of a shared mutable module-level store.

## Context
`src/history.py` uses a module-global dictionary and trims based on a directly imported config constant. `src/summarizer.py` reaches into the same storage and coordinates replacement logic externally. That mixes storage policy, summarization policy, and orchestration.

## Requirements
- Introduce a conversation-state service or repository that owns history reads and writes.
- Move trimming, replacement, and summary-boundary decisions behind the service API.
- Keep the current in-memory storage model, but structure it so a persistent backend can be added later without rewriting handlers.

## Implementation Notes
- Preserve the current user-facing behavior for history accumulation and summary insertion.
- Make “summary entry” creation a clear domain operation rather than ad hoc dict construction spread across modules.
- Keep APIs type-annotated and deterministic for tests.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- src/history.py
- src/summarizer.py
- src/handlers.py
- src/llm.py

## Risks / Dependencies
- Depends on RS-01 if summarization LLM calls are routed through the shared Ollama gateway.
- State behavior is easy to regress, so tests must cover trimming and summary replacement rules.

## Validation Steps
1. Send multiple messages for one user and verify history growth and trimming remain correct.
2. Cross the summary threshold and verify older messages are replaced by one summary entry plus recent messages.
3. Confirm user histories remain isolated from each other.

## Follow-ups (optional)
- Add storage backend abstraction if persistent history becomes a future requirement.
