# PF-03 - Align prompt and runtime with model-agnostic stop conditions

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make stop behavior robust across different local and OpenAI-compatible model backends, even when chat templates and EOS handling differ.

## Context
The prompt explicitly calls out missing stop sequences, EOS handling issues, max-token misconfiguration, and incompatible prompt formats as potential root causes. The fix must remain universal rather than tuned for one model only.

## Requirements
- Review and normalize stop-sequence, EOS, and max-token handling across the agent runtime.
- Confirm the prompt format does not depend on one backend-specific chat template.
- Ensure backend-specific differences fail safely instead of causing endless generation.

## Implementation Notes
- Review `src/ollama_gateway.py`, `src/prompts.py`, and any OpenAI-compatible request formatting paths.
- Prefer explicit runtime boundaries over fragile backend-specific hacks.
- Document any backend assumptions that cannot be fully normalized today.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] Stop-condition handling is explicit and documented
- [ ] Prompt/runtime behavior remains model-agnostic
- [ ] Misconfigured backend responses fail with controlled termination
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/ollama_gateway.py`
- `src/prompts.py`
- `docs/project-overview.md`

## Risks / Dependencies
- Dependency: `GW-03` and `PF-02` provide the runtime fallback paths when backend termination signals are missing.
- Risk: backend differences may require careful defaults to avoid breaking current Ollama behavior.

## Validation Steps
1. Inspect request construction and confirm stop-related parameters are explicit where supported.
2. Simulate a backend that omits expected terminal markers and confirm the runtime still aborts safely.
3. Verify current Ollama-based flows continue to work with the normalized contract.

## Follow-ups (optional)
- Add backend capability flags if future runtimes need small targeted overrides.
