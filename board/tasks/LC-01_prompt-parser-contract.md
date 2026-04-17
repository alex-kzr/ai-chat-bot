# LC-01 - Align prompt and parser with the required JSON contract

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Bring the LLM-agent protocol into line with the required response contract so the agent can process only valid, deterministic outputs.

## Context
`board/prompts/prompt_7_agentic_loop.xml` requires the model to respond with either `{"final_answer": "..."}` or `{"tool": "...", "args": {...}}`. The current implementation uses older action-oriented structures, which makes the runtime incompatible with the target flow.

## Requirements
- Update the system prompt so it documents only the required `final_answer` and `tool` JSON shapes.
- Update the parser to validate `tool` calls through `{"tool": "name", "args": {...}}`.
- Gracefully handle malformed JSON, missing keys, or invalid types without crashing the loop.

## Implementation Notes
- Update `build_agent_prompt()` or the equivalent prompt assembly in `src/prompts.py`.
- Keep JSON extraction resilient for fenced code blocks and mixed text, but deterministic.
- Return structured parse errors that the core loop can log and recover from.

## Definition of Done
- [ ] The prompt and parser accept only the required JSON contract
- [ ] Invalid model output is handled gracefully
- [ ] Final-answer parsing still works without regression
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/prompts.py`
- `src/agent/parser.py`
- `board/prompts/prompt_7_agentic_loop.xml`

## Risks / Dependencies
- Dependency: `LC-02` consumes the parser output models and error behaviour.
- Risk: overly strict validation could reject slightly noisy but recoverable model responses.

## Validation Steps
1. Parse a valid `{"tool": "http_request", "args": {"url": "https://example.com"}}` response.
2. Parse a valid `{"final_answer": "Done"}` response.
3. Pass malformed JSON and confirm the parser returns a controlled error instead of crashing.

## Follow-ups (optional)
- Add table-driven parser tests for edge-case extraction and validation.
