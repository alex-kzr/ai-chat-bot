import ast
import asyncio
import ipaddress
import json
import logging
import socket
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any, Callable
from urllib.parse import urldefrag, urljoin, urlparse

import httpx

from src.errors import ToolExecutionError

logger = logging.getLogger(__name__)


def _settings():
    from src.runtime import get_runtime

    return get_runtime().settings


@dataclass
class ToolSpec:
    """Specification for an agent tool."""

    name: str
    description: str
    args_schema: dict
    run: Callable


def validate_tool_args(spec: ToolSpec, args: dict) -> tuple[bool, str | None]:
    """Validate tool arguments against the tool spec's schema.

    Returns:
        (is_valid, error_message) — (True, None) if valid; (False, reason) if invalid.
    """
    if not isinstance(args, dict):
        return False, f"invalid_args: arguments must be a dict, got {type(args).__name__}"

    provided_keys = set(args.keys())
    schema_keys = set(spec.args_schema.keys())

    for key in provided_keys:
        if key not in schema_keys:
            return False, f"invalid_args: {key}: unknown key"

    for key, field_spec in spec.args_schema.items():
        is_required = field_spec.get("required", True)
        field_type = field_spec.get("type", "string")

        if key not in args:
            if is_required:
                return False, f"invalid_args: {key}: required argument missing"
            continue

        value = args[key]

        if field_type == "string":
            if not isinstance(value, str):
                return False, f"invalid_args: {key}: expected string, got {type(value).__name__}"
        elif field_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return False, f"invalid_args: {key}: expected integer, got {type(value).__name__}"
        elif field_type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return False, f"invalid_args: {key}: expected number, got {type(value).__name__}"
        elif field_type == "boolean":
            if not isinstance(value, bool):
                return False, f"invalid_args: {key}: expected boolean, got {type(value).__name__}"

    return True, None


@dataclass
class FetchPayload:
    """HTTP fetch payload with metadata and deterministic truncation info."""

    requested_url: str
    final_url: str
    status_code: int
    reason_phrase: str
    content_type: str
    encoding: str
    body: str
    body_bytes: int
    truncated: bool


async def calculator(args: dict) -> str:
    """Evaluate safe arithmetic expressions.

    Args:
        args: {"expression": str}

    Returns:
        Result as string or error message.
    """
    try:
        expression = args.get("expression", "")
        if not expression:
            return "[tool_error] Missing expression argument"

        result = _eval_safe_arithmetic(expression)
        if isinstance(result, float) and result.is_integer():
            return str(int(result))
        return str(result)
    except (ValueError, TypeError, ZeroDivisionError, SyntaxError) as e:
        return f"[tool_error] {type(e).__name__}: {e}"


