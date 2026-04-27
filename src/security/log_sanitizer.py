import re
from typing import Any

PATTERNS = [
    (r"\d{8,10}:[A-Za-z0-9_-]{20,}", "telegram_bot_token"),
    (r"sk-[A-Za-z0-9]{20,}", "openai_api_key"),
    (r"ghp_[A-Za-z0-9]{36,}", "github_token"),
    (r"xox[abp]-[A-Za-z0-9-]+", "slack_token"),
    (r"Bearer\s+[A-Za-z0-9_.=-]+", "bearer_token"),
    (r"(?i)Authorization:\s*Basic\s+[A-Za-z0-9+/=]+", "basic_auth"),
    (r"(?i)Set-Cookie:\s*[^;\n]+", "set_cookie"),
    (r"(?i)Cookie:\s*[^;\n]+", "cookie"),
    (r"(?i)api[_-]key[=:\s]+[A-Za-z0-9_-]{20,}", "generic_api_key"),
]

COMPILED_PATTERNS = [(re.compile(pattern, re.IGNORECASE), kind) for pattern, kind in PATTERNS]


def sanitize_log_data(value: Any) -> Any:
    """Recursively sanitize secrets from log data."""
    if isinstance(value, str):
        return _sanitize_string(value)
    if isinstance(value, dict):
        return {k: sanitize_log_data(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        result = [sanitize_log_data(item) for item in value]
        return type(value)(result)
    return value


def _sanitize_string(value: str) -> str:
    """Sanitize secrets in a string value."""
    result = value
    for pattern, kind in COMPILED_PATTERNS:
        result = pattern.sub(f"[REDACTED:{kind}]", result)
    return result
