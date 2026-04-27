from __future__ import annotations

from src.agent.tools import _host_matches_allowlist


def test_host_matches_allowlist_empty() -> None:
    assert _host_matches_allowlist("example.com", []) is True
    assert _host_matches_allowlist("google.com", []) is True


def test_host_matches_allowlist_exact_match() -> None:
    allowlist = ["example.com"]
    assert _host_matches_allowlist("example.com", allowlist) is True
    assert _host_matches_allowlist("google.com", allowlist) is False


def test_host_matches_allowlist_case_insensitive() -> None:
    allowlist = ["example.com"]
    assert _host_matches_allowlist("EXAMPLE.COM", allowlist) is True
    assert _host_matches_allowlist("Example.Com", allowlist) is True


def test_host_matches_allowlist_wildcard_suffix() -> None:
    allowlist = ["*.example.com"]
    assert _host_matches_allowlist("docs.example.com", allowlist) is True
    assert _host_matches_allowlist("api.example.com", allowlist) is True
    assert _host_matches_allowlist("example.com", allowlist) is False
    assert _host_matches_allowlist("google.com", allowlist) is False


def test_host_matches_allowlist_wildcard_case_insensitive() -> None:
    allowlist = ["*.example.com"]
    assert _host_matches_allowlist("DOCS.EXAMPLE.COM", allowlist) is True
    assert _host_matches_allowlist("Docs.Example.Com", allowlist) is True


def test_host_matches_allowlist_multiple_entries() -> None:
    allowlist = ["example.com", "google.com", "*.internal.local"]
    assert _host_matches_allowlist("example.com", allowlist) is True
    assert _host_matches_allowlist("google.com", allowlist) is True
    assert _host_matches_allowlist("api.internal.local", allowlist) is True
    assert _host_matches_allowlist("github.com", allowlist) is False


def test_host_matches_allowlist_deep_subdomain() -> None:
    allowlist = ["*.example.com"]
    assert _host_matches_allowlist("a.b.example.com", allowlist) is True
    assert _host_matches_allowlist("deep.nested.example.com", allowlist) is True


def test_host_matches_allowlist_wildcard_no_parent() -> None:
    allowlist = ["*.example.com"]
    assert _host_matches_allowlist("notexample.com", allowlist) is False


