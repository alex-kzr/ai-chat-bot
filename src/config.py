import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# History size limits
MAX_HISTORY_MESSAGES: int = 20  # Keep last N messages (~10 turns)
# MAX_HISTORY_CHARS: int = 10000  # TODO: char-based strategy (future improvement)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please add it to your .env file.")
