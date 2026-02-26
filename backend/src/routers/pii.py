"""PII detection and redaction endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from dependencies import StateDep
from utils.pii_detector import PIIEntity as PIIEntityInternal
from utils.pii_detector import detect_pii
from utils.pii_redactor import RedactionStrategy, redact_text

router = APIRouter(prefix="/pii", tags=["pii"])


# ── Request / Response models ──────────────────────────────────────


class PIIEntityModel(BaseModel):
    type: str
    value: str
    start: int
    end: int
    confidence: float
    source: str


class PIIDetectRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50_000)


class PIIDetectResponse(BaseModel):
    entities: list[PIIEntityModel]


class PIIRedactRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50_000)
    entities: list[PIIEntityModel]
    strategy: RedactionStrategy = RedactionStrategy.MASK


class PIIRedactResponse(BaseModel):
    redacted_text: str
    redaction_count: int


# ── Endpoints ──────────────────────────────────────────────────────


@router.post("/detect", response_model=PIIDetectResponse)
async def detect(body: PIIDetectRequest, state: StateDep) -> PIIDetectResponse:
    """Detect PII in the given text using regex + LLM hybrid approach."""
    entities = await detect_pii(body.text, state.translation_model)
    return PIIDetectResponse(
        entities=[
            PIIEntityModel(
                type=e.type,
                value=e.value,
                start=e.start,
                end=e.end,
                confidence=e.confidence,
                source=e.source,
            )
            for e in entities
        ]
    )


@router.post("/redact", response_model=PIIRedactResponse)
async def redact(body: PIIRedactRequest) -> PIIRedactResponse:
    """Redact specified PII entities from text."""
    internal_entities = [
        PIIEntityInternal(
            type=e.type,
            value=e.value,
            start=e.start,
            end=e.end,
            confidence=e.confidence,
            source=e.source,
        )
        for e in body.entities
    ]
    result = redact_text(body.text, internal_entities, body.strategy)
    return PIIRedactResponse(
        redacted_text=result,
        redaction_count=len(body.entities),
    )
