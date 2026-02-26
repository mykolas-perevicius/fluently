import asyncio
import logging
import textwrap
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from openai.types.responses import (
    ResponseInputImageParam,
    ResponseInputTextParam,
)
from pydantic import Base64Bytes, BaseModel, Field, field_validator

import config
from dependencies import DefaultLanguageDep, StateDep
from utils.classifier import TextType, classify_text_type
from utils.format_renderers import render_latex, render_markdown, render_plaintext
from utils.image import ImageProcessor
from utils.language import LANGUAGES, LanguageCode, detect_language
from utils.ocr import extract_text_ocr_from_data_uri
from utils.pdf_layout import DocumentLayout, extract_layout

logger = logging.getLogger("fluently")

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
    description="Extracts and translates text from an image using OCR for printed text or vision model for handwritten text.",
    response_description="The translated text from the image.",
    responses={
        400: {"description": "Unsupported source or target language code."},
        422: {"description": "Invalid image format or encoding."},
        500: {"description": "Internal server error during processing."},
    },
)
async def translate_image(
    body: ImageTranslationRequest, state: StateDep, default_language: DefaultLanguageDep
) -> JSONResponse:
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

    image_data_uri = image_processor.process(body.image)

    # Build the text translation prompt (reused across pipelines)
    def _text_prompt() -> str:
        return textwrap.dedent(
            f"You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. "
            f"Your goal is to accurately convey the meaning and nuances of the original {source_lang} text, ensuring strict fidelity to the original tone (including slang or profanity), while adhering to {target_lang} grammar and vocabulary.\n"
            f"Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:\n"
            "\n\n"
        )

    # If vision model is NOT available, skip classification entirely
    # and always use OCR + 12b pipeline
    if not state.vision_model_available:
        extracted_text = extract_text_ocr_from_data_uri(
            image_data_uri, lang=str(source_code)
        )

        if not extracted_text.strip():
            # OCR found nothing — use 12b vision as last resort
            response = await state.translation_model.responses.create(
                model=config.LLM_MODEL,
                input=[
                    {
                        "role": "user",
                        "content": [
                            ResponseInputTextParam(
                                type="input_text",
                                text=(
                                    f"Read the text in this image and translate it into {target_lang}. "
                                    f"Produce only the {target_lang} translation, no explanations.\n\n\n"
                                ),
                            ),
                            ResponseInputImageParam(
                                type="input_image",
                                detail="auto",
                                image_url=image_data_uri,
                            ),
                        ],
                    }
                ],
            )
            return JSONResponse(
                content=response.output_text,
                headers={
                    "X-Text-Type": TextType.PRINTED.value,
                    "Access-Control-Expose-Headers": "X-Text-Type",
                },
            )

        response = await state.translation_model.responses.create(
            model=config.LLM_MODEL,
            input=_text_prompt() + extracted_text,
            top_p=0.9,
            temperature=0.1,
        )
        return JSONResponse(
            content=response.output_text,
            headers={
                "X-Text-Type": TextType.PRINTED.value,
                "Access-Control-Expose-Headers": "X-Text-Type",
            },
        )

    # ── Full dual-pipeline (vision model available) ────────────────────

    # Step 1: Classify text type (printed vs handwritten)
    text_type = await classify_text_type(image_data_uri, state.translation_model)

    if text_type in (TextType.PRINTED, TextType.MIXED):
        # Printed/Mixed pipeline: Tesseract OCR → 12b text translation
        extracted_text = extract_text_ocr_from_data_uri(
            image_data_uri, lang=str(source_code)
        )

        if not extracted_text.strip():
            # Fallback to vision model if OCR finds nothing
            text_type = TextType.HANDWRITTEN
        else:
            response = await state.translation_model.responses.create(
                model=config.LLM_MODEL,
                input=_text_prompt() + extracted_text,
                top_p=0.9,
                temperature=0.1,
            )

            return JSONResponse(
                content=response.output_text,
                headers={
                    "X-Text-Type": text_type.value,
                    "Access-Control-Expose-Headers": "X-Text-Type",
                },
            )

    # Handwritten pipeline: 27b vision model translates directly
    prompt = (
        f"Please carefully read the handwritten "
        f"{source_lang} text in this image and "
        f"translate it into {target_lang}. "
        f"The text may be hard to read due to "
        f"handwriting style. Do your best. "
        f"Produce only the {target_lang} "
        f"translation, no explanations.\n\n\n"
    )

    response = await state.translation_model.responses.create(
        model=config.LLM_MODEL_VISION,
        input=[
            {
                "role": "user",
                "content": [
                    ResponseInputTextParam(type="input_text", text=prompt),
                    ResponseInputImageParam(
                        type="input_image",
                        detail="auto",
                        image_url=image_data_uri,
                    ),
                ],
            }
        ],
    )

    return JSONResponse(
        content=response.output_text,
        headers={
            "X-Text-Type": TextType.HANDWRITTEN.value,
            "Access-Control-Expose-Headers": "X-Text-Type",
        },
    )


