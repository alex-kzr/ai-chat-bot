import logging
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src import config

# Module-level singleton logger
_context_logger: Optional[logging.Logger] = None


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

    if not config.CONTEXT_LOGGING_ENABLED:
        # Return a null logger if logging is disabled
        _context_logger = logging.getLogger("context_null")
        _context_logger.addHandler(logging.NullHandler())
        return _context_logger

    _context_logger = logging.getLogger("context_logger")
    _context_logger.setLevel(logging.DEBUG)

    # Remove any existing handlers to avoid duplicates
    _context_logger.handlers.clear()

    # Create appropriate handler based on configuration
    if config.LOG_DESTINATION.lower() == "file":
        # Ensure logs directory exists
        log_path = Path(config.LOG_FILE_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        handler = logging.FileHandler(config.LOG_FILE_PATH, mode='a')
    else:  # Default to console
        handler = logging.StreamHandler()

    # Set up formatter based on configuration
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
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
        format_type = config.LOG_FORMAT.lower()

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
    if level.lower() == "debug":
        logger.debug(formatted_entry)
    elif level.lower() == "warning":
        logger.warning(formatted_entry)
    elif level.lower() == "error":
        logger.error(formatted_entry)
    else:  # Default to info
        logger.info(formatted_entry)


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
    if config.TOKEN_COUNT_STRATEGY.lower() == "tiktoken":
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
    token_estimate = (char_count + config.HEURISTIC_TOKEN_RATIO - 1) // config.HEURISTIC_TOKEN_RATIO

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
