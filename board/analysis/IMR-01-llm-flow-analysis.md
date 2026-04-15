# IMR-01: LLM Request Flow Analysis

## Overview
This document provides a detailed analysis of the LLM request flow in `src/llm.py` to identify injection points for context logging.

## Current Request Flow

### Function Signature
```python
async def ask_llm(user_text: str, history: list[dict] | None = None) -> tuple[str, str]:
```

**Note:** `user_text` parameter is not used in the function; all context comes from the `history` parameter.

### Step-by-Step Request Flow

```
1. INPUT
   ├─ user_text: str (NOT USED - can be ignored)
   └─ history: list[dict] | None (message history)

2. PREPARATION
   ├─ Normalize history (default to empty list)
   ├─ Check if system prompt should be prepended:
   │  ├─ Condition: SYSTEM_PROMPT_ENABLED config AND
   │  └─ First message in history is NOT already a system message
   └─ Build system_messages list (0 or 1 system message)

3. PAYLOAD ASSEMBLY
   ├─ Construct payload dict:
   │  ├─ model: config.OLLAMA_MODEL
   │  ├─ messages: system_messages + history (concatenated)
   │  └─ stream: False
   └─ Final messages = [optional system] + history

4. LOGGING (EXISTING)
   ├─ logging.info(">>> LLM request: %s", payload["messages"])
   └─ This only logs the message array, not structured context

5. HTTP REQUEST
   ├─ Create AsyncClient with timeout
   ├─ POST to {OLLAMA_URL}/api/chat with payload
   ├─ Raise for status (raises exception on 4xx/5xx)
   └─ Parse response JSON

6. SUCCESS PATH
   ├─ Extract llm_raw from response["message"]["content"]
   ├─ Strip whitespace
   └─ Return (llm_raw, llm_raw)

7. ERROR PATH (ANY EXCEPTION)
   ├─ Catch Exception (any error from steps 5-6)
   ├─ logging.error("LLM error: %s", e)
   ├─ Pick random error_phrase from ERROR_PHRASES
   └─ Return ("[error]", error_phrase)
```

## Code Paths Analysis

### Path 1: Happy Path (Success)
- Input: valid history list
- System prompt added (if enabled)
- Request succeeds (HTTP 200 with valid JSON)
- Returns: (llm_raw, llm_raw)
- **Frequency:** Most requests

### Path 2: Error Path (Any Exception)
- HTTP error (4xx, 5xx)
- Network timeout
- Invalid JSON response
- Any other exception
- Returns: ("[error]", error_phrase)
- **Frequency:** Some requests (errors)

### Path 3: Empty History
- history param is None or empty list
- No system message or uses existing system message in history
- Proceeds normally with minimal messages
- **Frequency:** Depends on application logic

## Identified Data at Each Point

### Before HTTP Request (BEST LOGGING POINT)
**Available data:**
- ✓ Complete payload dict (model, messages, stream)
- ✓ System prompt (if used)
- ✓ Full message history
- ✓ All message roles and content
- ✓ Model name
- ✓ Configuration state (SYSTEM_PROMPT_ENABLED, etc.)

