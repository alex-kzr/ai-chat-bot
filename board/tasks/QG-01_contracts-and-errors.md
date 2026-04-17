# QG-01 - Add explicit contracts and domain exceptions

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Improve readability and safety by replacing loosely typed dictionaries and broad exception handling with explicit contracts and narrower failure categories.

## Context
The current codebase uses many plain `dict` payloads and several broad `except Exception` blocks across LLM, summarization, tools, and agent flow. The `python-error-handling`, `python-type-safety`, and `python-anti-patterns` skills all recommend clear exception hierarchies and typed public signatures.

## Requirements
- Define typed models or aliases for chat messages, tool arguments, tool observations, and key Ollama responses.
- Introduce domain-specific exceptions for configuration errors, transport errors, parse errors, and tool failures.
- Narrow broad exception handlers where the failure modes are known and actionable.

## Implementation Notes
- Reuse existing parser contracts where they are already explicit, but lift them into stronger typed interfaces.
- Keep tool error strings deterministic if the agent prompt depends on them.
- Avoid over-engineering; add explicit contracts first on public boundaries and hot paths.

## Definition of Done
- [x] Feature implemented
- [x] Works as expected
- [x] No regressions
- [x] Code is clean and consistent
- [x] Documentation is updated

## Affected Files / Components
- src/agent/parser.py
- src/agent/core.py
- src/agent/tools.py
- src/llm.py
- src/summarizer.py
- src/context_logging.py

## Risks / Dependencies
- Works best after RS-01 through RS-03 establish cleaner boundaries.
- Error-message changes may affect tests or operator expectations if done carelessly.

## Validation Steps
1. Run parser and tool failure scenarios and verify each failure maps to a specific exception or controlled result.
2. Confirm public function signatures are fully type-annotated and no longer depend on ambiguous raw dict contracts where avoidable.
3. Verify logs still contain actionable failure information after narrowing exceptions.

## Follow-ups (optional)
- Add strict type-checking gradually per module once the contracts settle.
