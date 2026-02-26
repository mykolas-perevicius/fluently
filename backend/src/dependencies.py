from dataclasses import dataclass
from typing import Annotated, TypedDict

from fastapi import Depends, Header
from fastapi.requests import HTTPConnection
from fasttext import FastText
from openai import AsyncOpenAI

from utils.language import LanguageCode


@dataclass
class State:
    translation_model: AsyncOpenAI
    lid_model: FastText


class AppState(TypedDict):
    data: State


def get_state(conn: HTTPConnection) -> State:
    return conn.state["data"]


StateDep = Annotated[State, Depends(get_state)]


def get_default_language(
    accept_language: Annotated[
        str | None,
        Header(
            description="RFC 7231 Accept-Language header to determine default source language if not provided in the request body.",
            examples=["en-US,en;q=0.9", "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7"],
        ),
    ] = None,
) -> LanguageCode:
    if accept_language:
        # Split by comma to get languages, then by semicolon to remove quality value
        languages = [lang.split(";")[0].strip() for lang in accept_language.split(",")]
        for lang in languages:
            try:
                return LanguageCode(lang)
            except ValueError:
                continue
    return LanguageCode.en


DefaultLanguageDep = Annotated[LanguageCode, Depends(get_default_language)]
