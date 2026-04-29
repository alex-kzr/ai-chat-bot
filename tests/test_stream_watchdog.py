from __future__ import annotations

import asyncio
import json

import pytest

from src.config import load_settings
from src.errors import OllamaProtocolError, OllamaTransportError
from src.ollama_gateway import OllamaGateway


def _settings_for_tests(*, stream_timeout: int = 1, max_repeat_chunks: int = 3):
    return load_settings(
        env={
            "BOT_TOKEN": "test-token",
            "OLLAMA_URL": "http://localhost:11434",
            "OLLAMA_MODEL": "test-model",
            "AGENT_LLM_STREAM_TIMEOUT": str(stream_timeout),
            "AGENT_MAX_REPEAT_STREAM_CHUNKS": str(max_repeat_chunks),
            "CONTEXT_LOGGING_ENABLED": "false",
            "SYSTEM_PROMPT_ENABLED": "false",
        },
        load_dotenv_file=False,
    )


class _FakeStreamResponse:
    def __init__(self, lines: list[object]):
        self._lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _tb):
        return False

    def raise_for_status(self) -> None:
        return None

    def aiter_lines(self):
        async def _gen():
            for item in self._lines:
                if isinstance(item, asyncio.Future):
                    await item
                    continue
                yield str(item)

        return _gen()


class _FakeAsyncClient:
    def __init__(self, *, timeout: float):
        self._timeout = timeout
        self.last_json: object | None = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _tb):
        return False

    def stream(self, _method: str, _url: str, *, json: object):
        self.last_json = json
        return self._stream_response

    async def post(self, _url: str, *, json: object):
        self.last_json = json
        return self._post_response


class _FakePostResponse:
    def __init__(self, text: str):
        self.text = text

    def raise_for_status(self) -> None:
        return None


@pytest.mark.unit
async def test_stream_watchdog_aborts_on_repeated_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_for_tests(stream_timeout=1, max_repeat_chunks=3)
    gateway = OllamaGateway(settings=settings)

    line = json.dumps({"response": "x", "thinking": "", "done": False})
    client = _FakeAsyncClient(timeout=1.0)
    client._stream_response = _FakeStreamResponse([line, line, line, line])
    monkeypatch.setattr("src.ollama_gateway.httpx.AsyncClient", lambda timeout: client)

    with pytest.raises(OllamaProtocolError):
        await gateway.generate_streamed_text("prompt", model="test-model")


@pytest.mark.unit
async def test_stream_watchdog_aborts_on_stall(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_for_tests(stream_timeout=1, max_repeat_chunks=10)
    gateway = OllamaGateway(settings=settings)

    stalled = asyncio.get_running_loop().create_future()
    client = _FakeAsyncClient(timeout=1.0)
    client._stream_response = _FakeStreamResponse([stalled])
    monkeypatch.setattr("src.ollama_gateway.httpx.AsyncClient", lambda timeout: client)

    with pytest.raises(OllamaTransportError):
        await gateway.generate_streamed_text("prompt", model="test-model")


@pytest.mark.integration
async def test_stream_requests_include_stop_sequences(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_for_tests(stream_timeout=1, max_repeat_chunks=10)
    gateway = OllamaGateway(settings=settings)

    line = json.dumps({"response": "ok", "thinking": "", "done": True})
    client = _FakeAsyncClient(timeout=1.0)
    client._stream_response = _FakeStreamResponse([line])
    monkeypatch.setattr("src.ollama_gateway.httpx.AsyncClient", lambda timeout: client)

    content, thinking = await gateway.generate_streamed_text("prompt", model="test-model")
    assert content == "ok"
    assert thinking == ""
    assert isinstance(client.last_json, dict)
    assert "stop" in client.last_json


@pytest.mark.integration
async def test_generate_once_requests_include_stop_sequences(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = _settings_for_tests(stream_timeout=1, max_repeat_chunks=10)
    gateway = OllamaGateway(settings=settings)

    response_text = json.dumps({"response": "ok", "done": True})
    client = _FakeAsyncClient(timeout=1.0)
    client._post_response = _FakePostResponse(response_text)
    monkeypatch.setattr("src.ollama_gateway.httpx.AsyncClient", lambda timeout: client)

    content = await gateway.generate_once("prompt", model="test-model")
    assert content == "ok"
    assert isinstance(client.last_json, dict)
    assert "stop" in client.last_json
