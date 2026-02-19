"""
Language detection service — wraps FastText model for language identification.
"""

from fasttext import FastText

import config
from utils.language import LanguageCode, detect_language


class DetectionService:
    """Wraps FastText language detection with confidence thresholding."""

    def __init__(self, model: FastText) -> None:
        self._model = model
        self._threshold = config.DETECTION_CONFIDENCE_THRESHOLD

    def detect(self, texts: list[str]) -> tuple[LanguageCode, float]:
        """
        Detect the dominant language from a list of texts.

        Returns (language_code, confidence). If confidence is below
        the threshold, returns English as the fallback.
        """
        lang, score = detect_language(self._model, texts)

        if score < self._threshold:
            return LanguageCode.en, score

        return lang, score
