import base64
import io

import pytesseract
from PIL import Image

import config

# Map common ISO 639-1 codes to Tesseract language codes
_LANG_MAP: dict[str, str] = {
    "en": "eng",
    "es": "spa",
    "fr": "fra",
    "de": "deu",
    "it": "ita",
    "pt": "por",
    "nl": "nld",
    "ru": "rus",
    "zh": "chi_sim",
    "ja": "jpn",
    "ko": "kor",
    "ar": "ara",
    "hi": "hin",
    "tr": "tur",
    "pl": "pol",
    "uk": "ukr",
    "vi": "vie",
    "th": "tha",
    "sv": "swe",
    "da": "dan",
    "fi": "fin",
    "no": "nor",
    "cs": "ces",
    "ro": "ron",
    "hu": "hun",
    "el": "ell",
    "he": "heb",
    "id": "ind",
}


def extract_text_ocr(image_bytes: bytes, lang: str = "en") -> str:
    """
    Runs Tesseract OCR on raw image bytes.
    Returns extracted text string.
    """
    if config.TESSERACT_CMD:
        pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

    tess_lang = _LANG_MAP.get(lang, "eng")

    img = Image.open(io.BytesIO(image_bytes))
    text: str = pytesseract.image_to_string(img, lang=tess_lang)
    return text.strip()


def extract_text_ocr_from_data_uri(data_uri: str, lang: str = "en") -> str:
    """
    Convenience wrapper: accepts a data URI (data:image/...;base64,...),
    decodes it, and runs OCR.
    """
    if "base64," in data_uri:
        b64_data = data_uri.split("base64,", 1)[1]
    else:
        b64_data = data_uri

    image_bytes = base64.b64decode(b64_data)
    return extract_text_ocr(image_bytes, lang)
