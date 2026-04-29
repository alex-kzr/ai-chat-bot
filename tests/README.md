# Tests

All tests live flat under `tests/` and are runnable with a single command:

```bash
pytest
```

## File-prefix convention

| Prefix | What it covers |
|---|---|
| `test_*_logic.py` | Business logic — pure functions and service classes |
| `test_handlers_*.py` | Telegram handler layer (`src/handlers.py`) with a fake runtime |
| `test_security_*.py` | Security controls (SSRF, injection, rate limiting, input limits) |

## Pytest markers

Three markers are registered (see `pyproject.toml`):

| Marker | Meaning |
|---|---|
| `unit` | Pure-logic test — no I/O, no network |
| `handlers` | Exercises `src/handlers.py` end-to-end with a stubbed runtime |
| `integration` | Wires multiple real modules together |

Run a specific subset:

```bash
pytest -m unit        # only unit tests
pytest -m handlers    # only handler tests
pytest -m integration # only integration tests
pytest -m "not integration"  # skip integration tests
```

## Async support

`asyncio_mode = "auto"` in `pyproject.toml` means every `async def test_*` function
runs automatically inside an event loop — no `@pytest.mark.asyncio` decorator needed.

## Shared fixtures

`tests/conftest.py` provides:

- `fake_settings` — deterministic `Settings` (session-scoped)
- `event_bus` — fresh `EventBus` per test
- `user_service` — fresh `UserService` per test
- `rate_limiter` — `AsyncMock` that always allows (flip `.is_allowed.return_value = False` to deny)
- `chat_orchestrator` / `agent_orchestrator` — `AsyncMock`s with realistic return shapes
- `fake_runtime` — `AppRuntime` composing all of the above

## Test doubles

`tests/_fakes.py` exports:

- `FakeOllamaGateway(script=[...])` — scripted Ollama stand-in; no network
- `make_message(text, user_id, username, chat_id)` — aiogram `Message` mock
- `make_message_with_failing_answer(exc)` — same but `answer()` raises
