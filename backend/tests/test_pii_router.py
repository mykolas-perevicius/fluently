"""
Tests for the PII router endpoints (routers/pii).

Uses httpx.AsyncClient with ASGITransport to test FastAPI endpoints.
Mocks the LLM client (Ollama) via FastAPI dependency overrides so no
external services are required.
"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
from httpx import ASGITransport, AsyncClient

from dependencies import State, get_state
from main import app


# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def mock_state():
    """Create a mock State with a fake translation_model (AsyncOpenAI)."""
    mock_client = AsyncMock()
    # The detect_pii function calls client.responses.create(...)
    # We need mock_client.responses.create to return an object with output_text
    mock_response = MagicMock()
    mock_response.output_text = "[]"  # no LLM-detected entities by default
    mock_client.responses.create = AsyncMock(return_value=mock_response)

    state = State(
        translation_model=mock_client,
        lid_model=MagicMock(),  # not used by PII endpoints
        vision_model_available=False,
    )
    return state


@pytest.fixture
def client(mock_state):
    """Provide an httpx AsyncClient that overrides the app's state dependency."""

    def _override_state():
        return mock_state

    app.dependency_overrides[get_state] = _override_state
    yield AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    )
    app.dependency_overrides.clear()


# ── POST /pii/detect ─────────────────────────────────────────────────


class TestPIIDetect:
    async def test_detect_email(self, client: AsyncClient):
        response = await client.post(
            "/pii/detect",
            json={"text": "Contact alice@example.com for details."},
        )
        assert response.status_code == 200
        data = response.json()
        entities = data["entities"]
        email_entities = [e for e in entities if e["type"] == "EMAIL"]
        assert len(email_entities) >= 1
        assert email_entities[0]["value"] == "alice@example.com"
        assert email_entities[0]["source"] == "regex"

    async def test_detect_ssn(self, client: AsyncClient):
        response = await client.post(
            "/pii/detect",
            json={"text": "SSN: 123-45-6789"},
        )
        assert response.status_code == 200
        data = response.json()
        entities = data["entities"]
        ssn_entities = [e for e in entities if e["type"] == "SSN"]
        assert len(ssn_entities) == 1
        assert ssn_entities[0]["value"] == "123-45-6789"

    async def test_detect_multiple_types(self, client: AsyncClient):
        response = await client.post(
            "/pii/detect",
            json={"text": "Email: a@b.com, SSN: 111-22-3333, IP: 10.0.0.1"},
        )
        assert response.status_code == 200
        data = response.json()
        types_found = {e["type"] for e in data["entities"]}
        assert "EMAIL" in types_found
        assert "SSN" in types_found
        assert "IP_ADDRESS" in types_found

    async def test_detect_no_pii(self, client: AsyncClient):
        response = await client.post(
            "/pii/detect",
            json={"text": "This text has no personal information."},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["entities"] == []

    async def test_detect_empty_text_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/pii/detect",
            json={"text": ""},
        )
        assert response.status_code == 422

    async def test_detect_missing_text_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/pii/detect",
            json={},
        )
        assert response.status_code == 422

    async def test_detect_entity_fields(self, client: AsyncClient):
        """Verify all expected fields are present on returned entities."""
        response = await client.post(
            "/pii/detect",
            json={"text": "hello@world.com"},
        )
        assert response.status_code == 200
        entity = response.json()["entities"][0]
        assert "type" in entity
        assert "value" in entity
        assert "start" in entity
        assert "end" in entity
        assert "confidence" in entity
        assert "source" in entity

    async def test_detect_with_llm_results(self, client: AsyncClient, mock_state):
        """When the LLM returns entities, they should appear in the response."""
        import json

        llm_response = MagicMock()
        llm_response.output_text = json.dumps(
            [
                {
                    "type": "PERSON_NAME",
                    "value": "John Smith",
                    "confidence": 0.85,
                }
            ]
        )
        mock_state.translation_model.responses.create = AsyncMock(
            return_value=llm_response
        )

        response = await client.post(
            "/pii/detect",
            json={"text": "Please contact John Smith about the project."},
        )
        assert response.status_code == 200
        data = response.json()
        person_entities = [e for e in data["entities"] if e["type"] == "PERSON_NAME"]
        assert len(person_entities) >= 1
        assert person_entities[0]["value"] == "John Smith"
        assert person_entities[0]["source"] == "llm"


# ── POST /pii/redact ─────────────────────────────────────────────────


class TestPIIRedact:
    async def test_redact_mask_strategy(self, client: AsyncClient):
        response = await client.post(
            "/pii/redact",
            json={
                "text": "Email: alice@example.com",
                "entities": [
                    {
                        "type": "EMAIL",
                        "value": "alice@example.com",
                        "start": 7,
                        "end": 24,
                        "confidence": 0.95,
                        "source": "regex",
                    }
                ],
                "strategy": "mask",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["redacted_text"] == "Email: [EMAIL]"
        assert data["redaction_count"] == 1

    async def test_redact_asterisk_strategy(self, client: AsyncClient):
        response = await client.post(
            "/pii/redact",
            json={
                "text": "SSN: 123-45-6789",
                "entities": [
                    {
                        "type": "SSN",
                        "value": "123-45-6789",
                        "start": 5,
                        "end": 16,
                        "confidence": 0.95,
                        "source": "regex",
                    }
                ],
                "strategy": "asterisk",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["redacted_text"] == "SSN: ***********"

    async def test_redact_synthetic_strategy(self, client: AsyncClient):
        response = await client.post(
            "/pii/redact",
            json={
                "text": "Email: alice@real.com",
                "entities": [
                    {
                        "type": "EMAIL",
                        "value": "alice@real.com",
                        "start": 7,
                        "end": 21,
                        "confidence": 0.95,
                        "source": "regex",
                    }
                ],
                "strategy": "synthetic",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "jane.doe@example.com" in data["redacted_text"]
        assert "alice@real.com" not in data["redacted_text"]

    async def test_redact_multiple_entities(self, client: AsyncClient):
        response = await client.post(
            "/pii/redact",
            json={
                "text": "A a@b.com B 111-22-3333 C",
                "entities": [
                    {
                        "type": "EMAIL",
                        "value": "a@b.com",
                        "start": 2,
                        "end": 9,
                        "confidence": 0.95,
                        "source": "regex",
                    },
                    {
                        "type": "SSN",
                        "value": "111-22-3333",
                        "start": 12,
                        "end": 23,
                        "confidence": 0.95,
                        "source": "regex",
                    },
                ],
                "strategy": "mask",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["redacted_text"] == "A [EMAIL] B [SSN] C"
        assert data["redaction_count"] == 2

    async def test_redact_empty_entities(self, client: AsyncClient):
        response = await client.post(
            "/pii/redact",
            json={
                "text": "No PII here.",
                "entities": [],
                "strategy": "mask",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["redacted_text"] == "No PII here."
        assert data["redaction_count"] == 0

    async def test_redact_empty_text_returns_422(self, client: AsyncClient):
        response = await client.post(
            "/pii/redact",
            json={
                "text": "",
                "entities": [],
                "strategy": "mask",
            },
        )
        assert response.status_code == 422

    async def test_redact_default_strategy_is_mask(self, client: AsyncClient):
        """When strategy is omitted, mask should be the default."""
        response = await client.post(
            "/pii/redact",
            json={
                "text": "Email: a@b.com",
                "entities": [
                    {
                        "type": "EMAIL",
                        "value": "a@b.com",
                        "start": 7,
                        "end": 14,
                        "confidence": 0.95,
                        "source": "regex",
                    }
                ],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["redacted_text"] == "Email: [EMAIL]"
