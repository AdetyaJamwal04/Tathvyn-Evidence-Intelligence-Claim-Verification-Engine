import pytest
from httpx import ASGITransport, AsyncClient

from tathvyn.api.app import create_app


@pytest.mark.asyncio
async def test_health_check_endpoint() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database_connected"] is True
        assert data["redis_connected"] is True
        assert "uptime_seconds" in data

@pytest.mark.asyncio
async def test_openapi_schema_generation() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert data["info"]["title"] == "Tathvyn API"

@pytest.mark.asyncio
async def test_web_dashboard_root_serving() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "Tathvyn" in response.text


@pytest.mark.asyncio
async def test_health_live_and_ready_probes() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Test /health/live
        live_resp = await client.get("/api/v1/health/live")
        assert live_resp.status_code == 200
        live_data = live_resp.json()
        assert live_data["status"] == "live"
        assert "uptime_seconds" in live_data

        # 2. Test /health/ready
        ready_resp = await client.get("/api/v1/health/ready")
        assert ready_resp.status_code == 200
        ready_data = ready_resp.json()
        assert ready_data["status"] in ("ready", "degraded")
        assert "redis" in ready_data
        assert "nli_model" in ready_data
