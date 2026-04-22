# Architecture

## Runtime Paths

### Standard chat path

```text
User -> Telegram -> handlers.handle_text
     -> Users module (identify; publish UserCreated on first seen)
     -> ChatOrchestrator
     -> EventBus (MessageReceived) -> ConversationService
     -> ChatService -> OllamaGateway (/api/generate stream)
     -> EventBus (ResponseGenerated) -> ConversationService
     -> User
```

### Agent path (`/agent` command or URL in text)

```text
User -> Telegram -> handlers
     -> AgentOrchestrator -> agent.run_agent
     -> OllamaGateway (/api/generate)
     -> parser (tool/args | final_answer)
     -> tool execution (optional)
     -> observation feedback
     -> ... repeat ...
     -> final_answer -> User
```

User-visible contract on agent path:
- No intermediate step messages
- Only final answer, or controlled fallback if loop cannot complete

---

## Core Modules

- `src/bootstrap.py`: synchronous startup bootstrap (settings, model selection, runtime wiring)
- `src/runtime.py`: application container for shared services/dependencies
- `src/handlers.py`: Telegram integration, typing indicator, routing
- `src/services/chat_orchestrator.py`: chat/URL routing orchestration for handlers
- `src/modules/*`: public module boundaries (users/chat/history) and shared contracts
- `src/events/*`: shared event contracts (published/consumed via event bus)
- `src/events/bus.py`: in-memory publish/subscribe event bus
- `src/modules/chat/service.py`: Chat/AI boundary for response generation (uses `OllamaGateway`)
- `src/modules/history/service.py`: History boundary for conversation state and summarization
- `src/conversation.py`: compatibility wrapper over `src/modules/history/service.py`
- `src/ollama_gateway.py`: shared Ollama transport boundary (tags/chat/generate)
- `src/llm.py`: compatibility wrapper over `src/modules/chat/service.py`
- `src/agent/core.py`: iterative agent loop (parsing + tool loop)
- `src/agent/parser.py`: strict JSON contract parsing
- `src/agent/tools.py`: calculator + deterministic HTTP tooling
- `src/prompts.py`: system prompts (chat and agent)
- `src/context_logging.py`: structured context and agent event logging
- `src/config.py`: typed environment-backed settings (`Settings`) with explicit runtime overrides (for selected chat model)

---

## Module Responsibilities

- **Users** (`src/modules/users`): identifies Telegram users and stores in-memory user records.
- **Chat/AI** (`src/modules/chat`): turns prompt/history into an `LLMReply` using `OllamaGateway` (and formats thinking output when enabled).
- **History** (`src/modules/history`): owns in-memory conversation state, trimming, and optional summarization.
- **Orchestration** (`src/services/chat_orchestrator.py`): routes URL vs normal chat and coordinates events (no Telegram imports inside modules).
- **Events** (`src/events`): typed event contracts and an in-memory `EventBus` used for in-process module communication.

Dependency direction:

```text
handlers/runtime -> orchestration -> (Users, Chat/AI, History) + EventBus
Chat/AI and History do not import Telegram handlers.
```

---

## Example Event Flow (standard text)

1. `handlers.handle_text` identifies the user via `UserService`.
2. If new, `UserCreated` is published.
3. `ChatOrchestrator.process_text` publishes `MessageReceived`.
4. History subscriber stores the user message.
5. `ChatService.generate_response` calls `OllamaGateway` and returns `LLMReply`.
6. If successful, `ChatOrchestrator` publishes `ResponseGenerated`.
7. History subscriber stores the assistant reply.

Notes:
- The `EventBus` is **in-memory** and **not durable** (it is not a message broker).
- Subscribers run in-process; failures are contained and logged without stopping other subscribers.

---

## Agent State Model

`AgentResult`:
- `run_id`
- `final_answer`
- `steps`
- `stopped_reason` (`final`, `max_steps`, `error`)

`Step`:
- `action`
- `args`
- `observation`

---

## Determinism and Safety

- Tool protocol strictly enforced (`tool`, `args`, `final_answer`)
- Parser gracefully handles malformed model output
- HTTP tool bounded by timeout and byte limits
- Resource loading is same-origin and limit-controlled
- Event subscriptions are registered in runtime wiring (modules communicate via `EventBus`)
- Structured logging with run correlation supports reproducible debugging

---

## Observability

Agent emits structured JSON-line events with shared `run_id`:
- step lifecycle
- parse failures/retries
- tool call timing and outcome
- terminal reason

This enables end-to-end traceability for multi-step runs.
