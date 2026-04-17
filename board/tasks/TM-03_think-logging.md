# TM-03 - Log thinking content at DEBUG level

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Emit the model's reasoning trace to the debug log so developers can inspect the chain-of-thought without it appearing in production logs.

## Context
After TM-02, `ask_llm()` has access to the `thinking` string. Logging it at DEBUG level gives developers full visibility during local development (where `LOG_LEVEL=DEBUG` is common) while keeping INFO/WARNING logs clean in production. Depends on TM-02.

## Requirements
- Immediately after extracting `thinking`, if it is non-empty, emit: `logging.debug("LLM thinking: %s", thinking)`.
- Log line must appear before the content/thinking selection logic so it is always captured regardless of which branch is taken.
- No changes to INFO-level logging.

## Implementation Notes
- One line addition in `src/llm.py` inside the `try` block, after `thinking = data["message"].get("thinking", "").strip()`.
- No new imports needed.

## Definition of Done
- [ ] `logging.debug("LLM thinking: %s", thinking)` is emitted when `thinking` is non-empty.
- [ ] Nothing is logged at INFO or WARNING level for the thinking content.
- [ ] With `LOG_LEVEL=DEBUG` the reasoning trace appears in the console.
- [ ] With `LOG_LEVEL=INFO` the reasoning trace is absent.

## Affected Files / Components
- `src/llm.py`

## Risks / Dependencies
- Depends on TM-02.
- Thinking traces can be very long (thousands of tokens) — acceptable at DEBUG but would be noisy at higher levels.

## Validation Steps
1. Set `OLLAMA_THINK=true` and `LOG_LEVEL=DEBUG`, send a message, confirm thinking trace appears.
2. Set `LOG_LEVEL=INFO`, send a message, confirm thinking trace is absent.
3. Set `OLLAMA_THINK=false`, confirm no thinking log line appears.
