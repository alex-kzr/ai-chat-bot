import asyncio
import logging

from aiogram import Router, F
from aiogram.enums import ChatAction
from aiogram.filters import Command
from aiogram.types import Message

from .llm import ask_llm

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


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user = message.from_user.username or message.from_user.id
    logging.info(">>> %s: %s", user, message.text)
    stop = asyncio.Event()
    typing_task = asyncio.create_task(_keep_typing(message, stop))
    try:
        llm_raw, bot_reply = await ask_llm(message.text)
    finally:
        stop.set()
        typing_task.cancel()
    await message.answer(bot_reply)
    asyncio.create_task(_log_response(llm_raw, bot_reply))


async def _log_response(llm_raw: str, bot_reply: str) -> None:
    if llm_raw == bot_reply:
        logging.info("<<< LLM: %s", llm_raw)
    else:
        logging.info("<<< LLM: %s", llm_raw)
        logging.info("<<< BOT: %s", bot_reply)
