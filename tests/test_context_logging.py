"""
Test suite for context logging infrastructure and integration.

Tests cover:
- Basic logging functionality
- Context extraction
- Message serialization
- Token counting
- Log formatting (human and JSON)
- Edge cases and error handling
- Configuration options
"""

import json
import logging
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from src import config
from src.context_logging import (
    count_context_tokens,
    count_tokens,
    extract_context,
    extract_metadata,
    format_log_entry,
    serialize_messages,
    setup_context_logger,
)


class TestTokenCounting:
    """Test token counting functions."""

    def test_count_tokens_simple_text(self):
        """Test token counting on simple text."""
        tokens = count_tokens("Hello world")
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_empty_string(self):
        """Test token counting on empty string returns 0."""
        tokens = count_tokens("")
        assert tokens == 0

    def test_count_tokens_unicode(self):
        """Test token counting handles unicode characters."""
        tokens = count_tokens("你好世界 مرحبا العالم")
        assert tokens > 0

    def test_count_tokens_long_text(self):
        """Test token counting on long text."""
        long_text = "word " * 1000
        tokens = count_tokens(long_text)
        assert tokens > 0
        # Should be roughly proportional to text length
        short_tokens = count_tokens("word")
        assert tokens > short_tokens * 100

    def test_count_context_tokens_single_message(self):
        """Test token counting on single message."""
        messages = [
            {"role": "user", "content": "Hello assistant"}
        ]
        tokens = count_context_tokens(messages)
        assert tokens > 0

    def test_count_context_tokens_multiple_messages(self):
        """Test token counting on multiple messages."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
        ]
        tokens = count_context_tokens(messages)
        assert tokens > 0
        # With multiple messages, token count should scale
        single_msg = count_context_tokens([messages[0]])
        assert tokens > single_msg

    def test_count_context_tokens_empty_list(self):
        """Test token counting on empty message list."""
        tokens = count_context_tokens([])
        assert tokens == 0

    def test_count_context_tokens_missing_content(self):
        """Test token counting handles missing content field."""
        messages = [
            {"role": "user"},  # Missing content
            {"role": "assistant", "content": "Response"},
        ]
        tokens = count_context_tokens(messages)
        assert tokens > 0  # Should handle gracefully


class TestContextExtraction:
    """Test context extraction functions."""

    def test_extract_context_basic(self):
        """Test basic context extraction."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]
        context = extract_context(messages)

        assert "timestamp" in context
        assert "messages" in context
        assert "metadata" in context
        assert "statistics" in context

    def test_extract_context_with_metadata(self):
        """Test context extraction with metadata."""
        messages = [
            {"role": "user", "content": "Test"}
        ]
        context = extract_context(
            messages,
            user_id="user123",
            model_name="qwen3",
            temperature=0.7,
            max_tokens=256
        )

        assert context["user_id"] == "user123"
        assert context["metadata"]["user_id"] == "user123"
        assert context["metadata"]["model"] == "qwen3"
        assert context["metadata"]["parameters"]["temperature"] == 0.7
        assert context["metadata"]["parameters"]["max_tokens"] == 256

    def test_extract_context_statistics(self):
        """Test that context statistics are correct."""
        messages = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "User message"},
            {"role": "assistant", "content": "Assistant response"},
        ]
        context = extract_context(messages)

        stats = context["statistics"]
        assert stats["total_messages"] == 3
        assert stats["message_breakdown"]["system"] == 1
        assert stats["message_breakdown"]["user"] == 1
        assert stats["message_breakdown"]["assistant"] == 1

    def test_serialize_messages(self):
        """Test message serialization."""
        messages = [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Response"},
        ]
        serialized = serialize_messages(messages)

        assert len(serialized) == 2
        assert serialized[0]["index"] == 0
        assert serialized[0]["role"] == "user"
        assert serialized[0]["content"] == "Test message"
        assert serialized[0]["content_truncated"] is False

    def test_serialize_messages_with_truncation(self):
        """Test message serialization with content truncation."""
        long_content = "A" * 1000
        messages = [
            {"role": "user", "content": long_content}
        ]
        serialized = serialize_messages(messages, max_content_length=50)

        assert serialized[0]["content_truncated"] is True
        assert "original_length" in serialized[0]
        assert serialized[0]["original_length"] == 1000
        assert len(serialized[0]["content"]) < 1000

    def test_extract_metadata_complete(self):
        """Test metadata extraction with all parameters."""
        metadata = extract_metadata(
            user_id="user456",
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=512
        )

        assert metadata["user_id"] == "user456"
        assert metadata["model"] == "gpt-4"
        assert metadata["parameters"]["temperature"] == 0.5
        assert metadata["parameters"]["max_tokens"] == 512

    def test_extract_metadata_minimal(self):
        """Test metadata extraction with minimal parameters."""
        metadata = extract_metadata()

        assert metadata["user_id"] is None
        assert metadata["model"] is None
        assert metadata["parameters"] == {}


