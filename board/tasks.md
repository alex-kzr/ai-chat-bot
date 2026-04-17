# 📋 Tasks — Project-Wide Python Refactoring
---

## Phase 1 — Configuration & Bootstrap

### CB-01 Introduce typed settings object
Replace module-level environment reads in `src/config.py` with an explicit typed settings object that validates inputs, owns defaults, and removes fragile `from src.config import ...` coupling.
→ [CB-01_typed-settings.md](./tasks/CB-01_typed-settings.md)

### CB-02 Refactor startup and model selection flow
Move startup orchestration into a clear bootstrap path that performs environment loading, model discovery, and runtime model selection without blocking inside async handlers or mutating hidden globals.
→ [CB-02_startup-bootstrap.md](./tasks/CB-02_startup-bootstrap.md)

### CB-03 Centralize logging and runtime wiring
Unify application logging setup, context logger configuration, and runtime dependency wiring so console/file logging, bot startup logs, and debug output are configured from one place.
→ [CB-03_logging-runtime-wiring.md](./tasks/CB-03_logging-runtime-wiring.md)

## Phase 2 — Runtime Services & State

### RS-01 Extract Ollama gateway and request models
Create a dedicated Ollama client layer shared by chat, summarization, agent, and model-discovery flows so HTTP settings, retries, payload construction, and error mapping are centralized.
→ [RS-01_ollama-gateway.md](./tasks/RS-01_ollama-gateway.md)

### RS-02 Encapsulate conversation state and summarization
Refactor in-memory history and summarization into an explicit conversation-state service with clear APIs for read, append, trim, summarize, and replace operations.
→ [RS-02_conversation-state.md](./tasks/RS-02_conversation-state.md)

### RS-03 Slim Telegram handlers and agent orchestration
Reduce `handlers.py` and agent runtime modules to orchestration-only code by moving business rules, formatting, and fallback decisions into dedicated services or helper modules.
→ [RS-03_orchestration-boundaries.md](./tasks/RS-03_orchestration-boundaries.md)

## Phase 3 — Quality Gates & Safety

### QG-01 Add explicit contracts and domain exceptions
Introduce typed request/response models plus custom exception classes for configuration, Ollama transport, agent parsing, and tool failures so broad `except Exception` blocks can be narrowed.
→ [QG-01_contracts-and-errors.md](./tasks/QG-01_contracts-and-errors.md)

### QG-02 Expand automated test coverage for critical flows
Build focused unit and integration-style tests for config parsing, conversation state, Ollama client behavior, parser/tool execution, and Telegram-facing orchestration paths.
→ [QG-02_test-coverage.md](./tasks/QG-02_test-coverage.md)

### QG-03 Add static quality tooling and documentation sync
Add project-level developer tooling for pytest, linting, and type checking, then update docs so architecture and runbooks describe the refactored structure rather than the legacy layout.
→ [QG-03_quality-tooling-docs.md](./tasks/QG-03_quality-tooling-docs.md)

---
