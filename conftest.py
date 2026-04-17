from __future__ import annotations

import asyncio
import inspect


def pytest_addoption(parser):  # type: ignore[no-untyped-def]
    # Prevent "Unknown config option: asyncio_mode" when pytest-asyncio is absent.
    parser.addini("asyncio_mode", "async test mode compatibility option", default="auto")


def pytest_configure(config):  # type: ignore[no-untyped-def]
    config.addinivalue_line("markers", "asyncio: mark async test functions")


def pytest_pyfunc_call(pyfuncitem):  # type: ignore[no-untyped-def]
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        asyncio.run(test_func(**pyfuncitem.funcargs))
        return True
    return None
