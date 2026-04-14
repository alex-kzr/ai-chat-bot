import asyncio
import logging
import httpx
from . import config
from aiogram import Bot, Dispatcher
from .handlers import router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


async def select_model() -> None:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{config.OLLAMA_URL}/api/tags")
            models = [m["name"] for m in response.json().get("models", [])]
    except Exception as e:
        print(f"⚠️  Could not connect to Ollama ({config.OLLAMA_URL}): {e}")
        print(f"⚠️  Using default model: {config.OLLAMA_MODEL}\n")
        return

    print("\nAvailable models:")
    for i, name in enumerate(models, 1):
        marker = " (default)" if name == config.OLLAMA_MODEL else ""
        print(f"  {i}. {name}{marker}")

    print(f"\nEnter model number or press Enter to use [{config.OLLAMA_MODEL}]: ", end="", flush=True)
    choice = input().strip()

    if choice == "":
        return

    if choice.isdigit() and 1 <= int(choice) <= len(models):
        config.OLLAMA_MODEL = models[int(choice) - 1]
    else:
        print(f"⚠️  Invalid choice. Using: {config.OLLAMA_MODEL}\n")


async def main() -> None:
    await select_model()
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    info = await bot.get_me()
    logging.info("Bot started: @%s | LLM: %s @ %s", info.username, config.OLLAMA_MODEL, config.OLLAMA_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
