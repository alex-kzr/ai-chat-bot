from __future__ import annotations

import logging
from dataclasses import dataclass

from .core import run_agent

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AgentOrchestrator:
    fallback_message: str = "Не удалось завершить обработку запроса. Попробуйте переформулировать запрос."

    async def run_task(self, task: str) -> str:
        result = await run_agent(task)
        if result.final_answer:
            return result.final_answer
        logger.warning("Agent stopped without final answer. reason=%s", result.stopped_reason)
        return self.fallback_message
