from __future__ import annotations

import pytest

from src.bootstrap import choose_model


@pytest.mark.unit
def test_choose_model_non_interactive_returns_default_without_prompt() -> None:
    prompted: list[bool] = []

    def _prompt(_: str) -> str:
        prompted.append(True)
        return "1"

    selected = choose_model("default", ["m1"], is_interactive=False, prompt=_prompt)

    assert selected == "default"
    assert prompted == []


@pytest.mark.unit
def test_choose_model_interactive_empty_models_returns_default() -> None:
    selected = choose_model("default", [], is_interactive=True, prompt=lambda _: "1")
    assert selected == "default"


@pytest.mark.unit
def test_choose_model_interactive_accepts_numeric_selection() -> None:
    output: list[str] = []

    selected = choose_model(
        "m2",
        ["m1", "m2", "m3"],
        is_interactive=True,
        prompt=lambda _: "1",
        out=output.append,
    )

    assert selected == "m1"
    assert any("Available models" in line for line in output)


@pytest.mark.unit
def test_choose_model_interactive_invalid_input_keeps_default_and_logs_warning(caplog) -> None:
    output: list[str] = []

    with caplog.at_level("WARNING"):
        selected = choose_model(
            "m2",
            ["m1", "m2"],
            is_interactive=True,
            prompt=lambda _: "not-a-number",
            out=output.append,
        )

    assert selected == "m2"
    assert any("Invalid model selection" in record.getMessage() for record in caplog.records)

