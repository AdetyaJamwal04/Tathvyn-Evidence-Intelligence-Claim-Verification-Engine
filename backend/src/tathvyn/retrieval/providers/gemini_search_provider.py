"""Gemini Google Search Grounding Provider Implementation.

Leverages official Google GenAI with Google Search Grounding for cloud-native,
high-reputation live web evidence retrieval without datacenter IP restrictions.
"""

import time
from typing import Any

from tathvyn.common.config import get_settings
from tathvyn.common.exceptions import ProviderError, ProviderRateLimitError
from tathvyn.common.logging import get_logger
from tathvyn.retrieval.interfaces import SearchProvider, SearchResponse, SearchResultItem

logger = get_logger("gemini_search_provider")


class GeminiSearchProvider(SearchProvider):
    """SearchProvider implementing Google Search Grounding via Gemini."""

    def __init__(self, api_key: str | None = None) -> None:
        settings = get_settings()
        raw_key = (
            api_key if api_key is not None else settings.gemini_api_key.get_secret_value()
        )
        self.api_key = raw_key.strip().strip("'\"").strip() if raw_key else ""
        self.model_name = settings.llm_model_name or "gemini-3.8-flash"
        self._client: Any = None

    @property
    def provider_name(self) -> str:
        return "gemini_google_search"

    def _get_client(self) -> Any:
        if self._client is None:
            if not self.api_key:
                raise ProviderError(
                    self.provider_name, "Gemini API key is not configured.", status_code=500
                )
            try:
                from google import genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                raise ProviderError(
                    self.provider_name, f"Failed to initialize Google GenAI client: {e}", status_code=500
                ) from e
        return self._client

    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        client = self._get_client()
        start_time = time.perf_counter()

        prompt = f"Find factual public news, documents, and web evidence verifying: {query}"
        if domain_filter:
            domains_str = " OR ".join(f"site:{d}" for d in domain_filter)
            prompt = f"{prompt} ({domains_str})"

        try:
            from google.genai import types

            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                    temperature=0.0,
                ),
            )

            items: list[SearchResultItem] = []
            if response.candidates:
                candidate = response.candidates[0]
                meta = getattr(candidate, "grounding_metadata", None)
                if meta and hasattr(meta, "grounding_chunks") and meta.grounding_chunks:
                    for chunk in meta.grounding_chunks[:max_results]:
                        web = getattr(chunk, "web", None)
                        if web and hasattr(web, "uri") and web.uri:
                            items.append(
                                SearchResultItem(
                                    url=web.uri,
                                    title=getattr(web, "title", "Google Search Source"),
                                    snippet=response.text[:300] if response.text else "Grounded search evidence.",
                                    provider_score=0.95,
                                    published_date=None,
                                )
                            )

            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                "Gemini Google search grounding executed successfully",
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

        except Exception as e:
            logger.error("gemini_google_search_failed", error=str(e), query=query)
            raise ProviderError(
                self.provider_name, f"Gemini Google search error: {e}", status_code=502
            ) from e
