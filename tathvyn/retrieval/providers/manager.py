"""Search Provider Manager with Automatic Fallback.

Coordinates multi-provider execution across Tavily, Brave Search, and Mocks.
"""

import asyncio

from tathvyn.common.config import get_settings
from tathvyn.common.exceptions import ProviderError, ProviderRateLimitError
from tathvyn.common.logging import get_logger
from tathvyn.retrieval.interfaces import SearchProvider, SearchResponse, SearchResultItem
from tathvyn.retrieval.providers.brave_provider import BraveSearchProvider
from tathvyn.retrieval.providers.mock import MockSearchProvider
from tathvyn.retrieval.providers.tavily_provider import TavilySearchProvider
from tathvyn.storage.cache import get_cache_manager

logger = get_logger("search_manager")


class SearchProviderManager:
    """Manages search provider selection, caching, retries, and parallel routing."""

    def __init__(self, primary_provider: SearchProvider | None = None) -> None:
        settings = get_settings()
        self.providers: list[SearchProvider] = []
        self.cache_manager = get_cache_manager()

        if primary_provider:
            self.providers.append(primary_provider)
        else:
            # Register Tavily if API key is present
            if settings.tavily_api_key.get_secret_value():
                self.providers.append(TavilySearchProvider())
            # Register Brave if API key is present
            if settings.brave_search_api_key.get_secret_value():
                self.providers.append(BraveSearchProvider())
            # If no live API keys are configured, fallback to MockSearchProvider
            if not self.providers:
                logger.info("No live search API keys configured. Using MockSearchProvider.")
                self.providers.append(MockSearchProvider())

    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        """Execute search with caching and automatic fallback to secondary providers."""
        primary_name = self.providers[0].provider_name if self.providers else "mock"

        # Check Cache
        cached_results = await self.cache_manager.get_cached_search_results(query, primary_name)
        if cached_results is not None:
            logger.info("Search query served from cache", query=query, results_count=len(cached_results))
            return SearchResponse(
                query=query,
                results=cached_results[:max_results],
                raw_results_count=len(cached_results),
                provider_name=f"{primary_name}_cached",
                latency_ms=1,
            )

        for provider in self.providers:
            try:
                logger.info(
                    "Dispatching search query", provider=provider.provider_name, query=query
                )
                response = await provider.search(
                    query, max_results=max_results, domain_filter=domain_filter
                )
                # Store in Cache
                if response.results:
                    await self.cache_manager.set_cached_search_results(
                        query, provider.provider_name, response.results
                    )
                return response
            except (ProviderRateLimitError, ProviderError) as e:
                logger.warning(
                    "Search provider failed, attempting fallback",
                    provider=provider.provider_name,
                    error=str(e),
                )
                continue

        # If all registered providers failed, use MockSearchProvider as safety net
        logger.warning("All configured search providers failed. Using emergency mock response.")
        mock = MockSearchProvider()
        return await mock.search(query, max_results=max_results, domain_filter=domain_filter)

    async def search_parallel(
        self,
        queries: list[str],
        max_results_per_query: int = 5,
        timeout_seconds: float = 8.0,
    ) -> list[SearchResultItem]:
        """Execute multiple search queries concurrently with timeout protection.

        Args:
            queries: List of search query strings.
            max_results_per_query: Max results per query.
            timeout_seconds: Hard timeout for all queries combined.

        Returns:
            list[SearchResultItem]: Aggregated and deduplicated search results across all queries.
        """
        if not queries:
            return []

        tasks = [
            self.search(query=q, max_results=max_results_per_query)
            for q in queries
        ]

        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout_seconds,
            )
        except TimeoutError:
            logger.warning("Parallel search queries timed out", timeout_seconds=timeout_seconds)
            responses = []

        all_results: list[SearchResultItem] = []
        seen_urls: set[str] = set()

        for res in responses:
            if isinstance(res, SearchResponse):
                for item in res.results:
                    if item.url not in seen_urls:
                        seen_urls.add(item.url)
                        all_results.append(item)

        return all_results
