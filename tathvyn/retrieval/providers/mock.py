"""Deterministic Mock Search Provider and Document Fetcher for Testing."""

import hashlib

from tathvyn.retrieval.interfaces import (
    DocumentFetcher,
    FetchedContent,
    SearchProvider,
    SearchResponse,
    SearchResultItem,
)


class MockSearchProvider(SearchProvider):
    """Deterministic in-memory search provider returning pre-configured or generated responses."""

    def __init__(self, predefined_results: dict[str, list[SearchResultItem]] | None = None) -> None:
        self.predefined_results = predefined_results or {}

    @property
    def provider_name(self) -> str:
        return "mock_search"

    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        results = self.predefined_results.get(
            query,
            [
                SearchResultItem(
                    url=f"https://example.org/article/{i}",
                    title=f"Authoritative Report {i} regarding {query}",
                    snippet=f"Official publication confirming that {query}",
                    provider_score=0.95 - (i * 0.1),
                    published_date="2024-05-31",
                )
                for i in range(1, max_results + 1)
            ],
        )

        return SearchResponse(
            query=query,
            provider_name=self.provider_name,
            results=results[:max_results],
            latency_ms=45,
            raw_results_count=len(results),
        )


class MockDocumentFetcher(DocumentFetcher):
    """Deterministic document fetcher returning synthetic or tailored parsed page content."""

    def __init__(
        self,
        custom_content_by_url: dict[str, str] | None = None,
        default_template: str | None = None,
    ) -> None:
        self.custom_content_by_url = custom_content_by_url or {}
        self.default_template = default_template

    async def fetch(self, url: str) -> FetchedContent:
        if url in self.custom_content_by_url:
            text = self.custom_content_by_url[url]
        elif self.default_template:
            text = self.default_template
        else:
            text = f"Full extracted text content downloaded from mock URL: {url}. Official report and telemetry records."

        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return FetchedContent(
            url=url,
            canonical_url=url.split("?")[0],
            title="NASA & Space Observatory Official Report",
            author="Science Editorial Board",
            published_at="2024-05-31T00:00:00Z",
            main_text=text,
            content_hash=content_hash,
            http_status=200,
        )
