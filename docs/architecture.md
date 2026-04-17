# Architecture

## Runtime Paths

### Standard chat path

```text
User -> Telegram -> handlers.handle_text
     -> ChatOrchestrator
     -> ConversationService (trim/summarize)
     -> OllamaGateway (/api/generate stream)
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
- `src/conversation.py`: in-memory conversation state + summarization boundary
- `src/ollama_gateway.py`: shared Ollama transport boundary (tags/chat/generate)
- `src/llm.py`: chat reply composition built on top of the gateway
- `src/agent/core.py`: iterative agent loop (parsing + tool loop)
- `src/agent/parser.py`: strict JSON contract parsing
- `src/agent/tools.py`: calculator + deterministic HTTP tooling
- `src/prompts.py`: system prompts (chat and agent)
- `src/context_logging.py`: structured context and agent event logging
- `src/config.py`: typed environment-backed settings (`Settings`) with explicit runtime overrides (for selected chat model)

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
- Structured logging with run correlation supports reproducible debugging

---

## Observability

Agent emits structured JSON-line events with shared `run_id`:
- step lifecycle
- parse failures/retries
- tool call timing and outcome
- terminal reason

This enables end-to-end traceability for multi-step runs.
