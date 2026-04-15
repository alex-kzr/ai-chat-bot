import logging
import random
import httpx

from . import config
from .prompts import ERROR_PHRASES
from .context_logging import extract_context, count_context_tokens, log_context


async def ask_llm(user_text: str, history: list[dict] | None = None) -> tuple[str, str]:
    """Returns (llm_raw, bot_reply). llm_raw is what the model said, bot_reply is what gets sent.

    History should already include the current user message as its last entry.
    """
    history = history or []
    system_messages = []
    if config.SYSTEM_PROMPT_ENABLED and not (history and history[0].get("role") == "system"):
        system_messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]

    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": system_messages + history,
        "stream": False,
    }

    logging.info(">>> LLM request: %s", payload["messages"])

    # Log context using structured context logging infrastructure
    if config.CONTEXT_LOGGING_ENABLED:
        try:
            context_data = extract_context(
                messages=payload["messages"],
                model_name=config.OLLAMA_MODEL,
                user_id=None,  # Not available in current function signature
            )
            # Add token count to context
            token_count = count_context_tokens(payload["messages"])
            context_data["statistics"]["token_count"] = token_count

            log_context(context_data, level="debug")
        except Exception as e:
            # Don't let logging errors break the request flow
            logging.warning("Failed to log context: %s", e)

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
