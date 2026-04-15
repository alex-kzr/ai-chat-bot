import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
OLLAMA_TIMEOUT: int = int(os.getenv("OLLAMA_TIMEOUT", "120"))

# System prompt configuration
SYSTEM_PROMPT: str = os.getenv("SYSTEM_PROMPT", "You are a helpful assistant. Answer clearly and concisely in the user's language.")
SYSTEM_PROMPT_ENABLED: bool = os.getenv("SYSTEM_PROMPT_ENABLED", "true").lower() == "true"

# History size limits
MAX_HISTORY_MESSAGES: int = 20  # Keep last N messages (~10 turns)
# MAX_HISTORY_CHARS: int = 10000  # TODO: char-based strategy (future improvement)

# Summarization config
SUMMARY_THRESHOLD: int = int(os.getenv("SUMMARY_THRESHOLD", "10"))  # Trigger summarization when history exceeds this many messages
SUMMARY_KEEP_RECENT: int = int(os.getenv("SUMMARY_KEEP_RECENT", "4"))  # Keep last N messages untouched after summarization

# Validate summarization config
assert SUMMARY_KEEP_RECENT < SUMMARY_THRESHOLD, "SUMMARY_KEEP_RECENT must be less than SUMMARY_THRESHOLD"

# Context logging configuration
CONTEXT_LOGGING_ENABLED: bool = os.getenv("CONTEXT_LOGGING_ENABLED", "true").lower() == "true"
LOG_DESTINATION: str = os.getenv("LOG_DESTINATION", "console")  # "console" or "file"
LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "logs/context.log")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "human")  # "human" or "json"

# Token counting configuration
TOKEN_COUNT_STRATEGY: str = os.getenv("TOKEN_COUNT_STRATEGY", "heuristic")  # "heuristic" or "tiktoken"
HEURISTIC_TOKEN_RATIO: int = int(os.getenv("HEURISTIC_TOKEN_RATIO", "4"))  # characters per token estimate

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please add it to your .env file.")
