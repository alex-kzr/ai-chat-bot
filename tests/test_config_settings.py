from __future__ import annotations

import pytest

from src.config import SettingsError, load_settings


def _base_env() -> dict[str, str]:
    return {
        "BOT_TOKEN": "token",
        "OLLAMA_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "qwen3:0.6b",
    }


def test_load_settings_success_defaults() -> None:
    settings = load_settings(env=_base_env(), load_dotenv_file=False)
    assert settings.bot_token == "token"
    assert settings.chat_model == "qwen3:0.6b"
    assert settings.history.max_messages == 20
    assert settings.logging.level == "INFO"


def test_load_settings_rejects_invalid_keep_recent_boundary() -> None:
    env = _base_env() | {"SUMMARY_THRESHOLD": "5", "SUMMARY_KEEP_RECENT": "5"}
    with pytest.raises(SettingsError):
        load_settings(env=env, load_dotenv_file=False)


def test_runtime_model_override() -> None:
    settings = load_settings(env=_base_env(), load_dotenv_file=False)
    settings.set_chat_model("llama3.2:3b")
    assert settings.chat_model == "llama3.2:3b"


def test_load_settings_accepts_log_level_case_insensitive() -> None:
    env = _base_env() | {"LOG_LEVEL": "debug"}
    settings = load_settings(env=env, load_dotenv_file=False)
    assert settings.logging.level == "DEBUG"


def test_load_settings_rejects_invalid_log_level() -> None:
    env = _base_env() | {"LOG_LEVEL": "verbose"}
    with pytest.raises(SettingsError):
        load_settings(env=env, load_dotenv_file=False)
