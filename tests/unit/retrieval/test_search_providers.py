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
