# Usage Guide

## Prerequisites

- Python 3.10 or later
- [Ollama](https://ollama.com/download) installed and running
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-chat-bot
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Create the `.env` file

```bash
cp .env.example .env
```

Edit `.env` and set your token:

```
BOT_TOKEN=123456789:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=qwen3:0.6b
OLLAMA_TIMEOUT=120
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `BOT_TOKEN` | Yes | — | Telegram bot token from BotFather |
| `OLLAMA_URL` | No | `http://localhost:11434` | Ollama server address |
| `OLLAMA_MODEL` | No | `qwen3:0.6b` | Model to use (can also be selected at startup) |
| `OLLAMA_TIMEOUT` | No | `120` | Max seconds to wait for LLM response |

---

## Running Ollama

### Start the server

```bash
ollama serve
```

### Pull the default model (first time only)

```bash
ollama pull qwen3:0.6b
```

The model is ~500 MB. Download takes a few minutes.

To use a larger model:

```bash
ollama pull llama3.2:3b
```

---

## Running the bot

```bash
python bot.py
```

On startup the bot will:
1. Connect to Ollama and list available models.
2. Ask you to choose a model (press Enter to use the default).
3. Start Telegram polling.

Example startup output:

```
Available models:
  1. qwen3:0.6b (default)
  2. llama3.2:3b

Enter model number or press Enter to use [qwen3:0.6b]: 
2026-04-14 12:00:00 Bot started: @YourBot | LLM: qwen3:0.6b @ http://localhost:11434
```

To stop the bot, press `Ctrl+C`.

---

## Using the bot in Telegram

| Action | Bot response |
|---|---|
| `/start` | Welcome message |
| Any text | LLM-generated answer (or provocation if LLM is uncertain) |
| Photo, voice, file | Ignored (no response) |

The bot always responds in the same language as the user's question.

---

## Troubleshooting

### `BOT_TOKEN is not set`

The `.env` file is missing or `BOT_TOKEN` line is absent. Check the file exists in the project root and contains `BOT_TOKEN=<your token>`.

### Bot replies with an error phrase

Ollama is unreachable. Verify:

```bash
ollama serve          # start if not running
ollama list           # confirm the model is pulled
```

### Bot does not respond to messages

Another bot instance with the same token may already be running. Only one polling instance per token is allowed. Stop the duplicate process.

### Responses are slow

Increase `OLLAMA_TIMEOUT` in `.env` or switch to a smaller model at startup.

### Python version error

```bash
python --version   # must be 3.10 or later
```
