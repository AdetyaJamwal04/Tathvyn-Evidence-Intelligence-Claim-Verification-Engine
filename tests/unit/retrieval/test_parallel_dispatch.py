"""Unit Tests for Parallel Search Provider Dispatch."""

import pytest

from tathvyn.retrieval.interfaces import SearchProvider, SearchResponse, SearchResultItem
from tathvyn.retrieval.providers.manager import SearchProviderManager


class DummySearchProvider(SearchProvider):
    @property
    def provider_name(self) -> str:
        return "dummy"

    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        return SearchResponse(
            query=query,
            results=[
                SearchResultItem(
                    url=f"https://example.com/{query.replace(' ', '_')}",
                    title=f"Result for {query}",
                    snippet=f"Snippet for {query}",
                    provider_score=0.9,
                ),
                SearchResultItem(
                    url="https://example.com/common_shared_source",
                    title="Shared Source",
                    snippet="Duplicate across queries",
                    provider_score=0.85,
                ),
            ],
            raw_results_count=2,
            provider_name="dummy",
            latency_ms=10,
        )


@pytest.mark.asyncio
async def test_search_parallel_deduplication() -> None:
    provider = DummySearchProvider()
    manager = SearchProviderManager(primary_provider=provider)

    queries = [
        "James Webb Space Telescope launch",
        "James Webb Space Telescope orbit altitude",
    ]

    results = await manager.search_parallel(queries, max_results_per_query=5)

    assert len(results) == 3
    urls = [r.url for r in results]
    assert "https://example.com/James_Webb_Space_Telescope_launch" in urls
    assert "https://example.com/James_Webb_Space_Telescope_orbit_altitude" in urls
    assert "https://example.com/common_shared_source" in urls
    # Ensure deduplication of common source
    assert urls.count("https://example.com/common_shared_source") == 1


@pytest.mark.asyncio
async def test_search_parallel_empty_queries() -> None:
    manager = SearchProviderManager(primary_provider=DummySearchProvider())
    results = await manager.search_parallel([])
    assert results == []
