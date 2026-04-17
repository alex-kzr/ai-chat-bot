import logging
import json
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src import config
from src.config import Settings

# Module-level singleton logger
_context_logger: Optional[logging.Logger] = None
_context_settings: Optional[Settings] = None


def _close_logger_handlers(logger: logging.Logger) -> None:
    """Detach and close all handlers to release resources and file locks."""
    for handler in list(logger.handlers):
        try:
            handler.flush()
        except Exception:
            pass
        try:
            handler.close()
        except Exception:
            pass
        logger.removeHandler(handler)


def _release_file_logger_if_needed(logger: logging.Logger) -> None:
    """Release file handlers so tests/short-lived runs don't keep file locks."""
    global _context_logger
    if any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
        _close_logger_handlers(logger)
        _context_logger = None


def configure_context_logging(settings: Settings) -> None:
    """Set explicit settings used by the context logger."""
    global _context_settings, _context_logger
    _context_settings = settings
    _context_logger = None


def _effective_settings() -> Settings:
    if _context_settings is not None:
        return _context_settings
    try:
        settings = config.get_settings()
        # Backward compatibility for tests/legacy callers that monkeypatch
        # module-level config attributes directly (e.g. config.LOG_FILE_PATH).
        # We only honor explicitly set attributes on the module object.
        cfg_vars = vars(config)
        has_logging_overrides = any(
            key in cfg_vars
            for key in (
                "CONTEXT_LOGGING_ENABLED",
                "LOG_LEVEL",
                "LOG_DESTINATION",
                "LOG_FILE_PATH",
                "LOG_FORMAT",
                "SHOW_THINKING",
                "TOKEN_COUNT_STRATEGY",
                "HEURISTIC_TOKEN_RATIO",
            )
        )
        if has_logging_overrides:
            logging_settings = replace(
                settings.logging,
                level=str(cfg_vars.get("LOG_LEVEL", settings.logging.level)),
                context_enabled=bool(cfg_vars.get("CONTEXT_LOGGING_ENABLED", settings.logging.context_enabled)),
                destination=str(cfg_vars.get("LOG_DESTINATION", settings.logging.destination)),
                file_path=str(cfg_vars.get("LOG_FILE_PATH", settings.logging.file_path)),
                fmt=str(cfg_vars.get("LOG_FORMAT", settings.logging.fmt)),
                show_thinking=bool(cfg_vars.get("SHOW_THINKING", settings.logging.show_thinking)),
                token_count_strategy=str(
                    cfg_vars.get("TOKEN_COUNT_STRATEGY", settings.logging.token_count_strategy)
                ),
                heuristic_token_ratio=int(
                    cfg_vars.get("HEURISTIC_TOKEN_RATIO", settings.logging.heuristic_token_ratio)
                ),
            )
            settings = replace(settings, logging=logging_settings)
        return settings
    except Exception:
        return config.load_settings(
            env={
                "BOT_TOKEN": "test-token",
                "OLLAMA_URL": "http://localhost:11434",
                "OLLAMA_MODEL": "qwen3:0.6b",
            },
            load_dotenv_file=False,
        )


class LevelAwareFormatter(logging.Formatter):
    def __init__(self) -> None:
        super().__init__(fmt="%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")


