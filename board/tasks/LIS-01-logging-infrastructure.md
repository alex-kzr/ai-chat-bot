# LIS-01 - Create logging configuration and utilities

## Status
- [x] To Do
- [x] In Progress
- [x] Done 

## Purpose
Establish a reusable logging infrastructure for context logging. This task sets up the foundation that all subsequent logging tasks will depend on, including configurable log destinations (console/file) and utility functions for structured log output.

## Context
Currently, the bot has no visibility into what context is being sent to the LLM. We need a centralized, configurable logging system that:
- Outputs to console or file (configurable)
- Formats logs in a readable, developer-friendly way
- Supports structured output (JSON) for parsing/analysis
- Works seamlessly with the existing Python logging module

Related files to check:
- `src/config.py` - where configuration lives
- `src/llm.py` - where LLM requests are made (will consume this logger later)

## Requirements
- Create `src/context_logging.py` module with logging setup
- Add logging configuration constants to `src/config.py`:
  - `CONTEXT_LOGGING_ENABLED` (bool, default: True)
  - `LOG_DESTINATION` (enum or string: "console" or "file", default: "console")
  - `LOG_FILE_PATH` (string, default: "logs/context.log")
  - `LOG_FORMAT` (enum or string: "human" or "json", default: "human")
- Implement `setup_context_logger()` function that returns a configured logger
- Implement `format_log_entry(data)` utility that formats a context log dict into readable text/JSON
- Ensure logs directory is created automatically if using file output
- Log entries should include timestamp, user_id (if applicable), and context metadata

## Implementation Notes
- Use Python's standard `logging` module as the base
- Keep the logger instance as a module-level singleton in `context_logging.py`
- The logger should be lazy-initialized (set up once, on first use)
- Consider using environment variables for output directory to support testing
- Make file output append-only (don't truncate on restart)
- Human-readable format should include clear section headers and indentation for nested structures

## Definition of Done
- [x] `src/context_logging.py` module created with logger setup
- [x] Configuration constants added to `src/config.py`
- [x] `setup_context_logger()` works correctly and returns a logger instance
- [x] `format_log_entry()` produces readable human format
- [x] `format_log_entry()` produces valid JSON when requested
- [x] Logs directory is auto-created if needed
- [x] Logger can be imported and used without errors
- [x] No existing functionality is broken

## Affected Files / Components
- `src/context_logging.py` (new file)
- `src/config.py` (additions)
- Potentially `logs/` directory (created on first use)

## Risks / Dependencies
- None at this stage; this is foundational infrastructure with no external dependencies
- Future tasks (LIS-02, LIS-03, IMR-02) depend on this being complete and working

## Validation Steps
1. Create the module and import it in a test script
2. Verify `setup_context_logger()` returns a valid logger instance
3. Test `format_log_entry()` with sample context data in both "human" and "json" formats
4. Verify logs are written to the correct destination (console or file)
5. Check that the log format is readable and contains expected fields

## Follow-ups (optional)
- LIS-02: Implement context extraction and serialization (depends on this)
- LIS-03: Add token counting mechanism (depends on this)
