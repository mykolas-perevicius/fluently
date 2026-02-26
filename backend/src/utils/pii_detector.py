"""
PII (Personally Identifiable Information) detection.

Hybrid approach:
  1. Regex patterns for structured PII (high confidence, fast)
  2. LLM (Ollama 12b) for contextual PII (names, addresses, organizations)

Both run in parallel, then results are merged and deduplicated.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass

from openai import AsyncOpenAI

import config


@dataclass
class PIIEntity:
    type: str
    value: str
    start: int
    end: int
    confidence: float
    source: str  # "regex" or "llm"


# ── Regex patterns ──────────────────────────────────────────────────

_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "EMAIL",
        re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    ),
    (
        "PHONE",
        re.compile(
            r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
        ),
    ),
    (
        "SSN",
        re.compile(r"\d{3}-\d{2}-\d{4}"),
    ),
    (
        "CREDIT_CARD",
        re.compile(r"(?:\d{4}[-\s]?){3}\d{4}"),
    ),
    (
        "IP_ADDRESS",
        re.compile(r"(?:\d{1,3}\.){3}\d{1,3}"),
    ),
]


def _detect_regex(text: str) -> list[PIIEntity]:
    """Run regex patterns against text, returning all matches."""
    entities: list[PIIEntity] = []
    for pii_type, pattern in _PATTERNS:
        for match in pattern.finditer(text):
            entities.append(
                PIIEntity(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.95,
                    source="regex",
                )
            )
    return entities


# ── LLM-based detection ────────────────────────────────────────────

_LLM_PROMPT = """\
Analyze the following text and identify all personally identifiable information (PII).
Return ONLY a JSON array of objects. Each object must have:
- "type": one of PERSON_NAME, ADDRESS, ORGANIZATION, DATE_OF_BIRTH, PASSPORT, DRIVER_LICENSE, BANK_ACCOUNT
- "value": the exact text that constitutes PII
- "confidence": a float between 0 and 1

If no PII is found, return an empty array: []

Text to analyze:
"""


async def _detect_llm(text: str, client: AsyncOpenAI) -> list[PIIEntity]:
    """Use the LLM to detect contextual PII (names, addresses, etc.)."""
    # Truncate very long texts to avoid overwhelming the model
    analysis_text = text[:8000] if len(text) > 8000 else text

    try:
        response = await client.responses.create(
            model=config.LLM_MODEL,
            input=_LLM_PROMPT + analysis_text,
            temperature=0.1,
        )

        raw = response.output_text.strip()
        # Extract JSON array from response (handle markdown code blocks)
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        items = json.loads(raw)
        if not isinstance(items, list):
            return []

        entities: list[PIIEntity] = []
        for item in items:
            value = item.get("value", "")
            if not value:
                continue
            # Find the position of this value in the original text
            start = text.find(value)
            if start == -1:
                continue
            entities.append(
                PIIEntity(
                    type=item.get("type", "UNKNOWN"),
                    value=value,
                    start=start,
                    end=start + len(value),
                    confidence=min(float(item.get("confidence", 0.7)), 1.0),
                    source="llm",
                )
            )
        return entities
    except Exception:
        # LLM detection is best-effort; regex still provides baseline
        return []


# ── Public API ──────────────────────────────────────────────────────


def _deduplicate(entities: list[PIIEntity]) -> list[PIIEntity]:
    """Remove overlapping entities, preferring higher confidence."""
    if not entities:
        return []

    # Sort by confidence descending, then by start position
    sorted_entities = sorted(entities, key=lambda e: (-e.confidence, e.start))
    result: list[PIIEntity] = []
    occupied: list[tuple[int, int]] = []

    for entity in sorted_entities:
        # Check if this entity overlaps with any already-accepted entity
        overlaps = any(
            entity.start < occ_end and entity.end > occ_start
            for occ_start, occ_end in occupied
        )
        if not overlaps:
            result.append(entity)
            occupied.append((entity.start, entity.end))

    # Return sorted by position for consistent ordering
    return sorted(result, key=lambda e: e.start)


async def detect_pii(text: str, client: AsyncOpenAI) -> list[PIIEntity]:
    """Detect PII using both regex and LLM in parallel, then deduplicate."""
    regex_task = asyncio.to_thread(_detect_regex, text)
    llm_task = _detect_llm(text, client)

    regex_results, llm_results = await asyncio.gather(regex_task, llm_task)

    all_entities = regex_results + llm_results
    return _deduplicate(all_entities)
