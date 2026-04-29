# BLC-02 - Cover HistoryService trim and summarization

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Verify the deterministic history-management contract: append, trim at `MAX_HISTORY_MESSAGES`, and summarization trigger. These are the rules that prevent the prompt from growing unbounded.

## Context
- `src/modules/history/service.py` owns in-memory per-user history.
- `src/summarizer.py` performs LLM-backed summarization (must be mocked).
- Settings: `MAX_HISTORY_MESSAGES`, summarization threshold, summarization-on flag.

## Requirements
Add `tests/test_history_service_logic.py`:
- Appending below the limit keeps every message in order.
- Appending past the limit drops the oldest first; the most recent N are preserved (parametrize: limits 2, 4, 10).
- When summarization is enabled and the threshold is crossed, the summarizer is called once with the older messages; the resulting summary replaces them in history.
- When summarization is disabled, crossing the threshold simply trims (no summarizer call).
- Per-user isolation: appending to user A does not affect user B.

## Implementation Notes
- Mock `summarizer.summarize` with `AsyncMock(return_value="SUMMARY")`.
- Use a deterministic small `MAX_HISTORY_MESSAGES` in `fake_settings` (e.g. 4).
- Cover both branches of the on/off flag with `@pytest.mark.parametrize`.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] Trim/append/summarize behavior covered.
- [x] Per-user isolation verified.
- [x] Summarizer mocked — no LLM call.

## Affected Files / Components
- `tests/test_history_service_logic.py` (new)
- `src/modules/history/service.py` (read-only)

## Risks / Dependencies
- Depends on TF-01 (`fake_settings`).

## Validation Steps
1. `pytest -q tests/test_history_service_logic.py` — passes.
2. Temporarily comment out `trim_history()` in service — at least one test fails.
3. Full suite green.

## Follow-ups (optional)
- Add a stress test for very long histories once persistence lands (out of scope).
