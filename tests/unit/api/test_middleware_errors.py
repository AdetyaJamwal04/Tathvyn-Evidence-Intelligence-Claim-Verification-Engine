"""Tests for RFC-7807 Problem Details Error Middleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from tathvyn.api.app import create_app


@pytest.mark.asyncio
async def test_unsupported_non_english_claim_returns_422_rfc7807() -> None:
    """Verify non-English claim triggers HTTP 422 RFC-7807 Problem Details response."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "claim": "El telescopio espacial James Webb orbita alrededor del punto de Lagrange L2 del sistema Sol-Tierra.",
            "depth": "FAST",
        }
        response = await client.post("/api/v1/check", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["type"] == "https://Tathvyn.org/errors/unsupported-language"
        assert data["title"] == "Unsupported Language"
        assert data["status"] == 422
        assert data["error_code"] == "UNSUPPORTED_LANGUAGE"
        assert "English claims only" in data["detail"]
        assert data["instance"] == "/api/v1/check"


@pytest.mark.asyncio
async def test_empty_claim_validation_error_returns_422_rfc7807() -> None:
    """Verify structural Pydantic validation error produces standard RFC-7807 JSON."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {
            "claim": "a",  # min_length is 3
            "depth": "FAST",
        }
        response = await client.post("/api/v1/check", json=payload)
        assert response.status_code == 422
        data = response.json()
        assert data["type"] == "https://Tathvyn.org/errors/validation-error"
        assert data["error_code"] == "VALIDATION_ERROR"
        assert len(data["invalid_params"]) >= 1
