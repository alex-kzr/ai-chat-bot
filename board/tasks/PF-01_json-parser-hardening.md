# PF-01 - Harden JSON extraction and schema validation

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Make the parser resilient to markdown-wrapped JSON, noisy model output, and malformed payloads without silently misclassifying responses.

## Context
The prompt requires the parser to extract JSON from markdown, tolerate surrounding noise, validate schema, and distinguish action steps, final answers, and invalid responses. The current parser already handles fenced JSON and balanced objects, but it needs stronger hardening for messy local-model output.

## Requirements
- Extract valid JSON even when the model adds prose or markdown around it.
- Validate the schema for tool calls and final answers deterministically.
- Return structured parse failures instead of ambiguous fallthrough behavior.

## Implementation Notes
- Extend `src/agent/parser.py` with stricter extraction and validation helpers.
- Keep the output contract explicit so `src/agent/core.py` can decide between retry and termination without reinterpreting parser state.
- Preserve compatibility with the existing tool contract unless a small prompt adjustment is necessary.

## Testing
- [x] Unit tests
- [x] Integration tests
- [ ] Manual testing

## Definition of Done
- [ ] JSON inside markdown or noisy wrappers is parsed when valid
- [ ] Invalid payloads are rejected with structured parser errors
- [ ] Tool and final-answer schemas are validated consistently
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/parser.py`
- `src/agent/core.py`
- `docs/algorithms.md`

## Risks / Dependencies
- Dependency: `PF-02` will rely on explicit parser outcomes for retry enforcement.
- Risk: more permissive extraction must not accidentally parse the wrong JSON object from unrelated text.

## Validation Steps
1. Parse valid fenced JSON and confirm the result matches the schema.
2. Parse noisy markdown with one valid JSON object and confirm extraction still succeeds.
3. Feed malformed JSON and confirm a controlled parse failure is returned.

## Follow-ups (optional)
- Add parser metrics for extracted-vs-rejected payload ratios.
