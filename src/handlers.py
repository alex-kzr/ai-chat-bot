import asyncio
import logging
import random

from aiogram import F, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from .events import UserCreated
from .prompts import ERROR_PHRASES
from .runtime import get_runtime
from .security.injection_patterns import detect_injection_attempt
from .security.log_sanitizer import sanitize_log_data

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

    if not await runtime.rate_limiter.is_allowed(user_id):
        await message.answer("You're sending requests too quickly. Please slow down.")
        return

    task = message.text.replace("/agent", "", 1).strip()
    if not task:
        await message.answer("Usage: `/agent <task>`\n\nExample: `/agent What is 12*15?`", parse_mode="Markdown")
        return

    max_chars = runtime.settings.security.max_user_input_chars
    if len(task) > max_chars:
        await message.answer(f"Task is too long (max {max_chars} characters).")
        return

    # Check for injection patterns in user input (logged but not blocked)
    injection_matches = detect_injection_attempt(task)
    if injection_matches:
        logging.warning(
            "Injection patterns detected in /agent task from %s: %s",
            user_display,
            injection_matches,
        )

    logging.info(">>> %s (agent): %s", user_display, sanitize_log_data(task))

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

    if not await runtime.rate_limiter.is_allowed(user_id):
        await message.answer("You're sending requests too quickly. Please slow down.")
        return

    max_chars = runtime.settings.security.max_user_input_chars
    text = message.text.strip()
    if len(text) > max_chars:
        await message.answer(f"Message is too long (max {max_chars} characters).")
        return

    # Check for injection patterns in user input (logged but not blocked)
    injection_matches = detect_injection_attempt(text)
    if injection_matches:
        logging.warning(
            "Injection patterns detected in text message from %s: %s",
            user_display,
            injection_matches,
        )

    logging.info(">>> %s: %s", user_display, sanitize_log_data(text))

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
        logging.info("<<< LLM: %s", sanitize_log_data(llm_raw))
    else:
        logging.info("<<< LLM: %s", sanitize_log_data(llm_raw))
        logging.info("<<< BOT: %s", sanitize_log_data(bot_reply))