def setup_context_logger() -> logging.Logger:
    """
    Set up and return a configured context logger instance.

    This function uses lazy initialization - the logger is created once and
    reused on subsequent calls. Configuration is read from src.config.

    Returns:
        logging.Logger: Configured logger instance
    """
    global _context_logger

    if _context_logger is not None:
        return _context_logger

    settings = _effective_settings()

    if not settings.logging.context_enabled:
        # Return a null logger if logging is disabled
        _context_logger = logging.getLogger("context_null")
        _close_logger_handlers(_context_logger)
        _context_logger.addHandler(logging.NullHandler())
        return _context_logger

    _context_logger = logging.getLogger("context_logger")
    _context_logger.setLevel(getattr(logging, settings.logging.level.upper(), logging.INFO))
    _context_logger.propagate = False

    # Remove any existing handlers to avoid duplicates
    _close_logger_handlers(_context_logger)

    # Create appropriate handler based on configuration
    if settings.logging.destination.lower() == "file":
        # Ensure logs directory exists
        log_path = Path(settings.logging.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(settings.logging.file_path, mode='a', delay=True)
    else:  # Default to console
        handler = logging.StreamHandler()

    handler.setFormatter(LevelAwareFormatter())
    _context_logger.addHandler(handler)

    return _context_logger


def format_log_entry(data: Dict[str, Any], format_type: Optional[str] = None) -> str:
    """
    Format a context log dictionary into readable text or JSON.

    Args:
        data: Dictionary containing log data (should include timestamp, user_id, context, etc.)
        format_type: "human" or "json". If None, uses config.LOG_FORMAT

    Returns:
        str: Formatted log entry
    """
    if format_type is None:
        format_type = _effective_settings().logging.fmt.lower()

    if format_type == "json":
        return _format_json(data)
    else:  # Default to "human"
        return _format_human(data)


def _format_human(data: Dict[str, Any]) -> str:
    """
    Format log data in human-readable format with clear sections and indentation.

    Args:
        data: Dictionary containing log data

    Returns:
        str: Human-readable formatted log entry
    """
    lines = []

    # Add timestamp if present
    if "timestamp" in data:
        lines.append(f"Timestamp: {data['timestamp']}")
    elif "timestamp" not in data:
        lines.append(f"Timestamp: {datetime.now().isoformat()}")

    # Add user_id if present
    if "user_id" in data:
        lines.append(f"User ID: {data['user_id']}")

    # Add context section header
    lines.append("\n--- Context ---")

    # Format context data with indentation
    for key, value in data.items():
        if key not in ["timestamp", "user_id"]:
            if isinstance(value, (dict, list)):
                lines.append(f"{key}:")
                lines.append(_indent_value(value, 2))
            else:
                lines.append(f"{key}: {value}")

    return "\n".join(lines)


def _format_json(data: Dict[str, Any]) -> str:
    """
    Format log data as valid JSON.

    Args:
        data: Dictionary containing log data

    Returns:
        str: JSON-formatted log entry
    """
    # Ensure timestamp is present
    if "timestamp" not in data:
        data = {**data, "timestamp": datetime.now().isoformat()}

    return json.dumps(data, indent=2, default=str)


def _indent_value(value: Any, spaces: int = 2) -> str:
    """
    Indent a value for human-readable formatting.

    Args:
        value: Value to indent (typically dict or list)
        spaces: Number of spaces for indentation

    Returns:
        str: Indented value
    """
    indent = " " * spaces

    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{indent}{k}:")
                lines.append(_indent_value(v, spaces + 2))
            else:
                lines.append(f"{indent}{k}: {v}")
        return "\n".join(lines)

    elif isinstance(value, list):
        lines = []
        for i, item in enumerate(value):
            if isinstance(item, (dict, list)):
                lines.append(f"{indent}[{i}]:")
                lines.append(_indent_value(item, spaces + 2))
            else:
                lines.append(f"{indent}[{i}]: {item}")
        return "\n".join(lines)

    else:
        return f"{indent}{value}"


def log_context(data: Dict[str, Any], level: str = "info") -> None:
    """
    Log context data using the configured logger.

    Args:
        data: Dictionary containing log data
        level: Log level ("debug", "info", "warning", "error")
    """
    logger = setup_context_logger()

    # Format the log entry
    formatted_entry = format_log_entry(data)

    # Log at the appropriate level
    try:
        if level.lower() == "debug":
            logger.debug(formatted_entry)
        elif level.lower() == "warning":
            logger.warning(formatted_entry)
        elif level.lower() == "error":
            logger.error(formatted_entry)
        else:  # Default to info
            logger.info(formatted_entry)
    finally:
        _release_file_logger_if_needed(logger)


def log_agent_event(run_id: str, event: str, *, level: str = "info", **fields: Any) -> None:
    """Emit a deterministic single-line structured log for agent runtime events."""
    logger = setup_context_logger()
    record = {
        "kind": "agent_event",
        "run_id": run_id,
        "event": event,
        **fields,
    }
    message = json.dumps(record, ensure_ascii=False, sort_keys=True, default=str)

    try:
        if level.lower() == "debug":
            logger.debug(message)
        elif level.lower() == "warning":
            logger.warning(message)
        elif level.lower() == "error":
            logger.error(message)
        else:
            logger.info(message)
    finally:
        _release_file_logger_if_needed(logger)


def extract_context(
    messages: list[dict],
    user_id: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extract and organize the full LLM request context into a structured format.

    Args:
        messages: List of message dictionaries (each with "role" and "content")
        user_id: Optional user identifier
        model_name: Optional model name
        temperature: Optional temperature parameter
        max_tokens: Optional max_tokens parameter

    Returns:
        Dict containing extracted context with messages, metadata, and statistics
    """
    context = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "messages": serialize_messages(messages, include_content=True),
        "metadata": extract_metadata(user_id, model_name, temperature, max_tokens),
        "statistics": {
            "total_messages": len(messages),
            "message_breakdown": _count_message_roles(messages),
            "total_content_length": sum(len(msg.get("content", "")) for msg in messages),
        }
    }
    return context


def serialize_messages(
    messages: list[dict],
    include_content: bool = True,
    max_content_length: int = 500
) -> list[dict]:
    """
    Format messages array in a readable, loggable format.

    Args:
        messages: List of message dictionaries
        include_content: Whether to include full message content
        max_content_length: Maximum length of content before truncation

    Returns:
        List of formatted message dictionaries
    """
    serialized = []

    for i, msg in enumerate(messages):
        serialized_msg = {
            "index": i,
            "role": msg.get("role", "unknown"),
        }

        if include_content:
            content = msg.get("content", "")
            if len(content) > max_content_length:
                serialized_msg["content"] = content[:max_content_length] + "..."
                serialized_msg["content_truncated"] = True
                serialized_msg["original_length"] = len(content)
            else:
                serialized_msg["content"] = content
                serialized_msg["content_truncated"] = False

        serialized.append(serialized_msg)

    return serialized


def extract_metadata(
    user_id: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> Dict[str, Any]:
    """
    Extract and organize request metadata.

    Args:
        user_id: Optional user identifier
        model_name: Optional model name
        temperature: Optional temperature parameter
        max_tokens: Optional max_tokens parameter

    Returns:
        Dict containing request metadata
    """
    metadata = {
        "user_id": user_id,
        "model": model_name,
        "parameters": {}
    }

    # Add optional parameters if provided
    if temperature is not None:
        metadata["parameters"]["temperature"] = temperature

    if max_tokens is not None:
        metadata["parameters"]["max_tokens"] = max_tokens

    return metadata


def _count_message_roles(messages: list[dict]) -> Dict[str, int]:
    """
    Count messages by role.

    Args:
        messages: List of message dictionaries

    Returns:
        Dict with counts of messages by role
    """
    counts = {}
    for msg in messages:
        role = msg.get("role", "unknown")
        counts[role] = counts.get(role, 0) + 1

    return counts


# Module-level tokenizer cache
_tokenizer_available = None


def _try_import_tiktoken():
    """
    Attempt to import tiktoken for accurate token counting.
    Returns the encoding object if available, None otherwise.
    """
    global _tokenizer_available

    if _tokenizer_available is not None:
        return _tokenizer_available

    try:
        import tiktoken
        _tokenizer_available = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return _tokenizer_available
    except ImportError:
        _tokenizer_available = False
        return None


def count_tokens(text: str) -> int:
    """
    Count tokens in a given text string.

    Uses the configured strategy (heuristic or tiktoken if available).
    Falls back to heuristic if tiktoken fails.

    Args:
        text: Text to count tokens for

    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0

    # Try tiktoken if strategy is configured for it and available
    if _effective_settings().logging.token_count_strategy.lower() == "tiktoken":
        tokenizer = _try_import_tiktoken()
        if tokenizer:
            try:
                tokens = tokenizer.encode(text)
                return len(tokens)
            except Exception:
                # Fall back to heuristic if tiktoken fails
                pass

    # Use heuristic estimation
    return _count_tokens_heuristic(text)


def _count_tokens_heuristic(text: str) -> int:
    """
    Estimate token count using character-based heuristic.

    Conservative estimate: 1 token ≈ HEURISTIC_TOKEN_RATIO characters.

    Args:
        text: Text to estimate token count for

    Returns:
        Estimated number of tokens
    """
    if not text:
        return 0

    # Count characters and divide by the configured ratio
    # Round up to be conservative
    char_count = len(text.encode("utf-8"))  # Use byte count for unicode safety
    ratio = _effective_settings().logging.heuristic_token_ratio
    token_estimate = (char_count + ratio - 1) // ratio

    return token_estimate


def count_context_tokens(messages: list[dict]) -> int:
    """
    Count total tokens across a list of messages.

    Includes:
    - All message content tokens
    - JSON structure overhead (estimated at 4 tokens per message for role, brackets, etc.)

    Args:
        messages: List of message dictionaries (each with "role" and "content")

    Returns:
        Total estimated token count
    """
    if not messages:
        return 0

    total_tokens = 0

    for msg in messages:
        content = msg.get("content", "")
        role = msg.get("role", "")

        # Count tokens in content
        content_tokens = count_tokens(content)

        # Add tokens for role field (~1-2 tokens per role, estimate 2)
        role_tokens = count_tokens(role)

        # Add JSON structure overhead (estimate 4 tokens for JSON scaffolding per message)
        structure_tokens = 4

        total_tokens += content_tokens + role_tokens + structure_tokens

    return total_tokens
