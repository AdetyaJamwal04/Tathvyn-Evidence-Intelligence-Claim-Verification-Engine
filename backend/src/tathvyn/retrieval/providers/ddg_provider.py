"""DuckDuckGo Search Provider Implementation as resilient fallback."""

import re
import time
import urllib.parse
from typing import Any

import httpx

from tathvyn.common.exceptions import ProviderError, ProviderRateLimitError
from tathvyn.common.logging import get_logger
from tathvyn.retrieval.interfaces import SearchProvider, SearchResponse, SearchResultItem

logger = get_logger("ddg_provider")

DDG_URL = "https://html.duckduckgo.com/html/"


class DuckDuckGoSearchProvider(SearchProvider):
    """Resilient SearchProvider using live DuckDuckGo web search without API keys."""

    @property
    def provider_name(self) -> str:
        return "duckduckgo"

    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        start_time = time.perf_counter()
        effective_query = query
        if domain_filter:
            domains_str = " OR ".join(f"site:{d}" for d in domain_filter)
            effective_query = f"{query} ({domains_str})"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            try:
                response = await client.post(
                    DDG_URL,
                    data={"q": effective_query},
                    headers=headers,
                )
                if response.status_code == 429:
                    raise ProviderRateLimitError(self.provider_name)
                if response.status_code != 200:
                    raise ProviderError(
                        self.provider_name,
                        f"HTTP {response.status_code}: {response.text[:200]}",
                        status_code=response.status_code,
                    )

                text = response.text
                items: list[SearchResultItem] = []

                # Extract organic search results
                snippets = re.findall(r'class="result__snippet"[^>]*>(.*?)</a>', text, re.DOTALL)
                titles = re.findall(
                    r'class="result__title"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                    text,
                    re.DOTALL,
                )

                for idx, (raw_url, raw_title) in enumerate(titles[:max_results]):
                    clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
                    clean_snippet = ""
                    if idx < len(snippets):
                        clean_snippet = re.sub(r"<[^>]+>", "", snippets[idx]).strip()

                    # Unquote DuckDuckGo redirect URL if present
                    actual_url = raw_url
                    if "/l/?uddg=" in actual_url:
                        try:
                            parsed = urllib.parse.urlparse(actual_url)
                            query_params = urllib.parse.parse_qs(parsed.query)
                            if "uddg" in query_params:
                                actual_url = query_params["uddg"][0]
                        except Exception:
                            pass

                    if actual_url and clean_title:
                        items.append(
                            SearchResultItem(
                                url=actual_url,
                                title=clean_title,
                                snippet=clean_snippet,
                                provider_score=0.85,
                                published_date=None,
                            )
                        )

                latency_ms = int((time.perf_counter() - start_time) * 1000)
                logger.info(
                    "DuckDuckGo search executed successfully",
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
                    self.provider_name, f"Network error during DuckDuckGo search: {e}", status_code=502
                ) from e
