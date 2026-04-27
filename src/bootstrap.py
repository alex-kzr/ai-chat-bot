from __future__ import annotations

import asyncio
import logging
import sys

from . import config
from .bot import run_bot
from .config import Settings, SettingsError
from .errors import OllamaTransportError
from .runtime import create_runtime, set_runtime


def configure_root_logging(level: str = "INFO") -> None:
    from .context_logging import LevelAwareFormatter
    level_value = getattr(logging, str(level).upper(), logging.INFO)
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(LevelAwareFormatter())
        root.addHandler(handler)
    else:
        for handler in root.handlers:
            handler.setFormatter(LevelAwareFormatter())
    root.setLevel(level_value)


async def discover_models(settings: Settings) -> list[str]:
    from .ollama_gateway import OllamaGateway

    gateway = OllamaGateway(settings)
    return await gateway.list_models()


def choose_model(default_model: str, models: list[str]) -> str:
    if not sys.stdin.isatty():
        return default_model
    if not models:
        return default_model

    print("\nAvailable models:")
    for i, name in enumerate(models, 1):
        marker = " (default)" if name == default_model else ""
        print(f"  {i}. {name}{marker}")

    print(f"\nEnter model number or press Enter to use [{default_model}]: ", end="", flush=True)
    choice = input().strip()
    if not choice:
        return default_model
    if choice.isdigit() and 1 <= int(choice) <= len(models):
        return models[int(choice) - 1]

    logging.warning("Invalid model selection: %s. Keeping %s", choice, default_model)
    return default_model


def run() -> None:
    configure_root_logging()
    try:
        settings = config.get_settings()
    except SettingsError as exc:
        logging.error("Settings validation failed: %s", exc)
        return
    configure_root_logging(settings.logging.level)

    try:
        models = asyncio.run(discover_models(settings))
    except OllamaTransportError as exc:
        logging.warning("Could not discover Ollama models at %s: %s", settings.ollama.url, exc)
        models = []

    selected = choose_model(settings.chat_model, models)
    settings.set_chat_model(selected)

    runtime = create_runtime(settings)
    set_runtime(runtime)
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logging.info("Bot stopped.")
