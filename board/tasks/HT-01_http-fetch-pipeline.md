# HT-01 - Implement a deterministic HTML fetch pipeline

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Build a predictable HTML fetch pipeline for the `http_request` tool so the agent can retrieve web pages safely and consistently.

## Context
The requirements call for an HTTP tool that can fetch full HTML content and feed a processed result back into the loop. The current tool path is too limited and does not provide a stable fetch contract.

## Requirements
- Perform HTTP requests with fixed timeout, redirect policy, and request headers.
- Fetch full HTML content within explicit response-size safety limits.
- Normalize URL and encoding handling before returning the response body.

## Implementation Notes
- Split network fetching from result formatting inside `src/agent/tools.py`.
- Add bounded response-size checks and explicit tool errors when limits are exceeded.
- Keep request settings deterministic so debugging and reproduction stay simple.

## Definition of Done
- [ ] The tool can fetch HTML content reliably
- [ ] Network and timeout failures return a controlled tool error format
- [ ] Response size is bounded by configuration or explicit limits
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/tools.py`
- `src/config.py`
- `docs/api.md`

## Risks / Dependencies
- Dependency: `LC-02` must execute the tool in the loop.
- Risk: limits that are too strict may cut off useful content, while loose limits may hurt latency.

## Validation Steps
1. Fetch a stable HTML page and confirm the response contains the expected document body.
2. Trigger a timeout scenario and confirm the tool returns a controlled error.
3. Test redirect handling and confirm the final fetch result is deterministic.

## Follow-ups (optional)
- Extract HTTP tool settings into a dedicated configuration block.
