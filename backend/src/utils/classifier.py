from enum import StrEnum

from openai import AsyncOpenAI

import config


class TextType(StrEnum):
    PRINTED = "printed"
    HANDWRITTEN = "handwritten"
    MIXED = "mixed"


async def classify_text_type(image_data_uri: str, client: AsyncOpenAI) -> TextType:
    """
    Uses the 12b vision model to classify whether the text in an image
    is printed, handwritten, or mixed. Returns a TextType enum value.
    """
    response = await client.responses.create(
        model=config.LLM_MODEL,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Classify: is the text in this image "
                            "printed, handwritten, or mixed? "
                            "Reply with one word."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": image_data_uri,
                        "detail": "low",
                    },
                ],
            }
        ],
        temperature=0.0,
    )

    result = response.output_text.strip().lower()

    if "handwritten" in result:
        return TextType.HANDWRITTEN
    if "mixed" in result:
        return TextType.MIXED
    return TextType.PRINTED
