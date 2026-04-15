# LIS-02 - Implement context extraction and serialization

## Status
- [x] To Do
- [x] In Progress
- [x] Done 

## Purpose
Extract and serialize the full model request context into a loggable format. This task ensures that all relevant information about what will be sent to the LLM (messages, roles, order, etc.) can be captured and formatted for inspection.

## Context
The LLM request in `src/llm.py` includes:
- System prompt (if enabled, from config)
- Conversation history (from `src/history.py`)
- Current user message
- Optional parameters (temperature, max_tokens, etc.)

We need to extract this information before the request is sent and make it ready for logging.

Related files:
- `src/llm.py` - where the request is built
- `src/history.py` - source of conversation history
- `src/config.py` - source of system prompt and other config
- `src/context_logging.py` - the logger we just created (LIS-01)

## Requirements
- Create functions in `src/context_logging.py` (or related module) to:
  - `extract_context(messages, user_id=None)` - Extract full context from messages list
  - `serialize_messages(messages, include_content=True)` - Format messages array in readable way
  - `extract_metadata(user_id, model_name, temperature, max_tokens)` - Extract request metadata
- The extraction must capture:
  - All messages in the context (system, history, current user message)
  - Message roles (system, user, assistant)
  - Message order (they appear in the request)
  - Metadata about the request (user_id, model, temperature, etc.)
- Support both detailed (show full message content) and summary (show only structure) views
- Handle edge cases:
  - Empty history
  - Missing user_id
  - Very long messages (truncate for readability while noting they were truncated)

## Implementation Notes
- The extraction should happen at the point where the full messages list is assembled in `ask_llm()`
- Don't modify message content; extract as-is
- Preserve the exact order messages will be sent to the model
- Consider using a dataclass or dict to represent extracted context
- The extracted context should be self-contained (can be logged/serialized without additional context)

## Definition of Done
- [x] Functions to extract context are implemented
- [x] Messages are extracted and serialized correctly (roles, order, content)
- [x] Metadata is captured (user_id, model name, parameters)
- [x] Edge cases handled (empty messages, missing data, long content)
- [x] Extraction can be tested independently of the logging output
- [x] Output is readable and shows the full picture of what will be sent to LLM
- [x] No regressions in existing code

## Affected Files / Components
- `src/context_logging.py` (additions)
- `src/llm.py` (will integrate extraction here, but not yet in this task)

## Risks / Dependencies
- Depends on LIS-01 (logging infrastructure) being complete
- Must work with the current structure of `ask_llm()` without breaking it
- Must handle all message types that `ask_llm()` currently supports

## Validation Steps
1. Create test data (sample messages, history, metadata)
2. Call `extract_context()` with the test data
3. Verify extracted context contains all messages in correct order
4. Verify metadata is accurate
5. Serialize and inspect the output manually - it should be clear what will be sent to the model
6. Test with edge cases (empty history, long messages, etc.)

## Follow-ups (optional)
- IMR-02: Integrate this into the actual request pipeline