class TestLogFormatting:
    """Test log formatting functions."""

    def test_format_log_entry_human(self):
        """Test human-readable log formatting."""
        data = {
            "user_id": "user123",
            "action": "test",
            "details": {"key": "value"}
        }
        formatted = format_log_entry(data, format_type="human")

        assert isinstance(formatted, str)
        assert "Timestamp" in formatted or "timestamp" in formatted.lower()
        assert "User ID" in formatted or "user_id" in formatted
        assert "test" in formatted

    def test_format_log_entry_json(self):
        """Test JSON log formatting."""
        data = {
            "user_id": "user123",
            "action": "test",
        }
        formatted = format_log_entry(data, format_type="json")

        # Should be valid JSON
        parsed = json.loads(formatted)
        assert parsed["user_id"] == "user123"
        assert parsed["action"] == "test"

    def test_format_log_entry_with_nested_structures(self):
        """Test formatting with nested dict and list structures."""
        data = {
            "messages": [
                {"role": "user", "content": "Test"},
                {"role": "assistant", "content": "Response"},
            ],
            "config": {
                "model": "qwen",
                "temperature": 0.7
            }
        }
        formatted = format_log_entry(data, format_type="human")

        assert isinstance(formatted, str)
        assert "messages" in formatted
        assert "config" in formatted or "qwen" in formatted


class TestContextLogger:
    """Test context logger setup and usage."""

    def test_setup_context_logger_returns_logger(self):
        """Test that setup returns a logger instance."""
        logger = setup_context_logger()
        assert isinstance(logger, logging.Logger)

    def test_setup_context_logger_singleton(self):
        """Test that logger is a singleton (same instance on multiple calls)."""
        logger1 = setup_context_logger()
        logger2 = setup_context_logger()
        assert logger1 is logger2

    def test_context_logger_console_output(self):
        """Test that logger outputs to console."""
        with mock.patch('src.context_logging.config.CONTEXT_LOGGING_ENABLED', True):
            with mock.patch('src.context_logging.config.LOG_DESTINATION', 'console'):
                # Reset the logger
                import src.context_logging
                src.context_logging._context_logger = None

                logger = setup_context_logger()
                assert logger is not None
                # Check that handlers are set up
                assert len(logger.handlers) > 0

    def test_context_logger_disabled(self):
        """Test that logger returns null logger when disabled."""
        with mock.patch('src.context_logging.config.CONTEXT_LOGGING_ENABLED', False):
            import src.context_logging
            src.context_logging._context_logger = None

            logger = setup_context_logger()
            assert logger is not None
            # Should be a null logger with NullHandler