async def http_request(args: dict) -> str:
    """Fetch and process a web page with controlled resource loading.

    Args:
        args: {"url": str, "method": "GET"} (method defaults to GET)

    Returns:
        Deterministic JSON string with page summary and resource diagnostics.
    """
    try:
        started_at = asyncio.get_running_loop().time()
        raw_url = str(args.get("url", "")).strip()
        if not raw_url:
            return "[tool_error] Missing url argument"

        method = str(args.get("method", "GET")).upper().strip()
        if method not in {"GET"}:
            return f"[tool_error] Unsupported method: {method}. Allowed: GET"

        normalized_url = _normalize_url(raw_url)
        if not normalized_url:
            return "[tool_error] URL must use a valid http or https address"

        parsed_initial = urlparse(normalized_url)
        is_safe, error_msg = await _check_host_security(parsed_initial.netloc)
        if not is_safe:
            return f"[tool_error] {error_msg}"

        settings = _settings()

        headers = {
            "User-Agent": settings.agent.tools.user_agent,
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8",
        }
        timeout = httpx.Timeout(settings.agent.tools.timeout)
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
            document = await _fetch_text_with_redirects(
                client=client,
                method=method,
                url=normalized_url,
                headers=headers,
                byte_limit=settings.agent.tools.max_html_bytes,
            )

            if isinstance(document, str):
                return document

            if document.status_code >= 400:
                return (
                    f"[tool_error] HTTP {document.status_code} {document.reason_phrase} "
                    f"for {document.final_url}"
                )

            if "html" not in document.content_type.lower():
                return (
                    "[tool_error] Expected HTML content but received "
                    f"'{document.content_type or 'unknown'}' from {document.final_url}"
                )

            parser = _PageParser()
            parser.feed(document.body)
            parser.close()

            resource_summary = await _load_resources(
                client=client,
                base_url=document.final_url,
                resource_refs=parser.resources,
                headers=headers,
            )

        main_text = _normalize_whitespace(" ".join(parser.text_chunks))
        title = _normalize_whitespace(" ".join(parser.title_chunks))

        main_text_truncated = False
        if len(main_text) > settings.agent.tools.max_main_text_chars:
            main_text = main_text[: settings.agent.tools.max_main_text_chars].rstrip()
            main_text_truncated = True

        payload = {
            "url": document.final_url,
            "request": {
                "method": method,
            },
            "status": {
                "code": document.status_code,
                "reason": document.reason_phrase,
            },
            "title": title,
            "main_text": main_text,
            "main_text_truncated": main_text_truncated,
            "html": {
                "content_type": document.content_type,
                "encoding": document.encoding,
                "bytes_read": document.body_bytes,
                "truncated": document.truncated,
            },
            "resources": resource_summary,
        }
        logger.info(
            "HTTP_TOOL_RESULT %s",
            json.dumps(
                {
                    "event": "http_tool_result",
                    "url": document.final_url,
                    "status_code": document.status_code,
                    "resources_discovered": resource_summary["discovered_count"],
                    "resources_loaded": len(resource_summary["loaded"]),
                    "resources_failed": len(resource_summary["failed"]),
                    "resources_skipped": len(resource_summary["skipped"]),
                    "duration_ms": int((asyncio.get_running_loop().time() - started_at) * 1000),
                },
                sort_keys=True,
            ),
        )
        return _serialize_observation(payload)
    except asyncio.TimeoutError:
        return "[tool_error] Request timeout"
    except httpx.TimeoutException:
        return "[tool_error] Request timeout"
    except (httpx.HTTPError, ValueError, ToolExecutionError) as e:
        return f"[tool_error] {type(e).__name__}: {e}"