**Not available:**
- ✗ Response (hasn't happened yet)
- ✗ User ID (not passed to function)
- ✗ Request duration

### After HTTP Request
**Available data:**
- ✓ All "before" data
- ✓ HTTP response
- ✓ Extracted response content (llm_raw)
- ✓ Response timing (if measured)

**Limitations:**
- ✗ Not accessible in error path
- ✗ Harder to differentiate between request and response

### In Error Handler
**Available data:**
- ✓ Exception details
- ✓ Payload (if captured before request)
- ✗ Response (because request failed)

## Recommended Injection Points

### PRIMARY: Log Before HTTP Request
**Location:** After `payload` assembly, before `httpx` call

**Why this point:**
1. **All requests captured** - Every request (success or failure) passes through this point
2. **Complete context available** - Full messages, model, config
3. **No response bias** - Logs what we intended to send, not what we received
4. **Clear request boundaries** - Exactly marks the start of an LLM request
5. **Non-intrusive** - Can be added without affecting request flow
6. **Natural logging point** - Matches existing logging philosophy (log what happens)

**Data to capture at this point:**
- Complete messages list (with system prompt if applicable)
- Model name
- Configuration state (SYSTEM_PROMPT_ENABLED)
- Timestamp
- Full payload details

### SECONDARY: Log After Successful Response
**Location:** After successful response parsing, before return

**Why this point:**
1. Provides response information
2. Shows what the model actually returned
3. Allows comparison of request vs. response

**But only if:**
- We have resources to do both
- Response logging doesn't duplicate request data

### TERTIARY: Log in Error Path
**Location:** In the exception handler

**Why:**
- Captures error context for debugging
- Should reference the pre-request log for full context

## Current Logging

The existing logging in the code:
```python
logging.info(">>> LLM request: %s", payload["messages"])  # Line 25
logging.error("LLM error: %s", e)  # Line 36
```

**Issues with existing logging:**
1. Only logs message array, not structured context
2. No indication of what model or config was used
3. Generic format, hard to parse
4. Doesn't use the new context_logging infrastructure

## Implementation Recommendation

### Single Unified Logging Point

**Before** the HTTP request (after payload assembly):

```python
# Suggested location: Between line 24 and 25
# After: payload = { ... }
# Before: logging.info(">>> LLM request...")

# Call context logging here with:
# - messages: payload["messages"]
# - model_name: config.OLLAMA_MODEL
# - user_id: None (not available)
# - config: system_prompt_enabled, timeout, etc.
```

This single point captures:
- ✓ Exactly what will be sent to the LLM
- ✓ All message details (roles, content, order)
- ✓ Model and configuration state
- ✓ Works for all code paths (success and error)

### Error Logging Enhancement

Keep the existing error logging but enhance it:
- Reference the request log for context
- Add exception details
- Mention that response was not received

## Edge Cases & Constraints

### Edge Case 1: System Prompt Handling
**Issue:** System prompt may or may not be included
**Solution:** The logging point sees the final assembled messages, so system prompt status is already determined
**Constraint:** Can't retroactively add system prompt to context if it wasn't logged upfront

### Edge Case 2: Empty History
**Issue:** Request may have only system prompt, no user messages
**Solution:** Still valid request, log as-is with note that history is empty
**No constraint**

### Edge Case 3: Timeout/Network Errors
**Issue:** May fail before we see the request assembled
**Solution:** Logging happens before httpx call, so these are logged correctly
**No constraint**

### Edge Case 4: Malformed Messages
**Issue:** If messages dict is malformed, HTTP will fail
**Solution:** Logging is before validation, will log malformed state (useful for debugging)
**No constraint**

### Edge Case 5: Very Large Context
**Issue:** Large history might timeout or fail
**Solution:** Logging captures size and content; token counting helps identify large contexts
**No constraint**

## Summary for Implementation (IMR-02)

### Action Item for Next Task
1. Add context logging call **before** the httpx request
2. Use `extract_context()` and `count_context_tokens()` from LIS-02/LIS-03
3. Pass:
   - `messages`: payload["messages"]
   - `model_name`: config.OLLAMA_MODEL
   - `temperature`: None (not used in current config, but configurable)
   - `max_tokens`: None (not used in current config, but configurable)
4. Log at "debug" or "info" level
5. Consider async safety (logging in async context)

### Implementation Template
```python
# After payload assembly, before httpx call:
if config.CONTEXT_LOGGING_ENABLED:
    context = extract_context(
        messages=payload["messages"],
        model_name=config.OLLAMA_MODEL,
        user_id=None,  # Not available in current signature
    )
    log_context(context, level="debug")
```

### Optional Enhancements (Out of Scope)
- Pass user_id through ask_llm() signature
- Log response content after successful request
- Log error context details in exception handler
- Track request duration/timing
