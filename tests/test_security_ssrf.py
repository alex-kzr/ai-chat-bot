from __future__ import annotations

import pytest

from src.agent.tools import _is_private_ip, _check_host_security, http_request
import ipaddress


def test_is_private_ip_loopback_v4() -> None:
    assert _is_private_ip(ipaddress.ip_address("127.0.0.1"))
    assert _is_private_ip(ipaddress.ip_address("127.255.255.255"))


def test_is_private_ip_loopback_v6() -> None:
    assert _is_private_ip(ipaddress.ip_address("::1"))


def test_is_private_ip_rfc1918() -> None:
    assert _is_private_ip(ipaddress.ip_address("10.0.0.0"))
    assert _is_private_ip(ipaddress.ip_address("10.255.255.255"))
    assert _is_private_ip(ipaddress.ip_address("172.16.0.0"))
    assert _is_private_ip(ipaddress.ip_address("172.31.255.255"))
    assert _is_private_ip(ipaddress.ip_address("192.168.0.0"))
    assert _is_private_ip(ipaddress.ip_address("192.168.255.255"))


def test_is_private_ip_link_local() -> None:
    assert _is_private_ip(ipaddress.ip_address("169.254.0.0"))
    assert _is_private_ip(ipaddress.ip_address("169.254.169.254"))
    assert _is_private_ip(ipaddress.ip_address("169.254.255.255"))


def test_is_private_ip_ipv6_link_local() -> None:
    assert _is_private_ip(ipaddress.ip_address("fe80::1"))


def test_is_private_ip_ipv6_unique_local() -> None:
    assert _is_private_ip(ipaddress.ip_address("fc00::1"))
    assert _is_private_ip(ipaddress.ip_address("fd00::1"))


def test_is_private_ip_public_ipv4() -> None:
    assert not _is_private_ip(ipaddress.ip_address("8.8.8.8"))
    assert not _is_private_ip(ipaddress.ip_address("1.1.1.1"))


def test_is_private_ip_public_ipv6() -> None:
    assert not _is_private_ip(ipaddress.ip_address("2001:4860:4860::8888"))


@pytest.mark.asyncio
async def test_check_host_security_loopback() -> None:
    is_safe, error = await _check_host_security("127.0.0.1")
    assert is_safe is False
    assert "private" in error.lower() or "blocked" in error.lower()


@pytest.mark.asyncio
async def test_check_host_security_metadata_endpoint() -> None:
    is_safe, error = await _check_host_security("169.254.169.254")
    assert is_safe is False
    assert "private" in error.lower() or "blocked" in error.lower()


@pytest.mark.asyncio
async def test_check_host_security_rfc1918() -> None:
    is_safe, error = await _check_host_security("10.0.0.1")
    assert is_safe is False


@pytest.mark.asyncio
async def test_check_host_security_public_domain() -> None:
    is_safe, error = await _check_host_security("example.com")
    assert is_safe is True
    assert error is None


@pytest.mark.asyncio
async def test_http_request_rejects_loopback() -> None:
    result = await http_request({"url": "http://127.0.0.1/"})
    assert result.startswith("[tool_error]")
    assert "blocked_target" in result.lower() or "private" in result.lower()


@pytest.mark.asyncio
async def test_http_request_rejects_metadata_endpoint() -> None:
    result = await http_request({"url": "http://169.254.169.254/latest/meta-data/"})
    assert result.startswith("[tool_error]")
    assert "blocked_target" in result.lower() or "private" in result.lower()


@pytest.mark.asyncio
async def test_http_request_rejects_rfc1918() -> None:
    result = await http_request({"url": "http://10.0.0.1/"})
    assert result.startswith("[tool_error]")


@pytest.mark.asyncio
async def test_http_request_rejects_ftp_scheme() -> None:
    result = await http_request({"url": "ftp://example.com/"})
    assert result.startswith("[tool_error]")
    assert "http or https" in result.lower()


@pytest.mark.asyncio
async def test_http_request_rejects_file_scheme() -> None:
    result = await http_request({"url": "file:///etc/passwd"})
    assert result.startswith("[tool_error]")
    assert "http or https" in result.lower()
