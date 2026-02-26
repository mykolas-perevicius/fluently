import asyncio
import textwrap
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, status
from openai.types.responses import (
    ResponseInputImageParam,
    ResponseInputTextParam,
)
from pydantic import Base64Bytes, BaseModel, Field, field_validator

import config
from dependencies import DefaultLanguageDep, StateDep
from utils.image import ImageProcessor
from utils.language import LANGUAGES, LanguageCode, detect_language

router = APIRouter(
    prefix="/translate",
    tags=["translate"],
)

image_processor = ImageProcessor()


class TranslationRequest(BaseModel):
    type TextInput = Annotated[str, Field(min_length=1, max_length=5000)]

    contents: list[TextInput] = Field(
        ...,
        min_length=1,
        max_length=50,
        title="Contents",
        description="A list of text strings to translate.",
        examples=[["Hello world", "How are you?"]],
    )
    sourceLanguageCode: LanguageCode | None = Field(
        None,
        title="Source Language Code",
        description="The ISO 639-1 language code of the source text. If not provided, it will be automatically detected.",
        examples=[LanguageCode.en],
    )
    targetLanguageCode: LanguageCode = Field(
        ...,
        title="Target Language Code",
        description="The ISO 639-1 language code of the target language.",
        examples=[LanguageCode.es, LanguageCode.fr],
    )


@router.post(
    "/",
    summary="Translate Text",
    description="Translates a list of text strings from a source language to a target language.",
    response_description="A list of translated strings in the target language.",
    responses={
        200: {
            "description": "Successful translation",
            "content": {
                "application/json": {"example": ["Hola mundo", "¿Cómo estás?"]}
            },
        },
        400: {"description": "Unsupported source or target language code."},
        500: {"description": "Internal server error during translation."},
    },
)
async def translate(
    body: TranslationRequest, state: StateDep, default_language: DefaultLanguageDep
) -> list[str]:
    target_code = body.targetLanguageCode
    target_lang = LANGUAGES.get(target_code)

    detected_lang = detect_language(
        state.lid_model,
        body.contents,
        default=default_language,
    )

    source_code = body.sourceLanguageCode or detected_lang
    source_lang = LANGUAGES.get(LanguageCode(source_code))

    if not source_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source language code: {source_code}",
        )

    if not target_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language code: {target_code}",
        )

    # Gemma doesn't use system messages, so we just pass the text as input.
    prompt = textwrap.dedent(
        (
            f"You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. "
            f"Your goal is to accurately convey the meaning and nuances of the original {source_lang} text, ensuring strict fidelity to the original tone (including slang or profanity), while adhering to {target_lang} grammar and vocabulary.\n"
            f"Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:\n"
            "\n\n"
        )
    )

    responses = await asyncio.gather(
        *(
            [
                state.translation_model.responses.create(
                    model=config.LLM_MODEL,
                    input=prompt + text,
                    top_p=0.9,  # Maintain focus on the most relevant translations
                    temperature=0.1,  # Force deterministic output
                )
                for text in body.contents
            ]
        )
    )

    return list(map(lambda r: r.output_text, responses))


class InvalidImageFormatError(ValueError):
    msg = "Invalid image format. Must be a base64 string with a valid header (e.g., data:image/png;base64,...)."


class UnsupportedImageTypeError(ValueError):
    msg = "Unsupported image type. Allowed types are image/jpeg, image/png, image/gif, and image/webp."


class ImageTranslationRequest(BaseModel):
    image: Base64Bytes = Field(
        ...,
        title="Image Data",
        description="Base64 encoded image data containing text to translate. Max size 5MB.",
        examples=[
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        ],
        json_schema_extra={
            "contentEncoding": "base64",
            "anyOf": [
                {"contentMediaType": "image/png"},
                {"contentMediaType": "image/jpeg"},
            ],
        },
    )  # Base64-encoded image data

    @field_validator("image", mode="before")
    def strip_header(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise InvalidImageFormatError()

        if "base64," in v:
            header, data = v.split("base64,", 1)
            allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
            if not any(ctype in header for ctype in allowed_types):
                raise UnsupportedImageTypeError()
            return data

        raise InvalidImageFormatError()

    sourceLanguageCode: LanguageCode | None = Field(
        None,
        title="Source Language Code",
        description="The ISO 639-1 language code of the text in the image. If not provided, it will be automatically detected or default to English.",
        examples=[LanguageCode.en],
    )
    targetLanguageCode: LanguageCode = Field(
        ...,
        title="Target Language Code",
        description="The ISO 639-1 language code to translate the text into.",
        examples=[LanguageCode.es],
    )


@router.post(
    "/image",
    summary="Translate Image Text",
    description="Extracts and translates text from an image.",
    response_description="The translated text from the image.",
    responses={
        400: {"description": "Unsupported source or target language code."},
        422: {"description": "Invalid image format or encoding."},
        500: {"description": "Internal server error during processing."},
    },
)
async def translate_image(
    body: ImageTranslationRequest, state: StateDep, default_language: DefaultLanguageDep
) -> str:
    target_code = body.targetLanguageCode
    target_lang = LANGUAGES.get(target_code)

    source_code = body.sourceLanguageCode or default_language
    source_lang = LANGUAGES.get(LanguageCode(source_code))

    if not source_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source language code: {source_code}",
        )

    if not target_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language code: {target_code}",
        )

    prompt = (
        f"Please translate the {source_lang} text in the provided image into {target_lang}. "
        f"Produce only the {target_lang} translation, without any additional explanations, "
        "alternatives or commentary. Focus only on the text, do not output where the text is located, "
        "surrounding objects or any other explanation about the picture. Ignore symbols, pictogram, and "
        "arrows!\n\n\n"
    )

    response = await state.translation_model.responses.create(
        model=config.LLM_MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    ResponseInputTextParam(type="input_text", text=prompt),
                    ResponseInputImageParam(
                        type="input_image",
                        detail="auto",
                        image_url=image_processor.process(body.image),
                    ),
                ],
            }
        ],
    )

    return response.output_text
