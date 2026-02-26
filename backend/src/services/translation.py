"""
Translation service — owns prompt construction, LLM calls, and response parsing.

This is the core business logic layer. Routers call into this service;
this service calls out to the LLM client. Stateless and testable.
"""

import textwrap

from openai import AsyncOpenAI

import config
from utils.language import LanguageCode, LANGUAGES


class TranslationService:
    """Handles text translation via the configured LLM."""

    def __init__(self, client: AsyncOpenAI) -> None:
        self._client = client
        self._model = config.LLM_MODEL

    def _build_prompt(
        self,
        source_code: LanguageCode,
        target_code: LanguageCode,
    ) -> str:
        """Build the translation prompt for the LLM."""
        source_lang = LANGUAGES.get(source_code, str(source_code))
        target_lang = LANGUAGES.get(target_code, str(target_code))

        return textwrap.dedent(f"""\
        You are a professional {source_lang} ({source_code}) to {target_lang} ({target_code}) translator. Your goal is to accurately convey the meaning and nuances of the original {source_lang} text while adhering to {target_lang} grammar, vocabulary, and cultural sensitivities.
        Produce only the {target_lang} translation, without any additional explanations or commentary. Please translate the following {source_lang} text into {target_lang}:

        \
        """)

    async def translate_texts(
        self,
        texts: list[str],
        source_code: LanguageCode,
        target_code: LanguageCode,
    ) -> list[str]:
        """
        Translate a list of texts from source to target language.

        TODO: Batch inference — currently sequential. See roadmap Phase 3.
        """
        prompt = self._build_prompt(source_code, target_code)

        responses = [
            await self._client.responses.create(
                model=self._model,
                input=prompt + text,
            )
            for text in texts
        ]

        return [r.output_text for r in responses]
