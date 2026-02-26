import logging
import os
from contextlib import asynccontextmanager

import fasttext
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

import config
from dependencies import AppState, State
from routers import health, pii, translate

logger = logging.getLogger("fluently")


def _get_system_memory_gb() -> float:
    """Return total physical memory in GB."""
    try:
        if hasattr(os, "sysconf"):
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            if pages > 0 and page_size > 0:
                return (pages * page_size) / (1024**3)
    except (ValueError, OSError):
        pass
    # Fallback: assume 8 GB (conservative)
    return 8.0


async def _get_model_size_gb(client: httpx.AsyncClient, base_url: str, model: str) -> float:
    """Query Ollama for a model's file size in GB. Returns 0 if model not found."""
    try:
        resp = await client.post(
            f"{base_url}/api/show",
            json={"model": model},
            timeout=15,
        )
        if resp.status_code != 200:
            return 0.0
        data = resp.json()
        # model_info or details may contain size; modelfile has FROM line
        # The most reliable is the "size" field in the model info
        size_bytes = data.get("size", 0)
        if size_bytes:
            return size_bytes / (1024**3)
        # Fallback: check details.parameter_size (e.g. "27.0B")
        param_size = data.get("details", {}).get("parameter_size", "")
        if param_size:
            # Parse "12.2B" → 12.2, then estimate ~0.5 bytes per param for quantized
            num = float("".join(c for c in param_size if c in "0123456789."))
            return num * 0.5  # rough estimate: Q4 quantized ≈ 0.5 bytes/param → GB
        return 0.0
    except Exception:
        return 0.0


def _can_load_model(model_size_gb: float, system_memory_gb: float) -> bool:
    """Check if system has enough memory to safely load the model.

    Requires at least 1.5x the model size to leave headroom for the OS,
    other models, and the application itself.
    """
    if model_size_gb <= 0:
        return False
    required = model_size_gb * 1.5
    return system_memory_gb >= required


@asynccontextmanager
async def main(_app: FastAPI):
    translation_model = AsyncOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        max_retries=0,
    )

    lid_model = fasttext.load_model(config.FASTTEXT_MODEL_PATH)

    # Preload models into memory and pin them indefinitely (keep_alive=-1)
    ollama_base = config.LLM_BASE_URL.replace("/v1/", "").replace("/v1", "")
    vision_model_available = False

    system_mem = _get_system_memory_gb()
    logger.info(f"System memory: {system_mem:.1f} GB")

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{ollama_base}/api/generate",
            json={"model": config.LLM_MODEL, "keep_alive": -1},
            timeout=120,
        )

        # Check if vision model can fit in memory before loading
        vision_size = await _get_model_size_gb(client, ollama_base, config.LLM_MODEL_VISION)
        logger.info(
            f"Vision model '{config.LLM_MODEL_VISION}': "
            f"{vision_size:.1f} GB (system has {system_mem:.1f} GB)"
        )

        if vision_size > 0 and _can_load_model(vision_size, system_mem):
            try:
                await client.post(
                    f"{ollama_base}/api/generate",
                    json={"model": config.LLM_MODEL_VISION, "keep_alive": -1},
                    timeout=180,
                )
                vision_model_available = True
                logger.info(f"Vision model '{config.LLM_MODEL_VISION}' loaded successfully")
            except Exception:
                logger.warning(
                    f"Vision model '{config.LLM_MODEL_VISION}' failed to load"
                )
        else:
            reason = "not installed" if vision_size <= 0 else f"too large for {system_mem:.1f} GB RAM"
            logger.info(
                f"Skipping vision model '{config.LLM_MODEL_VISION}': {reason}. "
                f"All images will use OCR + 12b pipeline."
            )

    # Track which models we loaded so we can unload them on shutdown
    loaded_models = [config.LLM_MODEL]
    if vision_model_available:
        loaded_models.append(config.LLM_MODEL_VISION)

    yield AppState(
        data=State(
            translation_model=translation_model,
            lid_model=lid_model,
            vision_model_available=vision_model_available,
        )
    )

    # ── Graceful shutdown: unload models from RAM, keep cached on disk ──
    logger.info("Shutting down: unloading models from memory...")
    async with httpx.AsyncClient() as client:
        for model in loaded_models:
            try:
                await client.post(
                    f"{ollama_base}/api/generate",
                    json={"model": model, "keep_alive": 0},
                    timeout=10,
                )
                logger.info(f"  Unloaded '{model}' from memory (cached on disk)")
            except Exception:
                logger.warning(f"  Could not unload '{model}' (Ollama may already be stopped)")

    await translation_model.close()
    logger.info("Shutdown complete.")


tags_metadata = [
    {
        "name": "translate",
        "description": "Operations to translate text and images between supported languages.",
    },
]

app = FastAPI(
    title="Fluently API",
    description="A high-performance API for translating text and images between multiple languages using state-of-the-art AI models.",
    version="0.1.0",
    lifespan=main,
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Text-Type"],
)

app.include_router(health.router)
app.include_router(translate.router)
app.include_router(pii.router)