class _PageParser(HTMLParser):
    """Extract deterministic page summary data from HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_title = False
        self.in_script = False
        self.in_style = False
        self.title_chunks: list[str] = []
        self.text_chunks: list[str] = []
        self.resources: list[dict[str, str]] = []
        self._resource_keys: set[tuple[str, str]] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_l = tag.lower()

        if tag_l == "title":
            self.in_title = True
            return
        if tag_l == "script":
            self.in_script = True
            src = attrs_dict.get("src", "").strip()
            self._add_resource("script", src)
            return
        if tag_l == "style":
            self.in_style = True
            return
        if tag_l == "link":
            href = attrs_dict.get("href", "").strip()
            self._add_resource("link", href)
            return
        if tag_l == "img":
            src = attrs_dict.get("src", "").strip()
            self._add_resource("img", src)
            return

    def handle_endtag(self, tag: str) -> None:
        tag_l = tag.lower()
        if tag_l == "title":
            self.in_title = False
        elif tag_l == "script":
            self.in_script = False
        elif tag_l == "style":
            self.in_style = False

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if not text:
            return
        if self.in_title:
            self.title_chunks.append(text)
            return
        if self.in_script or self.in_style:
            return
        self.text_chunks.append(text)

    def _add_resource(self, kind: str, raw_url: str) -> None:
        if not raw_url:
            return
        key = (kind, raw_url)
        if key in self._resource_keys:
            return
        self._resource_keys.add(key)
        self.resources.append({"type": kind, "url": raw_url})


def _is_private_ip(ip_obj: ipaddress.ip_address) -> bool:
    """Check if an IP is loopback, private, link-local, or reserved."""
    return (
        ip_obj.is_loopback
        or ip_obj.is_private
        or ip_obj.is_link_local
        or ip_obj.is_reserved
        or ip_obj.is_multicast
    )


async def _check_host_security(hostname: str) -> tuple[bool, str | None]:
    """Verify hostname does not resolve to a private/loopback IP.

    Returns:
        (is_safe, error_reason) — (True, None) if safe; (False, reason) if blocked.
    """
    try:
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(
            None,
            socket.getaddrinfo,
            hostname,
            None,
            socket.AF_UNSPEC,
            socket.SOCK_STREAM,
        )

        if not results:
            return False, "could_not_resolve_hostname"

        for family, socktype, proto, canonname, sockaddr in results:
            ip_str = sockaddr[0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                if _is_private_ip(ip_obj):
                    return False, f"blocked_target: resolved to private IP {ip_str}"
            except ValueError:
                return False, f"invalid_ip_address: {ip_str}"

        return True, None
    except (socket.gaierror, OSError) as e:
        return False, f"dns_resolution_failed: {e}"


def _normalize_url(raw_url: str) -> str | None:
    normalized = urldefrag(raw_url.strip())[0]
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return normalized


async def _fetch_text_with_redirects(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict[str, str],
    byte_limit: int,
    max_redirects: int = 5,
) -> FetchPayload | str:
    """Fetch with manual redirect handling and SSRF checks on each hop.

    Returns:
        FetchPayload on success, or a string error message on failure.
    """
    current_url = url
    for hop in range(max_redirects + 1):
        parsed = urlparse(current_url)
        is_safe, error_msg = await _check_host_security(parsed.netloc)
        if not is_safe:
            return f"[tool_error] {error_msg}"

        content = bytearray()
        truncated = False

        try:
            async with client.stream(method, current_url, headers=headers) as response:
                async for chunk in response.aiter_bytes():
                    if not chunk:
                        continue
                    allowed = byte_limit - len(content)
                    if allowed <= 0:
                        truncated = True
                        break
                    if len(chunk) > allowed:
                        content.extend(chunk[:allowed])
                        truncated = True
                        break
                    content.extend(chunk)

                status_code = response.status_code
                reason_phrase = response.reason_phrase or ""
                content_type = response.headers.get("content-type", "")
                location = response.headers.get("location", "")

                if status_code in {301, 302, 303, 307, 308} and location:
                    current_url = urljoin(current_url, location)
                    if not _normalize_url(current_url):
                        return f"[tool_error] blocked_target: redirect to invalid URL"
                    continue

                encoding = response.encoding or "utf-8"
                body = bytes(content).decode(encoding, errors="replace")

                return FetchPayload(
                    requested_url=url,
                    final_url=str(response.url),
                    status_code=status_code,
                    reason_phrase=reason_phrase,
                    content_type=content_type,
                    encoding=encoding,
                    body=body,
                    body_bytes=len(content),
                    truncated=truncated,
                )
        except (httpx.HTTPError, asyncio.TimeoutError) as e:
            return f"[tool_error] {type(e).__name__}"

    return f"[tool_error] blocked_target: too many redirects"


async def _fetch_text(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    headers: dict[str, str],
    byte_limit: int,
) -> FetchPayload:
    content = bytearray()
    truncated = False

    async with client.stream(method, url, headers=headers) as response:
        async for chunk in response.aiter_bytes():
            if not chunk:
                continue
            allowed = byte_limit - len(content)
            if allowed <= 0:
                truncated = True
                break
            if len(chunk) > allowed:
                content.extend(chunk[:allowed])
                truncated = True
                break
            content.extend(chunk)

        encoding = response.encoding or "utf-8"
        body = bytes(content).decode(encoding, errors="replace")
        content_type = response.headers.get("content-type", "")
        return FetchPayload(
            requested_url=url,
            final_url=str(response.url),
            status_code=response.status_code,
            reason_phrase=response.reason_phrase,
            content_type=content_type,
            encoding=encoding,
            body=body,
            body_bytes=len(content),
            truncated=truncated,
        )


async def _fetch_resource(
    client: httpx.AsyncClient,
    url: str,
    headers: dict[str, str],
    byte_limit: int,
) -> dict[str, Any]:
    content = bytearray()
    truncated = False
    try:
        async with client.stream("GET", url, headers=headers) as response:
            async for chunk in response.aiter_bytes():
                if not chunk:
                    continue
                allowed = byte_limit - len(content)
                if allowed <= 0:
                    truncated = True
                    break
                if len(chunk) > allowed:
                    content.extend(chunk[:allowed])
                    truncated = True
                    break
                content.extend(chunk)

            if response.status_code >= 400:
                return {
                    "ok": False,
                    "status_code": response.status_code,
                    "reason": f"http_{response.status_code}",
                    "bytes_read": len(content),
                    "truncated": truncated,
                }

            return {
                "ok": True,
                "status_code": response.status_code,
                "bytes_read": len(content),
                "content_type": response.headers.get("content-type", ""),
                "truncated": truncated,
            }
    except httpx.TimeoutException:
        return {"ok": False, "reason": "timeout", "status_code": 0, "bytes_read": len(content), "truncated": truncated}
    except httpx.HTTPError as exc:
        return {
            "ok": False,
            "reason": f"http_error:{type(exc).__name__}",
            "status_code": 0,
            "bytes_read": len(content),
            "truncated": truncated,
        }


async def _load_resources(
    client: httpx.AsyncClient,
    base_url: str,
    resource_refs: list[dict[str, str]],
    headers: dict[str, str],
) -> dict[str, Any]:
    settings = _settings()
    loaded: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

    base = urlparse(base_url)
    max_count = settings.agent.tools.max_resource_count
    max_bytes_each = settings.agent.tools.max_resource_bytes
    max_bytes_total = settings.agent.tools.max_total_resource_bytes
    bytes_total = 0

    for ref in resource_refs:
        kind = ref["type"]
        resolved = _resolve_resource_url(base_url, ref["url"])
        if not resolved:
            skipped.append({"type": kind, "url": ref["url"], "reason": "invalid_url"})
            continue

        if not _is_same_origin(base, urlparse(resolved)):
            skipped.append({"type": kind, "url": resolved, "reason": "cross_origin"})
            continue

        parsed_resolved = urlparse(resolved)
        is_safe, error_msg = await _check_host_security(parsed_resolved.netloc)
        if not is_safe:
            skipped.append({"type": kind, "url": resolved, "reason": "blocked_by_ssrf_guard"})
            continue

        if len(loaded) >= max_count:
            skipped.append({"type": kind, "url": resolved, "reason": "count_limit"})
            continue

        remaining = max_bytes_total - bytes_total
        if remaining <= 0:
            skipped.append({"type": kind, "url": resolved, "reason": "total_size_limit"})
            continue

        per_resource_limit = min(max_bytes_each, remaining)
        fetched = await _fetch_resource(
            client=client,
            url=resolved,
            headers=headers,
            byte_limit=per_resource_limit,
        )

        if not fetched["ok"]:
            failed.append(
                {
                    "type": kind,
                    "url": resolved,
                    "reason": fetched.get("reason", "fetch_failed"),
                    "status_code": fetched.get("status_code", 0),
                }
            )
            continue

        bytes_total += int(fetched["bytes_read"])
        loaded.append(
            {
                "type": kind,
                "url": resolved,
                "status_code": fetched.get("status_code", 0),
                "bytes_read": fetched.get("bytes_read", 0),
                "content_type": fetched.get("content_type", ""),
                "truncated": bool(fetched.get("truncated", False)),
            }
        )

    return {
        "policy": {
            "origin": f"{base.scheme}://{base.netloc}",
            "same_origin_only": True,
            "max_resource_count": max_count,
            "max_resource_bytes": max_bytes_each,
            "max_total_resource_bytes": max_bytes_total,
        },
        "discovered_count": len(resource_refs),
        "loaded": loaded,
        "skipped": skipped,
        "failed": failed,
    }


def _resolve_resource_url(base_url: str, candidate: str) -> str | None:
    resolved = urldefrag(urljoin(base_url, candidate.strip()))[0]
    parsed = urlparse(resolved)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None
    return resolved


def _is_same_origin(base: Any, target: Any) -> bool:
    return (base.scheme, base.netloc) == (target.scheme, target.netloc)


def _normalize_whitespace(text: str) -> str:
    return " ".join(text.split())


def _serialize_observation(payload: dict[str, Any]) -> str:
    max_chars = _settings().agent.tools.max_observation_chars

    full = json.dumps(payload, ensure_ascii=False, indent=2)
    if len(full) <= max_chars:
        return full

    compact = dict(payload)
    compact["main_text"] = str(compact.get("main_text", ""))[:1000]
    compact["main_text_truncated"] = True
    resources = compact.get("resources", {})
    compact["resources"] = {
        "policy": resources.get("policy", {}),
        "discovered_count": resources.get("discovered_count", 0),
        "loaded_count": len(resources.get("loaded", [])),
        "skipped_count": len(resources.get("skipped", [])),
        "failed_count": len(resources.get("failed", [])),
    }
    compact["note"] = "Observation compacted due to size limits."
    serialized = json.dumps(compact, ensure_ascii=False, indent=2)
    if len(serialized) <= max_chars:
        return serialized

    minimal = {
        "url": payload.get("url", ""),
        "status": payload.get("status", {}),
        "title": payload.get("title", ""),
        "main_text": str(payload.get("main_text", ""))[:300],
        "note": "Observation heavily truncated due to size limits.",
    }
    return json.dumps(minimal, ensure_ascii=False, indent=2)


def _eval_safe_arithmetic(expression: str) -> float:
    """Safely evaluate arithmetic expressions using AST.

    Only allows: +, -, *, /, //, %, ** operators on numbers.
    Rejects: imports, function calls, attribute access, subscripts, etc.

    Args:
        expression: String like "2 + 2 * 3"

    Returns:
        Numeric result.

    Raises:
        ValueError: If expression contains disallowed constructs.
    """
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Invalid syntax: {e}")

    return _eval_node(tree.body)


def _eval_node(node: ast.expr) -> float:
    """Recursively evaluate an AST node, rejecting unsafe constructs."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value).__name__}")

    if isinstance(node, ast.Num):
        return float(node.n)

    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op = node.op

        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            if right == 0:
                raise ValueError("Division by zero")
            return left / right
        if isinstance(op, ast.FloorDiv):
            if right == 0:
                raise ValueError("Division by zero")
            return float(left // right)
        if isinstance(op, ast.Mod):
            if right == 0:
                raise ValueError("Modulo by zero")
            return float(left % right)
        if isinstance(op, ast.Pow):
            return left ** right

        raise ValueError(f"Unsupported binary operator: {op.__class__.__name__}")

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op = node.op

        if isinstance(op, ast.UAdd):
            return operand
        if isinstance(op, ast.USub):
            return -operand

        raise ValueError(f"Unsupported unary operator: {op.__class__.__name__}")

    raise ValueError(f"Unsafe or unsupported expression node: {ast.dump(node)}")


TOOLS: dict[str, ToolSpec] = {
    "calculator": ToolSpec(
        name="calculator",
        description="Evaluate safe arithmetic expressions (e.g., '2+2*3'). Supports +, -, *, /, //, %, ** operators.",
        args_schema={
            "expression": {
                "type": "string",
                "description": "Arithmetic expression to evaluate (e.g., '2+2*3')",
                "required": True,
            }
        },
        run=calculator,
    ),
    "http_request": ToolSpec(
        name="http_request",
        description=(
            "Fetch an HTML page via deterministic HTTP settings, discover same-origin linked resources "
            "(script/link/img) under strict limits, and return a compact structured JSON observation."
        ),
        args_schema={
            "url": {
                "type": "string",
                "description": "HTTP/HTTPS URL to fetch",
                "required": True,
            },
            "method": {
                "type": "string",
                "description": "HTTP method (default: GET, only GET supported)",
                "required": False,
            },
        },
        run=http_request,
    ),
}
