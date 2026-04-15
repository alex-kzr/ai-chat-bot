# LIS-03 - Add token counting mechanism

## Status
- [x] To Do
- [x] In Progress
- [x] Done 

## Purpose
Implement or integrate a token counting mechanism to measure the size of the context being sent to the LLM. This allows developers to see both what is being sent AND how large the context is in tokens.

## Context
Modern LLMs have context windows measured in tokens. The bot needs to report token count for every request to help developers understand:
- Whether context is approaching the model's limit
- How history trimming and summarization are affecting context size
- Whether the bot is efficiently using available context

We need a reliable way to count tokens that matches (or closely approximates) what the actual model sees.

Related files:
- `src/context_logging.py` - where we'll add token counting
- `src/llm.py` - where we need to know token count
- `src/config.py` - configuration for tokenization strategy

## Requirements
- Implement `count_tokens(text)` function that counts tokens in a string
- Implement `count_context_tokens(messages)` function that counts tokens across a messages list
- Support two strategies (implement the first, make the second pluggable for future):
  1. **Heuristic estimation** (primary): Simple word-count based estimation (e.g., 1 token ≈ 4 chars or use a simple regex)
  2. **Actual tokenizer** (optional, if available): Use `tiktoken` or similar if installed, fall back to heuristic if not
- Add configuration to `src/config.py`:
  - `TOKEN_COUNT_STRATEGY` (default: "heuristic", can be "tiktoken" if available)
  - `HEURISTIC_TOKEN_RATIO` (default: 4, chars per token estimate)
- Token counting must:
  - Include system message tokens if present
  - Include all history message tokens
  - Include current user message tokens
  - Include JSON structure overhead if messages are serialized
  - Be fast (no significant performance impact on each request)

## Implementation Notes
- Start with heuristic estimation (reliable, no dependencies)
- If `tiktoken` is already in requirements, use it; otherwise make it optional
- The heuristic should be conservative (overestimate slightly) to avoid context window overflows
- Consider character count vs. word count - characters might be more reliable
- Token counting should be deterministic (same input always produces same count)
- Add logging when actual tokenizer is used vs. heuristic to help with debugging

## Definition of Done
- [x] `count_tokens(text)` function implemented and tested
- [x] `count_context_tokens(messages)` function implemented and tested
- [x] Heuristic estimation works reliably
- [x] Configuration constants added to `src/config.py`
- [x] Token counting is fast and doesn't block request flow
- [x] Token counts match the actual message sizes being sent
- [x] Edge cases handled (empty messages, special characters, unicode)
- [x] No regressions in existing code

## Affected Files / Components
- `src/context_logging.py` (additions)
- `src/config.py` (additions)
- `requirements.txt` (potentially, if tiktoken is added as optional)

## Risks / Dependencies
- Depends on LIS-01 and LIS-02 (logging infrastructure and context extraction)
- If using actual tokenizer, must handle case where it's not installed
- Token count estimation may not be 100% accurate (use heuristic by default to be safe)

## Validation Steps
1. Implement heuristic token counting
2. Test with known text samples and verify counts are reasonable
3. Test `count_context_tokens()` with sample message lists
4. Compare heuristic counts with actual token count if tokenizer is available (for reference)
5. Verify token counting doesn't significantly slow down requests
6. Edge cases: empty strings, very long messages, unicode characters, JSON structures

## Follow-ups (optional)
- IMR-02: Integrate token counting into the logging output
- Consider adding actual tokenizer support if performance/accuracy becomes critical