# ── Document translation with formatting ───────────────────────────

MAX_PDF_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PDF_PAGES = 100
BATCH_SIZE = 50


class DocumentTranslationResponse(BaseModel):
    plaintext: str
    markdown: str
    latex: str
    page_count: int
    block_count: int


@router.post(
    "/document",
    summary="Translate PDF Document with Formatting",
    description="Extracts structured layout from a PDF, translates all blocks, and returns the result in three formats.",
    response_model=DocumentTranslationResponse,
    responses={
        400: {"description": "Invalid file type, file too large, or too many pages."},
        500: {"description": "Internal server error during processing."},
    },
)
async def translate_document(
    file: UploadFile = File(...),
    target_language_code: str = Form(...),
    source_language_code: str | None = Form(None),
    state: StateDep = None,
    default_language: DefaultLanguageDep = None,
) -> DocumentTranslationResponse:
    # Validate file type
    if file.content_type != "application/pdf" and not (
        file.filename and file.filename.lower().endswith(".pdf")
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for formatted document translation.",
        )

    # Read and validate size
    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_PDF_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_PDF_SIZE // (1024 * 1024)} MB.",
        )

    # Extract layout
    layout = await asyncio.to_thread(extract_layout, pdf_bytes)

    if layout.page_count > MAX_PDF_PAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Too many pages ({layout.page_count}). Maximum is {MAX_PDF_PAGES}.",
        )

    if not layout.blocks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No extractable text found in the PDF.",
        )

    # Resolve languages
    target_code = LanguageCode(target_language_code)
    target_lang = LANGUAGES.get(target_code)
    if not target_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported target language code: {target_language_code}",
        )

    if source_language_code:
        source_code = LanguageCode(source_language_code)
    else:
        sample_texts = [b.text for b in layout.blocks[:5]]
        source_code = detect_language(state.lid_model, sample_texts, default=default_language)

    source_lang = LANGUAGES.get(LanguageCode(source_code))
    if not source_lang:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported source language code: {source_code}",
        )

    # Build translation prompt (same as existing endpoint)
    prompt = textwrap.dedent(
        f"You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. "
        f"Your goal is to accurately convey the meaning and nuances of the original {source_lang} text, ensuring strict fidelity to the original tone (including slang or profanity), while adhering to {target_lang} grammar and vocabulary.\n"
        f"Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:\n"
        "\n\n"
    )

    # Batch translate all blocks
    block_texts = [b.text for b in layout.blocks]
    translated_texts: list[str] = []

    for batch_start in range(0, len(block_texts), BATCH_SIZE):
        batch = block_texts[batch_start : batch_start + BATCH_SIZE]
        responses = await asyncio.gather(
            *(
                state.translation_model.responses.create(
                    model=config.LLM_MODEL,
                    input=prompt + text,
                    top_p=0.9,
                    temperature=0.1,
                )
                for text in batch
            )
        )
        translated_texts.extend(r.output_text for r in responses)

    # Map translated text back into blocks
    for block, translated in zip(layout.blocks, translated_texts):
        block.text = translated

    # Render all three formats
    plaintext = render_plaintext(layout.blocks)
    markdown = render_markdown(layout.blocks)
    latex = render_latex(layout.blocks)

    return DocumentTranslationResponse(
        plaintext=plaintext,
        markdown=markdown,
        latex=latex,
        page_count=layout.page_count,
        block_count=len(layout.blocks),
    )
