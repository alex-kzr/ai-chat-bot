# 📋 Tasks — Modular Monolith and Event-Driven Chat Flow
---

## Phase 1 — Modular Monolith Foundation

### MM-01 Define module boundaries and shared contracts
Create the target module layout and shared public contracts for users, chat/AI, history, and events so implementation tasks have stable interfaces to follow.
→ [MM-01_define-module-boundaries.md](./tasks/MM-01_define-module-boundaries.md)

### MM-02 Introduce Users module
Add a Users module responsible for identifying Telegram users and storing in-memory user records behind a public service interface.
→ [MM-02_introduce-users-module.md](./tasks/MM-02_introduce-users-module.md)

### MM-03 Isolate Chat/AI module
Move chat response generation behind a Chat/AI module interface that owns LLM interaction and keeps Telegram handlers independent from AI internals.
→ [MM-03_isolate-chat-ai-module.md](./tasks/MM-03_isolate-chat-ai-module.md)

### MM-04 Isolate History module
Move message history operations behind a History module interface that owns append, retrieval, trimming, and summarization boundaries.
→ [MM-04_isolate-history-module.md](./tasks/MM-04_isolate-history-module.md)

## Phase 2 — Event Bus and Integration

### EB-01 Implement in-memory event bus
Create a lightweight typed event bus with publish/subscribe support, structured logging, and safe handler execution.
→ [EB-01_implement-in-memory-event-bus.md](./tasks/EB-01_implement-in-memory-event-bus.md)

### EB-02 Wire module subscriptions
Register History module subscribers for chat events and wire event bus dependencies through runtime/bootstrap without hidden globals.
→ [EB-02_wire-module-subscriptions.md](./tasks/EB-02_wire-module-subscriptions.md)

### EB-03 Publish chat flow events
Update the user message flow to publish `UserCreated`, `MessageReceived`, and `ResponseGenerated` events while preserving current Telegram behavior.
→ [EB-03_publish-chat-flow-events.md](./tasks/EB-03_publish-chat-flow-events.md)

## Phase 3 — Validation and Documentation

### VD-01 Add modular event-flow tests
Add focused tests for module boundaries, event bus behavior, event subscriptions, and the user-message-to-history flow.
→ [VD-01_add-modular-event-flow-tests.md](./tasks/VD-01_add-modular-event-flow-tests.md)

### VD-02 Document architecture decisions
Update README and docs with the modular monolith layout, event flow, public interfaces, and an example request lifecycle.
→ [VD-02_document-architecture-decisions.md](./tasks/VD-02_document-architecture-decisions.md)

---