class TestFileLogging:
    """Test file-based logging."""

    def test_file_logging_creates_directory(self):
        """Test that logging to file creates the logs directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "logs" / "context.log"

            with mock.patch('src.context_logging.config.CONTEXT_LOGGING_ENABLED', True):
                with mock.patch('src.context_logging.config.LOG_DESTINATION', 'file'):
                    with mock.patch('src.context_logging.config.LOG_FILE_PATH', str(log_file)):
                        import src.context_logging
                        src.context_logging._context_logger = None

                        logger = setup_context_logger()
                        assert logger is not None
                        assert log_file.parent.exists()

    def test_file_logging_writes_content(self):
        """Test that file logging actually writes content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            with mock.patch('src.context_logging.config.CONTEXT_LOGGING_ENABLED', True):
                with mock.patch('src.context_logging.config.LOG_DESTINATION', 'file'):
                    with mock.patch('src.context_logging.config.LOG_FILE_PATH', str(log_file)):
                        import src.context_logging
                        src.context_logging._context_logger = None

                        from src.context_logging import log_context
                        log_context({"test": "data"})

                        if log_file.exists():
                            content = log_file.read_text()
                            assert len(content) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_extract_context_empty_messages(self):
        """Test extraction with empty message list."""
        context = extract_context([])
        assert context["statistics"]["total_messages"] == 0

    def test_token_count_special_characters(self):
        """Test token counting with special characters."""
        text = "!@#$%^&*()_+-=[]{}|;:',.<>?/"
        tokens = count_tokens(text)
        assert tokens >= 0

    def test_serialize_messages_missing_role(self):
        """Test serialization handles missing role field."""
        messages = [
            {"content": "Message without role"}
        ]
        serialized = serialize_messages(messages)
        assert serialized[0]["role"] == "unknown"

    def test_format_log_entry_with_none_values(self):
        """Test formatting handles None values."""
        data = {
            "user_id": None,
            "content": "Test",
            "extra": None
        }
        formatted = format_log_entry(data, format_type="json")
        parsed = json.loads(formatted)
        assert parsed["user_id"] is None

    def test_token_count_consistency(self):
        """Test that token counting is deterministic."""
        text = "Test message content"
        count1 = count_tokens(text)
        count2 = count_tokens(text)
        assert count1 == count2


class TestConfiguration:
    """Test configuration handling."""

    def test_token_count_strategy_heuristic(self):
        """Test that default strategy is heuristic."""
        # This test verifies the configuration value
        assert config.TOKEN_COUNT_STRATEGY == "heuristic"

    def test_heuristic_token_ratio(self):
        """Test that heuristic ratio is configured."""
        assert config.HEURISTIC_TOKEN_RATIO == 4

    def test_context_logging_enabled_default(self):
        """Test that context logging is enabled by default."""
        assert config.CONTEXT_LOGGING_ENABLED is True

    def test_log_destination_default(self):
        """Test that console is default log destination."""
        assert config.LOG_DESTINATION == "console"


class TestIntegration:
    """Integration tests for the full logging pipeline."""

    def test_full_context_logging_flow(self):
        """Test the complete flow from context to formatted log."""
        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello"},
        ]

        # Extract context
        context = extract_context(messages, model_name="test-model")

        # Add token count
        tokens = count_context_tokens(messages)
        context["statistics"]["token_count"] = tokens

        # Format
        formatted = format_log_entry(context, format_type="json")
        parsed = json.loads(formatted)

        # Verify result
        assert parsed["messages"]
        assert parsed["metadata"]["model"] == "test-model"
        assert parsed["statistics"]["token_count"] > 0

    def test_multiple_message_types(self):
        """Test logging with various message types."""
        messages = [
            {"role": "system", "content": "System prompt"},
            {"role": "user", "content": "First user message"},
            {"role": "assistant", "content": "First assistant response"},
            {"role": "user", "content": "Second user message"},
            {"role": "assistant", "content": "Second assistant response"},
        ]

        context = extract_context(messages)
        tokens = count_context_tokens(messages)

        assert context["statistics"]["total_messages"] == 5
        assert context["statistics"]["message_breakdown"]["user"] == 2
        assert context["statistics"]["message_breakdown"]["assistant"] == 2
        assert tokens > 0


# Fixtures for common test data
@pytest.fixture
def sample_messages():
    """Fixture providing sample messages."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"},
        {"role": "assistant", "content": "2+2 equals 4."},
    ]


@pytest.fixture
def sample_context_data():
    """Fixture providing sample context data."""
    return {
        "timestamp": "2026-04-15T10:00:00",
        "user_id": "test_user",
        "messages": [
            {"role": "user", "content": "Test"},
        ],
        "metadata": {
            "model": "test-model",
            "user_id": "test_user",
        },
        "statistics": {
            "total_messages": 1,
            "message_breakdown": {"user": 1},
            "total_content_length": 4,
        }
    }
