"""
Application configuration via environment variables.

All config is read from the environment at import time.
See .env.example for the full list of supported variables.
"""

import os


# ── LLM / Translation Model ──────────────────────────────────────────
LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1/")
LLM_API_KEY: str = os.getenv("LLM_API_KEY", "ollama")
LLM_MODEL: str = os.getenv("LLM_MODEL", "translategemma:12b")

# ── Language Detection ────────────────────────────────────────────────
FASTTEXT_MODEL_PATH: str = os.getenv("FASTTEXT_MODEL_PATH", "models/fasttext/lid.176.bin")
DETECTION_CONFIDENCE_THRESHOLD: float = float(
    os.getenv("DETECTION_CONFIDENCE_THRESHOLD", "0.6827")
)

# ── Server ────────────────────────────────────────────────────────────
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

# ── CORS ──────────────────────────────────────────────────────────────
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")
