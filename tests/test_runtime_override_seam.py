import pytest

from src.runtime import (
    AppRuntime,
    get_runtime,
    reset_runtime_for_testing,
    set_runtime_for_testing,
)


def test_runtime_override_and_reset_cycle(fake_runtime: AppRuntime) -> None:
    reset_runtime_for_testing()

    with pytest.raises(RuntimeError):
        get_runtime()

    set_runtime_for_testing(fake_runtime)
    try:
        assert get_runtime() is fake_runtime
    finally:
        reset_runtime_for_testing()

    with pytest.raises(RuntimeError):
        get_runtime()

