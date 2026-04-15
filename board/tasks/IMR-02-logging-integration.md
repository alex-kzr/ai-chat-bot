# IMR-02 - Integrate logging into request pipeline

## Status
- [x] To Do
- [x] In Progress
- [x] Done 

## Purpose
Integrate the logging infrastructure (LIS-01 to LIS-03) into the actual LLM request pipeline. This ensures that every model request is logged automatically, showing developers exactly what context is being sent and its token count.

## Context
Now that we have:
- Logging infrastructure (LIS-01)
- Context extraction functions (LIS-02)
- Token counting (LIS-03)

We need to wire everything together at the LLM request boundary. Based on IMR-01 analysis, we know where to inject logging and what data is available.

The goal is to log the full context (messages, metadata, token count) immediately before each request to the model, without breaking the request flow or changing the bot's behavior.

Related files:
- `src/llm.py` - where we inject logging
- `src/context_logging.py` - the logging utilities
- Findings from IMR-01 task

## Requirements
- Update `src/llm.py` to call logging functions immediately before sending request to model
- Logging must happen for ALL requests:
  - Regular user messages
  - Any retries
  - Different model endpoints (if applicable)
- Log the following information:
  - Full messages list (system, history, current user message)
  - Message count and token count
  - User ID (if available)
  - Model name and request parameters (temperature, max_tokens, etc.)
  - Timestamp
- Logging must not block or slow down the request (async if needed)
- Logging must not modify the request payload or break error handling
- If logging fails, it should not crash the bot or prevent the LLM request

## Implementation Notes
- Add logging call immediately before the actual model API call
- Use context extraction functions from LIS-02 to get the data
- Use token counting from LIS-03 to calculate token counts
- Format log output using utilities from LIS-01
- Consider whether logging should be async to avoid latency impact
- If an exception occurs in logging, catch it and continue (don't break the request)
- Update docstrings in `ask_llm()` if needed to document the logging behavior
- Ensure logging respects the `CONTEXT_LOGGING_ENABLED` config flag

## Definition of Done
- [x] Logging call(s) added to `src/llm.py` at the correct injection point(s)
- [x] All requests are logged (test with multiple request types)
- [x] Log output includes full context, token count, and metadata
- [x] Logging is transparent (doesn't change request/response behavior)
- [x] Error handling in logging is robust (doesn't break the bot)
- [x] Logging respects configuration flags (can be disabled if needed)
- [x] Bot still responds correctly to user messages
- [x] No performance regression from logging overhead
- [x] Code is clean and maintainable

## Affected Files / Components
- `src/llm.py` (main integration point)
- `src/context_logging.py` (provides logging utilities)
- `src/config.py` (configuration for logging)

## Risks / Dependencies
- Depends on LIS-01, LIS-02, LIS-03 being complete and working
- Depends on IMR-01 analysis being accurate
- Must be careful not to modify request payload or error handling
- Performance impact should be minimal (logging should be fast)

## Validation Steps
1. Verify logging infrastructure is working (LIS-01)
2. Verify context extraction is working (LIS-02)
3. Verify token counting is working (LIS-03)
4. Add logging call to `ask_llm()`
5. Run the bot and send a message - verify log appears
6. Check that log shows:
   - All messages (system, history, current)
   - Correct message order
   - Token count
   - Metadata (user_id, model, etc.)
7. Test with multiple messages - verify each request is logged
8. Verify the model still responds correctly
9. Test with logging disabled - verify bot works without logging
10. Check logs for any exceptions or errors in logging itself

## Follow-ups (optional)
- IMR-03: Implement validation and testing for the logging feature
- Consider adding log rotation or cleanup if log files grow large
