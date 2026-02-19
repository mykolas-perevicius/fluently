"""
Smoke tests for the API.

These tests verify the API is wired up correctly without
requiring the LLM or FastText models to be loaded.
"""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def anyio_backend():
    return "asyncio"


# NOTE: Full integration tests require Ollama + FastText model to be available.
# These are placeholder tests to establish the test structure.
# Uncomment and adapt once the service layer is mockable.

# @pytest.mark.anyio
# async def test_health_endpoint():
#     """Health endpoint should always return 200."""
#     from main import app
#
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as client:
#         response = await client.get("/health")
#         assert response.status_code == 200
#         assert response.json() == {"status": "ok"}


def test_placeholder():
    """Remove this once real tests are added."""
    assert True
