"""Tavily Search API Provider Implementation."""

import time
from typing import Any

import httpx

from tathvyn.common.config import get_settings
from tathvyn.common.exceptions import ProviderError, ProviderRateLimitError
from tathvyn.common.logging import get_logger
from tathvyn.retrieval.interfaces import SearchProvider, SearchResponse, SearchResultItem

logger = get_logger("tavily_provider")

TAVILY_API_URL = "https://api.tavily.com/search"


class TavilySearchProvider(SearchProvider):
    """SearchProvider implementing Tavily search API."""

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        self.api_key = (
            api_key if api_key is not None else settings.tavily_api_key.get_secret_value()
        )

    @property
    def provider_name(self) -> str:
        return "tavily"

    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        if not self.api_key:
            raise ProviderError(
                self.provider_name, "Tavily API key is not configured.", status_code=500
            )

        start_time = time.perf_counter()
        payload: dict[str, Any] = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_domains": domain_filter or [],
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(TAVILY_API_URL, json=payload)
                if response.status_code == 429:
                    raise ProviderRateLimitError(self.provider_name)
                if response.status_code != 200:
                    raise ProviderError(
                        self.provider_name,
                        f"HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )

                data = response.json()
                latency_ms = int((time.perf_counter() - start_time) * 1000)

                items: list[SearchResultItem] = []
                for res in data.get("results", []):
                    items.append(
                        SearchResultItem(
                            url=res.get("url", ""),
                            title=res.get("title", ""),
                            snippet=res.get("content", ""),
                            provider_score=float(res.get("score", 0.0)),
                            published_date=res.get("published_date"),
                        )
                    )

                logger.info(
                    "Tavily search executed successfully",
                    query=query,
                    results_count=len(items),
                    latency_ms=latency_ms,
                )

                return SearchResponse(
                    query=query,
                    provider_name=self.provider_name,
                    results=items,
                    latency_ms=latency_ms,
                    raw_results_count=len(items),
                )

            except httpx.HTTPError as e:
                raise ProviderError(
                    self.provider_name, f"Network error during Tavily search: {e}", status_code=502
                ) from e
