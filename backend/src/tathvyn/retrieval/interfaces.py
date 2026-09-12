"""Abstract Interfaces for Information Retrieval Subsystems."""

from abc import ABC, abstractmethod

from pydantic import BaseModel


class SearchResultItem(BaseModel):
    """Normalized search candidate returned by a SearchProvider."""

    url: str
    title: str
    snippet: str
    provider_score: float = 0.0
    published_date: str | None = None


class SearchResponse(BaseModel):
    """Normalized response payload from a SearchProvider."""

    query: str
    provider_name: str
    results: list[SearchResultItem]
    latency_ms: int
    raw_results_count: int


class FetchedContent(BaseModel):
    """Extracted text and metadata from a downloaded web document."""

    url: str
    canonical_url: str
    title: str | None = None
    author: str | None = None
    published_at: str | None = None
    main_text: str
    content_hash: str
    http_status: int = 200


class SearchProvider(ABC):
    """Abstract Base Class for search engines and web discovery providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identifier of the search provider (e.g. 'tavily', 'brave')."""
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        max_results: int = 5,
        domain_filter: list[str] | None = None,
    ) -> SearchResponse:
        """Execute a search query asynchronously and return normalized results."""
        pass


class DocumentFetcher(ABC):
    """Abstract Base Class for downloading and parsing web documents with SSRF security."""

    @abstractmethod
    async def fetch(self, url: str) -> FetchedContent:
        """Download, validate, and parse main text from a target URL."""
        pass
