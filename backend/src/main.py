from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI
import fasttext

import config
from dependencies import AppState, State
from routers import translate
from routers import health


@asynccontextmanager
async def main(_app: FastAPI):
    translation_model = AsyncOpenAI(
        base_url=config.LLM_BASE_URL,
        api_key=config.LLM_API_KEY,
    )

    lid_model = fasttext.load_model(config.FASTTEXT_MODEL_PATH)

    yield AppState(
        data=State(
            translation_model=translation_model,
            lid_model=lid_model,
        )
    )

    await translation_model.close()


app = FastAPI(
    title="Fluently API",
    description="A high-performance API for translating text and images between multiple languages using state-of-the-art AI models.",
    version="0.1.0",
    lifespan=main,
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
