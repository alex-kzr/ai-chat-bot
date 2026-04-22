# MM-02 - Introduce Users module

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Add a dedicated Users module that owns user identification and in-memory user records.

## Context
Telegram handlers currently read `message.from_user.id` directly and pass the numeric ID through the chat flow. The modular monolith needs a Users boundary that can later support persistence or richer profiles.

## Requirements
- Create a Users module with its own folder and public interface.
- Identify users by Telegram ID and optional username.
- Store user records in memory.
- Return an existing user record for repeat interactions.
- Do not let other modules access Users internals directly.

## Implementation Notes
- Consider `User`, `UserService`, and an in-memory repository inside `src/modules/users`.
- Keep Telegram-specific extraction in handlers or an adapter; keep the Users module focused on identification records.
- Prepare the module to emit or support `UserCreated` in EB-03.

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
- `src/modules/users/`
- `src/handlers.py`
- `src/runtime.py`
- `tests/`

## Risks / Dependencies
- Must preserve existing per-user history identity semantics.
- Depends on MM-01 public boundary decisions.

## Validation Steps
1. Call the Users public service with a Telegram ID and username.
2. Call it again with the same Telegram ID.
3. Expected result: one stable user record is reused and no module imports private Users internals.
