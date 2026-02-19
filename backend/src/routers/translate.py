import textwrap

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from dependencies import StateDep
from utils.language import detect_language, LANGUAGES, LanguageCode

router = APIRouter(
    prefix="/translate",
    tags=["translate"],
)


class TranslationRequest(BaseModel):
    contents: list[str]
    sourceLanguageCode: LanguageCode | None = Field(None, examples=[None])
    targetLanguageCode: LanguageCode = Field(..., examples=["es", "fr", "de", "zh", "ja"])


@router.post("/")
async def translate(body: TranslationRequest, state: StateDep):
    target_code = body.targetLanguageCode
    target_lang = LANGUAGES.get(target_code)

    detected_lang, pscore = detect_language(state.lid_model, body.contents)

    detected_lang = detected_lang if pscore >= 0.6827 else "en"  # Default to English if confidence is low
    source_code = body.sourceLanguageCode or detected_lang
    source_lang = LANGUAGES.get(LanguageCode(source_code))

    if not source_lang:
        raise HTTPException(status_code=400, detail=f"Unsupported source language code: {source_code}")
    
    if not target_lang:
        raise HTTPException(status_code=400, detail=f"Unsupported target language code: {target_code}")

    # Gemma doesn't use system messages, so we just pass the text as input.
    prompt = textwrap.dedent(f"""\
    You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. Your goal is to accurately convey the meaning and nuances of the original {source_lang} text while adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.
    Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:

    \
    """)

    print(prompt + next(iter(body.contents)))

    responses = [await state.translation_model.responses.create(model="translategemma:12b",
        input=prompt + text) for text in body.contents]

    return list(map(lambda r: r.output_text, responses))
