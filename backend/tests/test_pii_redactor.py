"""
Tests for PII redaction (utils/pii_redactor).

Covers all three redaction strategies: MASK, ASTERISK, SYNTHETIC.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from utils.pii_detector import PIIEntity
from utils.pii_redactor import RedactionStrategy, _SYNTHETIC_DATA, redact_text


# ── Helpers ───────────────────────────────────────────────────────────


def _entity(
    pii_type: str,
    value: str,
    start: int,
    end: int,
    confidence: float = 0.95,
    source: str = "regex",
) -> PIIEntity:
    return PIIEntity(
        type=pii_type,
        value=value,
        start=start,
        end=end,
        confidence=confidence,
        source=source,
    )


# ── MASK strategy ─────────────────────────────────────────────────────


class TestMaskStrategy:
    def test_email_masked(self):
        text = "Send to alice@example.com today."
        entity = _entity("EMAIL", "alice@example.com", 8, 25)
        result = redact_text(text, [entity], RedactionStrategy.MASK)
        assert result == "Send to [EMAIL] today."

    def test_phone_masked(self):
        text = "Call 555-123-4567 now."
        entity = _entity("PHONE", "555-123-4567", 5, 17)
        result = redact_text(text, [entity], RedactionStrategy.MASK)
        assert result == "Call [PHONE] now."

    def test_ssn_masked(self):
        text = "SSN: 123-45-6789"
        entity = _entity("SSN", "123-45-6789", 5, 16)
        result = redact_text(text, [entity], RedactionStrategy.MASK)
        assert result == "SSN: [SSN]"

    def test_person_name_masked(self):
        text = "Contact John Smith for details."
        entity = _entity("PERSON_NAME", "John Smith", 8, 18)
        result = redact_text(text, [entity], RedactionStrategy.MASK)
        assert result == "Contact [PERSON_NAME] for details."

    def test_default_strategy_is_mask(self):
        text = "Email: a@b.com"
        entity = _entity("EMAIL", "a@b.com", 7, 14)
        result = redact_text(text, [entity])
        assert result == "Email: [EMAIL]"


# ── ASTERISK strategy ─────────────────────────────────────────────────


class TestAsteriskStrategy:
    def test_asterisk_count_matches_value_length(self):
        text = "Email: alice@example.com"
        value = "alice@example.com"
        entity = _entity("EMAIL", value, 7, 24)
        result = redact_text(text, [entity], RedactionStrategy.ASTERISK)
        assert result == f"Email: {'*' * len(value)}"

    def test_short_value(self):
        text = "IP: 1.2.3.4"
        entity = _entity("IP_ADDRESS", "1.2.3.4", 4, 11)
        result = redact_text(text, [entity], RedactionStrategy.ASTERISK)
        assert result == "IP: *******"

    def test_ssn_asterisks(self):
        text = "SSN 123-45-6789 here"
        entity = _entity("SSN", "123-45-6789", 4, 15)
        result = redact_text(text, [entity], RedactionStrategy.ASTERISK)
        # 123-45-6789 is 11 chars
        assert result == "SSN *********** here"


# ── SYNTHETIC strategy ────────────────────────────────────────────────


class TestSyntheticStrategy:
    def test_email_replaced_with_fake(self):
        text = "Email: alice@real.com"
        entity = _entity("EMAIL", "alice@real.com", 7, 21)
        result = redact_text(text, [entity], RedactionStrategy.SYNTHETIC)
        assert _SYNTHETIC_DATA["EMAIL"] in result
        assert "alice@real.com" not in result

    def test_phone_replaced_with_fake(self):
        text = "Call 555-999-8888."
        entity = _entity("PHONE", "555-999-8888", 5, 17)
        result = redact_text(text, [entity], RedactionStrategy.SYNTHETIC)
        assert _SYNTHETIC_DATA["PHONE"] in result

    def test_ssn_replaced_with_fake(self):
        text = "SSN: 123-45-6789"
        entity = _entity("SSN", "123-45-6789", 5, 16)
        result = redact_text(text, [entity], RedactionStrategy.SYNTHETIC)
        assert _SYNTHETIC_DATA["SSN"] in result

    def test_person_name_replaced(self):
        text = "Mr. John Smith is here."
        entity = _entity("PERSON_NAME", "John Smith", 4, 14)
        result = redact_text(text, [entity], RedactionStrategy.SYNTHETIC)
        assert "Jane Doe" in result
        assert "John Smith" not in result

    def test_unknown_type_falls_back_to_mask(self):
        text = "Data: some_weird_pii"
        entity = _entity("UNKNOWN_TYPE", "some_weird_pii", 6, 20)
        result = redact_text(text, [entity], RedactionStrategy.SYNTHETIC)
        assert "[UNKNOWN_TYPE]" in result

    def test_all_known_types_have_synthetic_data(self):
        """Every type in _SYNTHETIC_DATA should produce a replacement."""
        for pii_type, fake_value in _SYNTHETIC_DATA.items():
            text = f"Value: PLACEHOLDER"
            entity = _entity(pii_type, "PLACEHOLDER", 7, 18)
            result = redact_text(text, [entity], RedactionStrategy.SYNTHETIC)
            assert fake_value in result


# ── Multiple entities ─────────────────────────────────────────────────


class TestMultipleEntities:
    def test_two_entities_replaced(self):
        text = "Email: a@b.com, Phone: 555-000-1111"
        entities = [
            _entity("EMAIL", "a@b.com", 7, 14),
            _entity("PHONE", "555-000-1111", 23, 35),
        ]
        result = redact_text(text, entities, RedactionStrategy.MASK)
        assert result == "Email: [EMAIL], Phone: [PHONE]"

    def test_multiple_entities_offsets_dont_break(self):
        """Replacements of different lengths should not corrupt offsets."""
        text = "A 123-45-6789 B alice@x.com C"
        entities = [
            _entity("SSN", "123-45-6789", 2, 13),
            _entity("EMAIL", "alice@x.com", 16, 27),
        ]
        result = redact_text(text, entities, RedactionStrategy.MASK)
        assert "[SSN]" in result
        assert "[EMAIL]" in result
        assert "A [SSN] B [EMAIL] C" == result

    def test_three_entities_all_masked(self):
        text = "SSN: 111-22-3333 IP: 10.0.0.1 Email: x@y.z"
        entities = [
            _entity("SSN", "111-22-3333", 5, 16),
            _entity("IP_ADDRESS", "10.0.0.1", 21, 29),
            _entity("EMAIL", "x@y.z", 37, 42),
        ]
        result = redact_text(text, entities, RedactionStrategy.MASK)
        assert "[SSN]" in result
        assert "[IP_ADDRESS]" in result
        assert "[EMAIL]" in result

    def test_adjacent_entities(self):
        """Entities immediately next to each other."""
        text = "AB"
        entities = [
            _entity("X", "A", 0, 1),
            _entity("Y", "B", 1, 2),
        ]
        result = redact_text(text, entities, RedactionStrategy.MASK)
        assert result == "[X][Y]"


# ── Empty entity list ─────────────────────────────────────────────────


class TestEmptyEntities:
    def test_returns_original_text(self):
        text = "Nothing to redact here."
        result = redact_text(text, [], RedactionStrategy.MASK)
        assert result == text

    def test_returns_original_text_asterisk(self):
        text = "Nothing to redact here."
        result = redact_text(text, [], RedactionStrategy.ASTERISK)
        assert result == text

    def test_returns_original_text_synthetic(self):
        text = "Nothing to redact here."
        result = redact_text(text, [], RedactionStrategy.SYNTHETIC)
        assert result == text


# ── Reverse-sort correctness ─────────────────────────────────────────


class TestReverseSortByStart:
    def test_entities_unsorted_still_works(self):
        """Entities passed in arbitrary order should still produce correct result."""
        text = "A: a@b.com B: 111-22-3333"
        entities = [
            _entity("SSN", "111-22-3333", 14, 25),  # later in text, listed first
            _entity("EMAIL", "a@b.com", 3, 10),  # earlier in text, listed second
        ]
        result = redact_text(text, entities, RedactionStrategy.MASK)
        assert result == "A: [EMAIL] B: [SSN]"

    def test_entities_already_reverse_sorted(self):
        text = "X a@b.com Y 111-22-3333 Z"
        entities = [
            _entity("SSN", "111-22-3333", 12, 23),
            _entity("EMAIL", "a@b.com", 2, 9),
        ]
        result = redact_text(text, entities, RedactionStrategy.MASK)
        assert result == "X [EMAIL] Y [SSN] Z"
