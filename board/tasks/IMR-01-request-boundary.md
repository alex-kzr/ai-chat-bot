# IMR-01 - Identify LLM request boundary and injection points

## Status
- [x] To Do
- [x] In Progress
- [x] Done 

## Purpose
Analyze the current LLM request flow in `src/llm.py` to identify the exact point(s) where logging should be injected. This task ensures we understand the code structure and can integrate logging without breaking the existing flow.

## Context
The LLM request boundary is where:
- All context (system prompt, history, user message) is assembled
- The final payload is ready to be sent to the model
- We have access to all information needed for logging

Currently, this is in `src/llm.py` in the `ask_llm()` function. We need to map out:
- Where the messages list is assembled
- Where the request is actually sent to the model
- What happens before and after the request
- Are there multiple code paths (retries, different models)?
- What metadata is available at the logging point?

## Requirements
- Read and analyze `src/llm.py` thoroughly
- Identify the exact line(s) where logging should be inserted
- Document all code paths in the LLM request flow
- Identify what data is available at each potential injection point
- Create a summary document describing:
  - The current request flow (as a step-by-step description or diagram)
  - The recommended injection point(s) for logging
  - What data needs to be captured at each point
  - Any constraints or gotchas (e.g., exception handling, retries)
- Verify that the chosen injection point(s) will capture ALL requests (no hidden code paths)

## Implementation Notes
- This is an analysis task, not a coding task
- Focus on understanding before making changes
- Look for:
  - Entry point of `ask_llm()`
  - Where messages are assembled
  - Error handling and retries
  - Response handling
  - Any special cases (streaming, batch requests, etc.)
- Document findings in a clear, concise way that the next task (IMR-02) can use directly

## Definition of Done
- [x] `src/llm.py` analyzed completely
- [x] Request flow documented and understood
- [x] Recommended injection point(s) identified
- [x] All code paths verified to be covered by the injection point(s)
- [x] Data available at each injection point is documented
- [x] Constraints and edge cases identified
- [x] Summary/diagram created for reference
- [x] Team/next task can understand and act on findings without re-reading the code

## Affected Files / Components
- `src/llm.py` - primary file being analyzed
- Related files for context: `src/config.py`, `src/history.py`

## Risks / Dependencies
- This task is purely analysis; no code changes
- Findings are critical for IMR-02 (integration), so accuracy is important
- Must verify all code paths are covered, not just the happy path

## Validation Steps
1. Read `src/llm.py` from top to bottom
2. Identify the `ask_llm()` function and all its code paths
3. Trace through what happens before/during/after the request
4. Create a diagram or flowchart of the request flow
5. Identify where to inject logging (ideally one point, but may be multiple)
6. Verify that logging at that point would capture all requests
7. Document findings in a summary that others can use

## Follow-ups (optional)
- IMR-02: Use these findings to implement the actual logging integration
