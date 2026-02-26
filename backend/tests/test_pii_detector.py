"""
Tests for PII detection (utils/pii_detector).

Focuses on the regex-based detection and deduplication logic.
LLM-based detection is tested in the router tests via mocks.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from utils.pii_detector import PIIEntity, _deduplicate, _detect_regex


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


# ── Tests for _detect_regex ───────────────────────────────────────────


class TestDetectRegex:
    # ── Email ─────────────────────────────────────────────────────

    def test_detects_email(self):
        text = "Contact us at hello@example.com for more info."
        entities = _detect_regex(text)
        emails = [e for e in entities if e.type == "EMAIL"]
        assert len(emails) == 1
        assert emails[0].value == "hello@example.com"

    def test_detects_email_with_plus(self):
        text = "Send to user+tag@gmail.com please."
        entities = _detect_regex(text)
        emails = [e for e in entities if e.type == "EMAIL"]
        assert len(emails) == 1
        assert emails[0].value == "user+tag@gmail.com"

    def test_no_email_in_plain_text(self):
        text = "This sentence has no email at all."
        entities = _detect_regex(text)
        emails = [e for e in entities if e.type == "EMAIL"]
        assert len(emails) == 0

    # ── Phone ─────────────────────────────────────────────────────

    def test_detects_us_phone(self):
        text = "Call me at (555) 123-4567."
        entities = _detect_regex(text)
        phones = [e for e in entities if e.type == "PHONE"]
        assert len(phones) >= 1

    def test_detects_international_phone(self):
        text = "His number is +44 20 7946 0958."
        entities = _detect_regex(text)
        phones = [e for e in entities if e.type == "PHONE"]
        assert len(phones) >= 1

    # ── SSN ───────────────────────────────────────────────────────

    def test_detects_ssn(self):
        text = "Her SSN is 123-45-6789."
        entities = _detect_regex(text)
        ssns = [e for e in entities if e.type == "SSN"]
        assert len(ssns) == 1
        assert ssns[0].value == "123-45-6789"

    def test_no_ssn_without_dashes(self):
        text = "The number 123456789 is not formatted as an SSN."
        entities = _detect_regex(text)
        ssns = [e for e in entities if e.type == "SSN"]
        assert len(ssns) == 0

    # ── Credit Card ───────────────────────────────────────────────

    def test_detects_credit_card_with_spaces(self):
        text = "Card: 4111 1111 1111 1111"
        entities = _detect_regex(text)
        cards = [e for e in entities if e.type == "CREDIT_CARD"]
        assert len(cards) == 1

    def test_detects_credit_card_with_dashes(self):
        text = "Card: 4111-1111-1111-1111"
        entities = _detect_regex(text)
        cards = [e for e in entities if e.type == "CREDIT_CARD"]
        assert len(cards) == 1

    # ── IP Address ────────────────────────────────────────────────

    def test_detects_ip_address(self):
        text = "Server at 192.168.1.100 is down."
        entities = _detect_regex(text)
        ips = [e for e in entities if e.type == "IP_ADDRESS"]
        assert len(ips) == 1
        assert ips[0].value == "192.168.1.100"

    def test_no_ip_in_plain_text(self):
        text = "No addresses here."
        entities = _detect_regex(text)
        ips = [e for e in entities if e.type == "IP_ADDRESS"]
        assert len(ips) == 0

    # ── Offsets ───────────────────────────────────────────────────

    def test_offsets_correct(self):
        text = "Email: test@test.com"
        entities = _detect_regex(text)
        emails = [e for e in entities if e.type == "EMAIL"]
        assert len(emails) == 1
        e = emails[0]
        assert text[e.start : e.end] == "test@test.com"

    def test_confidence_is_0_95(self):
        text = "SSN: 111-22-3333"
        entities = _detect_regex(text)
        for e in entities:
            if e.type == "SSN":
                assert e.confidence == 0.95

    def test_source_is_regex(self):
        text = "hello@world.org"
        entities = _detect_regex(text)
        for e in entities:
            assert e.source == "regex"

    # ── Multiple entities ─────────────────────────────────────────

    def test_multiple_entities_in_one_text(self):
        text = "Email: a@b.com, SSN: 111-22-3333, IP: 10.0.0.1"
        entities = _detect_regex(text)
        types_found = {e.type for e in entities}
        assert "EMAIL" in types_found
        assert "SSN" in types_found
        assert "IP_ADDRESS" in types_found

    def test_empty_text(self):
        assert _detect_regex("") == []


# ── Tests for _deduplicate ────────────────────────────────────────────


class TestDeduplicate:
    def test_empty_list(self):
        assert _deduplicate([]) == []

    def test_no_overlaps_passes_through(self):
        entities = [
            _entity("EMAIL", "a@b.com", 0, 7),
            _entity("SSN", "111-22-3333", 20, 31),
        ]
        result = _deduplicate(entities)
        assert len(result) == 2

    def test_overlapping_keeps_higher_confidence(self):
        low = _entity("PHONE", "123-456-7890", 0, 12, confidence=0.7, source="llm")
        high = _entity("SSN", "123-45-6789", 0, 11, confidence=0.95, source="regex")
        result = _deduplicate([low, high])
        assert len(result) == 1
        assert result[0].type == "SSN"
        assert result[0].confidence == 0.95

    def test_identical_entities_deduped(self):
        e1 = _entity("EMAIL", "a@b.com", 5, 12, confidence=0.95)
        e2 = _entity("EMAIL", "a@b.com", 5, 12, confidence=0.90, source="llm")
        result = _deduplicate([e1, e2])
        assert len(result) == 1
        assert result[0].confidence == 0.95

    def test_non_overlapping_same_type_preserved(self):
        e1 = _entity("EMAIL", "a@b.com", 0, 7)
        e2 = _entity("EMAIL", "c@d.com", 20, 27)
        result = _deduplicate([e1, e2])
        assert len(result) == 2

    def test_result_sorted_by_position(self):
        e1 = _entity("SSN", "111-22-3333", 50, 61)
        e2 = _entity("EMAIL", "a@b.com", 10, 17)
        result = _deduplicate([e1, e2])
        assert result[0].start < result[1].start

    def test_partial_overlap_keeps_higher_confidence(self):
        """Entity that starts within another's range is considered overlapping."""
        e1 = _entity("PHONE", "123-456-7890", 0, 12, confidence=0.95)
        e2 = _entity("SSN", "456-78-9012", 4, 15, confidence=0.80)
        result = _deduplicate([e1, e2])
        assert len(result) == 1
        assert result[0].type == "PHONE"

    def test_single_entity(self):
        result = _deduplicate([_entity("EMAIL", "x@y.z", 0, 5)])
        assert len(result) == 1
