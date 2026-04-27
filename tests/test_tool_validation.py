from __future__ import annotations

import pytest

from src.agent.tools import validate_tool_args, TOOLS


def test_validate_tool_args_valid_calculator() -> None:
    spec = TOOLS["calculator"]
    is_valid, error = validate_tool_args(spec, {"expression": "2+2"})
    assert is_valid is True
    assert error is None


def test_validate_tool_args_valid_http_request_url_only() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {"url": "https://example.com"})
    assert is_valid is True
    assert error is None


def test_validate_tool_args_valid_http_request_with_method() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {"url": "https://example.com", "method": "GET"})
    assert is_valid is True
    assert error is None


def test_validate_tool_args_missing_required_argument() -> None:
    spec = TOOLS["calculator"]
    is_valid, error = validate_tool_args(spec, {})
    assert is_valid is False
    assert "expression" in error
    assert "required" in error.lower()


def test_validate_tool_args_missing_required_url() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {})
    assert is_valid is False
    assert "url" in error
    assert "required" in error.lower()


def test_validate_tool_args_wrong_type_string_instead_of_string() -> None:
    spec = TOOLS["calculator"]
    is_valid, error = validate_tool_args(spec, {"expression": 123})
    assert is_valid is False
    assert "expression" in error
    assert "string" in error.lower()


def test_validate_tool_args_wrong_type_integer_instead_of_string() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {"url": 42, "method": "GET"})
    assert is_valid is False
    assert "url" in error
    assert "string" in error.lower()


def test_validate_tool_args_wrong_type_boolean_instead_of_string() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {"url": True, "method": "GET"})
    assert is_valid is False
    assert "url" in error
    assert "string" in error.lower()


def test_validate_tool_args_unknown_key() -> None:
    spec = TOOLS["calculator"]
    is_valid, error = validate_tool_args(spec, {"expression": "2+2", "unknown_key": "value"})
    assert is_valid is False
    assert "unknown_key" in error
    assert "unknown" in error.lower()


def test_validate_tool_args_multiple_unknown_keys() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {"url": "https://example.com", "foo": "bar"})
    assert is_valid is False
    assert "foo" in error


def test_validate_tool_args_non_dict() -> None:
    spec = TOOLS["calculator"]
    is_valid, error = validate_tool_args(spec, "not a dict")
    assert is_valid is False
    assert "dict" in error.lower()


def test_validate_tool_args_none_instead_of_dict() -> None:
    spec = TOOLS["calculator"]
    is_valid, error = validate_tool_args(spec, None)
    assert is_valid is False
    assert "dict" in error.lower()


def test_validate_tool_args_optional_method_omitted() -> None:
    spec = TOOLS["http_request"]
    is_valid, error = validate_tool_args(spec, {"url": "https://example.com"})
    assert is_valid is True
    assert error is None
