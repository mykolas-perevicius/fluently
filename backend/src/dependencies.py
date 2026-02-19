from dataclasses import dataclass
from typing import Annotated, TypedDict
from fasttext import FastText
from fastapi import Depends
from fastapi.requests import HTTPConnection
from openai import AsyncOpenAI


@dataclass
class State:
    translation_model: AsyncOpenAI
    lid_model: FastText


class AppState(TypedDict):
    data: State


def get_state(conn: HTTPConnection) -> State:
    return conn.state["data"]


StateDep = Annotated[State, Depends(get_state)]
