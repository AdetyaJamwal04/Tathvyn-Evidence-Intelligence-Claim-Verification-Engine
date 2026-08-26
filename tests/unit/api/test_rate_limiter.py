"""Unit Tests for Sliding-Window Rate Limiter and Middleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from tathvyn.api.app import create_app
from tathvyn.api.rate_limiter import RateLimiter


def test_rate_limiter_sliding_window_logic() -> None:
    limiter = RateLimiter()
    limiter.clear()

    client_ip = "192.168.1.100"

    # Allow up to 3 requests per 10-second window
    for _ in range(3):
        allowed, remaining, retry_after = limiter.is_allowed(client_ip, max_requests=3, window_seconds=10)
        assert allowed is True
        assert retry_after == 0

    # 4th request should be rejected
    allowed, remaining, retry_after = limiter.is_allowed(client_ip, max_requests=3, window_seconds=10)
    assert allowed is False
    assert remaining == 0
    assert retry_after > 0


@pytest.mark.asyncio
async def test_rate_limit_middleware_headers_and_429() -> None:
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        # Check health is not rate-limited
        health_resp = await client.get("/api/v1/health")
        assert health_resp.status_code == 200

        # Post /check should have X-RateLimit headers
        resp = await client.post(
            "/api/v1/check",
            json={"claim": "The sky is blue.", "depth": "FAST"},
        )
        assert resp.status_code == 200
        assert "X-RateLimit-Limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers
