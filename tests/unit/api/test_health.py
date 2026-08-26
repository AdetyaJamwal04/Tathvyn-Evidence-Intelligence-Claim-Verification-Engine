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
