# TTD-01 - Inject runtime override seam

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Provide an explicit, well-documented way for tests to swap in a fake `Runtime` without monkey-patching module internals. Today, handler tests would have to reach into `src/runtime.py`'s private state.

## Context
- `src/runtime.py` exposes `get_runtime()` reading a module-level singleton.
- Tests currently use `monkeypatch.setattr` on the module — fragile against renames.

## Requirements
- Add to `src/runtime.py`:
  - `set_runtime_for_testing(runtime: Runtime) -> None` — overrides the singleton.
  - `reset_runtime_for_testing() -> None` — restores the previous value (typically `None`).
  - Or, equivalently, a `runtime_override(runtime)` context manager.
- Add a session-level fixture in `tests/conftest.py` that uses these helpers and yields a `fake_runtime`.
- Update `get_runtime()` to read the override transparently if set.
- Public app behavior must be unchanged when no override is active.
- Mark the helpers clearly (`# Test-only helper.` line; do not document in user docs).

## Implementation Notes
- Single small change; do not refactor the rest of `runtime.py`.
- Avoid `contextvars` unless concurrent test isolation becomes necessary.
- Keep helpers async-agnostic.

## Testing
- [x] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Definition of Done
- [x] `set_runtime_for_testing` / `reset_runtime_for_testing` (or `runtime_override`) available.
- [x] `get_runtime()` returns the override when one is active.
- [x] Existing tests still pass without modification.
- [x] At least one new test confirms override + reset cycle.

## Affected Files / Components
- `src/runtime.py`
- `tests/conftest.py`

## Risks / Dependencies
- Risk: tests forget to reset, leaking runtime across tests. Mitigation: fixture auto-resets on teardown.

## Validation Steps
1. `pytest -q` — full suite passes.
2. Write a tiny test that overrides → calls `get_runtime()` → asserts identity → resets → asserts old value restored.
3. Verify no production caller of `get_runtime()` regressed (grep `get_runtime`).

## Follow-ups (optional)
- Migrate handlers to receive `Runtime` as an explicit parameter once aiogram middleware injection is wired (out of scope).
