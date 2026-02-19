# Fluently Backend

The translation API. Built with FastAPI, powered by TranslateGemma via Ollama (dev) or vLLM (prod).

## Structure

```
backend/
├── src/
│   ├── main.py           # App factory, lifespan, router registration
│   ├── config.py         # Environment-based configuration
│   ├── dependencies.py   # FastAPI dependency injection
│   ├── routers/          # HTTP layer (thin — delegates to services)
│   │   ├── translate.py  # POST /translate/, POST /translate/image
│   │   └── health.py     # GET /health
│   ├── services/         # Business logic (testable, no HTTP concerns)
│   │   ├── translation.py
│   │   └── detection.py
│   └── utils/            # Pure utilities
│       └── language.py   # LanguageCode enum, LANGUAGES map, detect_language()
├── models/
│   └── fasttext/         # FastText LID model (not checked in — download separately)
├── tests/
├── typings/              # Type stubs for untyped libraries
├── pyproject.toml
└── Dockerfile
```

## Setup

```bash
uv sync                                    # install deps
ollama pull translategemma:12b             # get the translation model
# Download lid.176.bin → models/fasttext/  # language detection model
```

## Run

```bash
ollama serve                               # in terminal 1
fastapi dev src/main.py                    # in terminal 2
```

API docs at `http://localhost:8000/docs`.

## Test

```bash
uv run pytest
```

## Configuration

All configuration is via environment variables. See `../.env.example` for the full list.

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_BASE_URL` | `http://localhost:11434/v1/` | LLM API endpoint |
| `LLM_API_KEY` | `ollama` | LLM API key |
| `LLM_MODEL` | `translategemma:12b` | Model name |
| `FASTTEXT_MODEL_PATH` | `models/fasttext/lid.176.bin` | Path to FastText model |
| `DETECTION_CONFIDENCE_THRESHOLD` | `0.6827` | Min confidence for language detection |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins |
