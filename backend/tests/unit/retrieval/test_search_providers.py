"""Tests for Search Provider Manager and Search Providers."""

import pytest

from tathvyn.common.exceptions import ProviderError
from tathvyn.retrieval.providers.brave_provider import BraveSearchProvider
from tathvyn.retrieval.providers.manager import SearchProviderManager
from tathvyn.retrieval.providers.mock import MockSearchProvider
from tathvyn.retrieval.providers.tavily_provider import TavilySearchProvider


@pytest.mark.asyncio
async def test_search_provider_manager_with_mock() -> None:
    """Verify SearchProviderManager executes search and returns normalized results."""
    mock = MockSearchProvider()
    manager = SearchProviderManager(primary_provider=mock)

    response = await manager.search("JWST orbital position L2", max_results=3)
    assert response.provider_name == "mock_search"
    assert len(response.results) == 3
    assert response.latency_ms >= 0


@pytest.mark.asyncio
async def test_missing_api_keys_raise_provider_error() -> None:
    """Verify providers raise ProviderError if initialized without API key."""
    tavily = TavilySearchProvider(api_key="")
    with pytest.raises(ProviderError) as exc_info:
        await tavily.search("query")
    assert "Tavily API key is not configured" in str(exc_info.value)

    brave = BraveSearchProvider(api_key="")
    with pytest.raises(ProviderError) as exc_info:
        await brave.search("query")
    assert "Brave Search API key is not configured" in str(exc_info.value)


@pytest.mark.asyncio
async def test_tavily_provider_sends_hardened_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify TavilySearchProvider sends User-Agent, Accept, and Authorization headers."""
    import httpx

    captured_request = {}

    async def mock_post(self, url: str, **kwargs) -> httpx.Response:
        captured_request["url"] = url
        captured_request["json"] = kwargs.get("json")
        captured_request["headers"] = kwargs.get("headers")
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "url": "https://isro.gov.in/chandrayaan3",
                        "title": "Chandrayaan-3 Mission",
                        "content": "Mission successful",
                        "score": 0.99,
                        "published_date": "2023-08-23",
                    }
                ]
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    provider = TavilySearchProvider(api_key="tvly-mock-test-key")
    res = await provider.search("Chandrayaan-3", max_results=1)

    assert len(res.results) == 1
    assert captured_request["headers"] is not None
    assert captured_request["headers"]["User-Agent"] == "tavily-python"
    assert captured_request["headers"]["X-Client-Source"] == "tavily-python"
    assert captured_request["headers"]["Accept"] == "application/json"
    assert captured_request["headers"]["Authorization"] == "Bearer tvly-mock-test-key"
    assert captured_request["json"]["api_key"] == "tvly-mock-test-key"


@pytest.mark.asyncio
async def test_tavily_provider_handles_html_403(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify TavilySearchProvider detects Cloudflare HTML 403 blocks."""
    import httpx

    async def mock_post(self, url: str, **kwargs) -> httpx.Response:
        return httpx.Response(
            403,
            text="<html><head><title>403 Forbidden</title></head><body><h1>403 Forbidden</h1></body></html>",
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    provider = TavilySearchProvider(api_key="tvly-mock-test-key")
    with pytest.raises(ProviderError) as exc_info:
        await provider.search("query")

    assert "Cloudflare/WAF blocked" in str(exc_info.value)
    assert exc_info.value.status_code == 403


@pytest.mark.asyncio
async def test_manager_refuses_mock_fallback_in_production(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify SearchProviderManager raises ProviderError in production when providers fail."""
    from tathvyn.common.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "environment", "production")

    class FailingProvider(TavilySearchProvider):
        @property
        def provider_name(self) -> str:
            return "failing_tavily"

        async def search(self, query: str, max_results: int = 5, domain_filter: list[str] | None = None):
            raise ProviderError("failing_tavily", "Provider is unavailable", status_code=503)

    manager = SearchProviderManager(primary_provider=FailingProvider(api_key="key"))

    with pytest.raises(ProviderError) as exc_info:
        await manager.search("Chandrayaan-3")

    assert "Refusing mock fallback" in str(exc_info.value) or "All configured search providers failed" in str(exc_info.value)
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_manager_permits_mock_fallback_in_development(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify SearchProviderManager falls back to mock in development mode."""
    from tathvyn.common.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "environment", "development")

    class FailingProvider(TavilySearchProvider):
        @property
        def provider_name(self) -> str:
            return "failing_tavily"

        async def search(self, query: str, max_results: int = 5, domain_filter: list[str] | None = None):
            raise ProviderError("failing_tavily", "Provider is unavailable", status_code=503)

    manager = SearchProviderManager(primary_provider=FailingProvider(api_key="key"))
    res = await manager.search("Chandrayaan-3", max_results=2)

    assert res.provider_name == "mock_search"
    assert len(res.results) == 2
