from __future__ import annotations


class AppError(Exception):
    """Base application exception."""


class ConfigurationError(AppError):
    """Raised when configuration values are invalid."""


class OllamaTransportError(AppError):
    """Raised when transport-level communication with Ollama fails."""


class OllamaProtocolError(AppError):
    """Raised when Ollama returns unexpected payload shape."""


class AgentParseContractError(AppError):
    """Raised when agent output does not satisfy the JSON contract."""


class ToolExecutionError(AppError):
    """Raised when a tool invocation fails in a non-recoverable way."""
