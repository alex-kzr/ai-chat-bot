# AI Chat Bot

A Telegram chatbot that answers questions via a local language model (Ollama).

---

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env   # then fill in BOT_TOKEN
ollama serve
ollama pull qwen3:0.6b
python main.py
```

Full setup and troubleshooting: [docs/usage-guide.md](docs/usage-guide.md)

## Dev checks

```bash
pip install -r requirements-dev.txt
python -m pytest
ruff check src tests
mypy src
```

---

## Documentation

| Document | Description |
|---|---|
| [docs/project-overview.md](docs/project-overview.md) | Goals, stack, key design decisions |
| [docs/architecture.md](docs/architecture.md) | Module map, data flow diagram, concurrency model |
| [docs/domain-model.md](docs/domain-model.md) | Data concepts flowing through the pipeline |
| [docs/algorithms.md](docs/algorithms.md) | Model selection, typing indicator, LLM request/response flow |
| [docs/api.md](docs/api.md) | Telegram Bot API and Ollama REST API integration details |
| [docs/usage-guide.md](docs/usage-guide.md) | Installation, configuration, running, troubleshooting |
| [docs/legacy-warnings.md](docs/legacy-warnings.md) | Known limitations and technical debt |
| [docs/change-request.md](docs/change-request.md) | Recommended improvements |
| [docs/content-dump.md](docs/content-dump.md) | Raw inventory of all source files |

---

## How it works

```
User message
  → Users module (identify; publishes UserCreated on first seen)
  → ChatOrchestrator (publishes MessageReceived / ResponseGenerated)
  → ChatService → OllamaGateway
  → History updates via EventBus subscriptions
```

Chat history is stored **in memory per user** with deterministic trimming and summarization.
