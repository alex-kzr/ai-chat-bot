import asyncio
import logging
import random

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from .events import UserCreated
from .runtime import get_runtime
from .prompts import ERROR_PHRASES

router = Router()

WELCOME_MESSAGE = (
    "Привет! Я чат-бот на базе локальной языковой модели.\n\n"
    "Задавай вопросы — постараюсь помочь."
)


async def _keep_typing(message: Message, stop: asyncio.Event) -> None:
    while not stop.is_set():
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(4)


@router.message(Command("start"))
async def handle_start(message: Message) -> None:
    await message.answer(WELCOME_MESSAGE)


@router.message(Command("agent"))
async def handle_agent(message: Message) -> None:
    runtime = get_runtime()
    user, created = runtime.users.get_or_create(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
    )
    user_id = int(user.user_id)
    user_display = user.username or user_id
    if created:
        await runtime.event_bus.publish(UserCreated(user_id=user_id, username=user.username))

    task = message.text.replace("/agent", "", 1).strip()
    if not task:
        await message.answer("Usage: `/agent <task>`\n\nExample: `/agent What is 12*15?`", parse_mode="Markdown")
        return

    max_chars = runtime.settings.security.max_user_input_chars
    if len(task) > max_chars:
        await message.answer(f"Task is too long (max {max_chars} characters).")
        return

    logging.info(">>> %s (agent): %s", user_display, task)

    stop = asyncio.Event()
    typing_task = asyncio.create_task(_keep_typing(message, stop))
    try:
        answer = (await runtime.agent_orchestrator.run_task(task)).strip() or random.choice(ERROR_PHRASES)
        for chunk in _split_message(answer):
            await message.answer(chunk)
    finally:
        stop.set()
        typing_task.cancel()


@router.message(F.text)
async def handle_text(message: Message) -> None:
    runtime = get_runtime()
    user, created = runtime.users.get_or_create(
        telegram_user_id=message.from_user.id,
        username=message.from_user.username,
    )
    user_id = int(user.user_id)
    user_display = user.username or user_id
    if created:
        await runtime.event_bus.publish(UserCreated(user_id=user_id, username=user.username))

    max_chars = runtime.settings.security.max_user_input_chars
    text = message.text.strip()
    if len(text) > max_chars:
        await message.answer(f"Message is too long (max {max_chars} characters).")
        return

    logging.info(">>> %s: %s", user_display, text)

    stop = asyncio.Event()
    typing_task = asyncio.create_task(_keep_typing(message, stop))
    try:
        outcome = await runtime.chat_orchestrator.process_text(user_id, text)
    finally:
        stop.set()
        typing_task.cancel()

    reply = outcome.reply.strip()
    if not reply:
        logging.error("Skipping empty bot reply for user_id=%s; returning fallback phrase", user_id)
        reply = random.choice(ERROR_PHRASES)
    for chunk in _split_message(reply):
        await message.answer(chunk)
    asyncio.create_task(_log_response(outcome.llm_raw, reply))


_TELEGRAM_MAX_LEN = 4096


def _split_message(text: str, limit: int = _TELEGRAM_MAX_LEN) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts: list[str] = []
    while text:
        parts.append(text[:limit])
        text = text[limit:]
    return parts


async def _log_response(llm_raw: str, bot_reply: str) -> None:
    if llm_raw == bot_reply:
        logging.info("<<< LLM: %s", llm_raw)
    else:
        logging.info("<<< LLM: %s", llm_raw)
        logging.info("<<< BOT: %s", bot_reply)
