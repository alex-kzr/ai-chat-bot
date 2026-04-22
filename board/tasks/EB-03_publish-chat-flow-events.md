# EB-03 - Publish chat flow events

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Update the request flow so user, message, and response lifecycle events are published during normal chat processing.

## Context
The assignment requires `UserCreated`, `MessageReceived`, and `ResponseGenerated`. The current chat flow appends user and assistant messages directly through the conversation service.

## Requirements
- Publish `UserCreated` when a new user is identified.
- Publish `MessageReceived` when a user text message enters the standard chat flow.
- Publish `ResponseGenerated` after a successful AI response.
- Remove direct Chat/AI-to-History calls wherever event publication can replace them.
- Preserve existing fallback behavior for LLM errors and empty replies.

## Implementation Notes
- Keep Telegram handler behavior unchanged from the user's perspective.
- Make event payloads contain stable IDs and content needed by subscribers.
- Do not publish assistant history events for failed `"[error]"` LLM responses unless explicitly required by the final design.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- `src/handlers.py`
- `src/services/chat_orchestrator.py`
- `src/modules/users/`
- `src/modules/chat/`
- `src/modules/history/`
- `src/events/`
- `tests/`

## Risks / Dependencies
- Event ordering matters because history must include the user message before response generation.
- Depends on EB-01 and EB-02.

## Validation Steps
1. Send a standard text message through the orchestrator in a test.
2. Inspect published events and stored history.
3. Expected result: user and assistant messages are stored via event subscribers, and the Telegram reply remains unchanged.
