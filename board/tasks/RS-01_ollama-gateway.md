# RS-01 - Extract Ollama gateway and request models

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Centralize all Ollama HTTP interactions behind a dedicated client abstraction so transport behavior, payload shaping, and failures are handled consistently.

## Context
Ollama requests are currently split across `src/bot.py`, `src/llm.py`, `src/summarizer.py`, and `src/agent/core.py`. That duplicates transport setup, exception handling, and response parsing. The `python-design-patterns`, `python-error-handling`, and `python-resilience` skills all point toward a dedicated gateway boundary.

## Requirements
- Create a shared Ollama client or gateway responsible for model discovery, chat/generate requests, and summary requests.
- Consolidate timeout handling and transport-level error mapping.
- Introduce typed request/response DTOs or helper models for Ollama payloads and parsed responses.

## Implementation Notes
- Keep streaming behavior for normal chat and agent flows where currently required.
- Avoid retry duplication if transport-level retries are later introduced.
- Design the gateway so tests can stub network behavior without patching multiple modules.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- src/llm.py
- src/summarizer.py
- src/bot.py
- src/agent/core.py
- src/config.py

## Risks / Dependencies
- Depends on CB-01 and CB-03 because the gateway should be built from shared settings and logging.
- Streaming and thinking-output behavior must remain backward-compatible.

## Validation Steps
1. Verify regular chat requests still return content and optional thinking output.
2. Verify summarization requests still produce summary text and controlled fallbacks on errors.
3. Verify agent loop requests still operate across multiple steps with the shared gateway.

## Follow-ups (optional)
- Introduce transport metrics or retry policies once the API boundary is stable.
