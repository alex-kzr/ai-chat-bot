import logging
import random
import httpx

from . import config
from .prompts import SYSTEM_PROMPT, ERROR_PHRASES


async def ask_llm(user_text: str, history: list[dict] | None = None) -> tuple[str, str]:
    """Returns (llm_raw, bot_reply). llm_raw is what the model said, bot_reply is what gets sent.

    History should already include the current user message as its last entry.
    """
    history = history or []
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
        ] + history,
        "stream": False,
    }

    logging.info(">>> LLM request: %s", payload["messages"])

    try:
        async with httpx.AsyncClient(timeout=config.OLLAMA_TIMEOUT) as client:
            response = await client.post(f"{config.OLLAMA_URL}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            llm_raw = data["message"]["content"].strip()

        return llm_raw, llm_raw
    except Exception as e:
        logging.error("LLM error: %s", e)
        error_phrase = random.choice(ERROR_PHRASES)
        return "[error]", error_phrase
