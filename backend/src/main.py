from contextlib import asynccontextmanager

import fasttext
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

import config
from dependencies import AppState, State
from routers import health, translate


@asynccontextmanager
async def main(_app: FastAPI):
    translation_model = AsyncOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
        max_retries=0,
    )

    lid_model = fasttext.load_model(config.FASTTEXT_MODEL_PATH)

    # Preload model into memory and pin it indefinitely (keep_alive=-1)
    ollama_base = config.LLM_BASE_URL.replace("/v1/", "").replace("/v1", "")
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{ollama_base}/api/generate",
            json={"model": config.LLM_MODEL, "keep_alive": -1},
            timeout=120,
        )

    yield AppState(
        data=State(
            translation_model=translation_model,
            lid_model=lid_model,
        )
    )

    await translation_model.close()


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
)

app.include_router(health.router)
app.include_router(translate.router)
