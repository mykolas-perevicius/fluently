"""
PII redaction strategies.

Applies chosen redaction to detected PII entities:
  - mask:      Replace with type label, e.g. [EMAIL], [PERSON_NAME]
  - asterisk:  Replace with asterisks matching the value's length
  - synthetic: Replace with realistic-looking fake data
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from utils.pii_detector import PIIEntity


class RedactionStrategy(StrEnum):
    MASK = "mask"
    ASTERISK = "asterisk"
    SYNTHETIC = "synthetic"


# Hardcoded synthetic replacements by PII type
_SYNTHETIC_DATA: dict[str, str] = {
    "EMAIL": "jane.doe@example.com",
    "PHONE": "+1 (555) 000-0000",
    "SSN": "000-00-0000",
    "CREDIT_CARD": "4111 1111 1111 1111",
    "IP_ADDRESS": "192.0.2.1",
    "PERSON_NAME": "Jane Doe",
    "ADDRESS": "123 Main St, Anytown, US 00000",
    "ORGANIZATION": "Acme Corp",
    "DATE_OF_BIRTH": "01/01/1990",
    "PASSPORT": "X00000000",
    "DRIVER_LICENSE": "D000-0000-0000",
    "BANK_ACCOUNT": "0000000000",
}


def _replacement(entity: PIIEntity, strategy: RedactionStrategy) -> str:
    if strategy == RedactionStrategy.MASK:
        return f"[{entity.type}]"
    elif strategy == RedactionStrategy.ASTERISK:
        return "*" * len(entity.value)
    else:  # SYNTHETIC
        return _SYNTHETIC_DATA.get(entity.type, f"[{entity.type}]")


def redact_text(
    text: str,
    entities: list[PIIEntity],
    strategy: RedactionStrategy = RedactionStrategy.MASK,
) -> str:
    """Replace PII entities in text using the chosen strategy.

    Entities are processed from end to start to preserve character offsets.
    """
    # Sort by start position descending so replacements don't shift offsets
    sorted_entities = sorted(entities, key=lambda e: e.start, reverse=True)

    result = text
    for entity in sorted_entities:
        replacement = _replacement(entity, strategy)
        result = result[: entity.start] + replacement + result[entity.end :]

    return result
