from __future__ import annotations

import pytest

from src.config import load_settings, SecuritySettings


def test_max_user_input_chars_default() -> None:
    env = {"BOT_TOKEN": "test_token"}
    settings = load_settings(env=env, load_dotenv_file=False)
    assert settings.security.max_user_input_chars == 4000


def test_max_user_input_chars_custom() -> None:
    env = {"MAX_USER_INPUT_CHARS": "5000", "BOT_TOKEN": "test_token"}
    settings = load_settings(env=env, load_dotenv_file=False)
    assert settings.security.max_user_input_chars == 5000


def test_max_user_input_chars_below_minimum() -> None:
    from src.config import SettingsError
    env = {"MAX_USER_INPUT_CHARS": "50", "BOT_TOKEN": "test_token"}
    with pytest.raises(SettingsError):
        load_settings(env=env, load_dotenv_file=False)


def test_max_user_input_chars_at_minimum() -> None:
    env = {"MAX_USER_INPUT_CHARS": "100", "BOT_TOKEN": "test_token"}
    settings = load_settings(env=env, load_dotenv_file=False)
    assert settings.security.max_user_input_chars == 100


def test_security_settings_dataclass() -> None:
    sec = SecuritySettings(max_user_input_chars=2000)
    assert sec.max_user_input_chars == 2000
