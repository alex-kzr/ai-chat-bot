# MM-04 - Isolate History module

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Move conversation history behavior behind a dedicated History module interface.

## Context
`src/conversation.py` currently owns in-memory history, trimming, pending summaries, and summarization orchestration. The modular monolith needs this behavior isolated behind a clear History boundary.

## Requirements
- Create a History module with its own folder and public interface.
- Support appending messages, retrieving the last N messages, clearing history, trimming, and summarization behavior.
- Keep storage in memory.
- Do not expose mutable internal lists to consumers.

## Implementation Notes
- Preserve the existing copy-on-read behavior from `ConversationService.get_history`.
- Keep summarization dependencies injected.
- Prepare subscriber methods for `MessageReceived` and `ResponseGenerated` events in EB-02.

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
- `src/modules/history/`
- `src/conversation.py`
- `src/runtime.py`
- `tests/test_conversation_service.py`

## Risks / Dependencies
- History trimming and summarization behavior are easy to break during relocation.
- Depends on MM-01 module boundary decisions.

## Validation Steps
1. Run existing conversation service tests.
2. Add or update tests that mutate returned history and then read it again.
3. Expected result: history behavior remains stable and internal state is protected.
