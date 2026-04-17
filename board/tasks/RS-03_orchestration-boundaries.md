# RS-03 - Slim Telegram handlers and agent orchestration

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Reduce handler and agent modules to orchestration-only code so transport adapters do not carry business rules, formatting decisions, and domain flow all at once.

## Context
`src/handlers.py` currently handles routing, typing indicators, URL-based agent switching, history mutation, summarization trigger, LLM invocation, thinking formatting, and response logging. `src/agent/core.py` also mixes loop control, transport calls, parsing, logging, and fallback composition.

## Requirements
- Extract chat-processing and agent-run orchestration into dedicated services or use-case functions.
- Keep Telegram handlers responsible for Telegram concerns only: routing, message extraction, and final reply delivery.
- Reduce hidden coupling between parser, tool execution, and user-facing fallback messages.

## Implementation Notes
- Preserve the current “final answer only” contract for agent replies.
- Consider a small application-service layer that returns user-facing response objects to handlers.
- Keep typing indicator behavior, but isolate it from business logic where possible.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- src/handlers.py
- src/agent/core.py
- src/agent/parser.py
- src/agent/tools.py
- src/llm.py

## Risks / Dependencies
- Depends on RS-01 and RS-02 because orchestration boundaries should call the new services rather than legacy helpers.
- Telegram-visible behavior must remain stable while internal structure changes significantly.

## Validation Steps
1. Verify `/start`, regular text, URL text, and `/agent` routes still produce the same user-visible outcomes.
2. Confirm agent fallback behavior still returns a controlled message when no final answer is produced.
3. Review handlers and agent modules to ensure business logic moved into dedicated services/helpers.

## Follow-ups (optional)
- Introduce separate modules for response formatting and typing-indicator lifecycle management.
