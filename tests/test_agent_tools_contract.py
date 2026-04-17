from __future__ import annotations

import pytest

from src.agent.tools import calculator, http_request


@pytest.mark.asyncio
async def test_calculator_valid_expression() -> None:
    result = await calculator({"expression": "2+2*3"})
    assert result == "8"


@pytest.mark.asyncio
async def test_calculator_missing_expression() -> None:
    result = await calculator({})
    assert result.startswith("[tool_error]")


@pytest.mark.asyncio
async def test_http_request_rejects_missing_url() -> None:
    result = await http_request({})
    assert result.startswith("[tool_error]")


@pytest.mark.asyncio
async def test_http_request_rejects_non_get() -> None:
    result = await http_request({"url": "https://example.com", "method": "POST"})
    assert result.startswith("[tool_error]")
