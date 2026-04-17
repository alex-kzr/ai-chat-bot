# HT-03 - Build an LLM-friendly processed page result

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Define a structured and compact output format for the HTTP tool so the next LLM iteration can reason over the page result reliably.

## Context
Raw HTML and resource bodies are too noisy to pass back into the agent loop directly. The tool must return a deterministic observation containing the most relevant page information and diagnostics.

## Requirements
- Return a stable result that includes URL, status, title, main text, and resource summary.
- Keep the observation size bounded for safe use in the LLM context window.
- Include enough diagnostics to explain what was fetched and what was skipped.

## Implementation Notes
- Choose a single structured result shape, such as a compact JSON-like or Markdown block.
- Strip scripts and styles from the main content extraction.
- Keep formatting deterministic so logs and manual checks are easy to compare.

## Definition of Done
- [ ] The HTTP tool returns one structured observation format
- [ ] The result is useful for the next reasoning step
- [ ] Observation length is bounded
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/tools.py`
- `src/prompts.py`
- `docs/api.md`

## Risks / Dependencies
- Dependency: `HT-01` and `HT-02` must provide the raw fetch and resource data.
- Risk: over-compressing the result may remove details the model needs for reasoning.

## Validation Steps
1. Fetch a static site and confirm the output includes URL, status, title, main text, and resource summary.
2. Verify scripts and styles are excluded from the main text section.
3. Confirm the observation remains within the configured or documented size limit.

## Follow-ups (optional)
- Add an optional raw-debug attachment mode for offline diagnostics.
