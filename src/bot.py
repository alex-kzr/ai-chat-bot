from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher

from .handlers import router
from .runtime import get_runtime


async def run_bot() -> None:
    runtime = get_runtime()
    bot = Bot(token=runtime.settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    info = await bot.get_me()
    logging.info(
        "Bot started: @%s | LLM: %s @ %s",
        info.username,
        runtime.settings.chat_model,
        runtime.settings.ollama.url,
    )
    await dp.start_polling(bot)


async def main() -> None:
    """Backward-compatible async entry point."""
    await run_bot()
