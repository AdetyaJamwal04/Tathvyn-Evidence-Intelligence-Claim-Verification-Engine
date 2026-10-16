"""Resilient Async HTTP Document Fetcher with Modern Browser Headers, Fast Timeouts, and Streaming Size Limits."""

from __future__ import annotations

import hashlib
from collections import OrderedDict

import httpx

from tathvyn.common.exceptions import DocumentFetchError, SecurityViolationError
from tathvyn.common.logging import get_logger
from tathvyn.retrieval.interfaces import DocumentFetcher, FetchedContent
from tathvyn.retrieval.parsers.html_parser import parse_html_content
from tathvyn.retrieval.parsers.pdf_parser import parse_pdf_content
from tathvyn.retrieval.security import validate_url_security

logger = get_logger("http_fetcher")

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB payload cap
DEFAULT_TIMEOUT_SECONDS = 2.5  # Optimized for low latency
MAX_REDIRECTS = 3
MAX_FETCH_CACHE_SIZE = 200

# Modern browser User-Agent and headers to bypass anti-bot blocks and 403 Forbidden errors
BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

BROWSER_HEADERS = {
    "User-Agent": BROWSER_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


class HTTPDocumentFetcher(DocumentFetcher):
    """Async HTTP document acquisition engine with SSRF defense, fast timeouts, and streaming size caps."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_size_bytes: int = MAX_DOCUMENT_SIZE_BYTES,
        max_cache_size: int = MAX_FETCH_CACHE_SIZE,
    ) -> None:
        self.timeout = timeout
        self.max_size_bytes = max_size_bytes
        self.max_cache_size = max_cache_size
        self._cache: OrderedDict[str, FetchedContent] = OrderedDict()

    async def fetch(self, url: str) -> FetchedContent:
        """Download and parse a web document securely with fast timeout."""
        if url in self._cache:
            self._cache.move_to_end(url)
            return self._cache[url]

        validated_url = validate_url_security(url)
        current_url = validated_url
        redirect_count = 0

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=1.5),
            follow_redirects=False,
            headers=BROWSER_HEADERS,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        ) as client:
            while redirect_count <= MAX_REDIRECTS:
                try:
                    validate_url_security(current_url)

                    async with client.stream("GET", current_url) as response:
                        if response.is_redirect:
                            location = response.headers.get("Location")
                            if not location:
                                raise DocumentFetchError(
                                    current_url, "Redirect received without Location header."
                                )
                            current_url = str(response.url.join(location))
                            redirect_count += 1
                            continue

                        if response.status_code != 200:
                            raise DocumentFetchError(
                                current_url,
                                f"HTTP {response.status_code}: {response.reason_phrase}",
                                status_code=response.status_code,
                            )

                        content_length = response.headers.get("Content-Length")
                        if content_length and int(content_length) > self.max_size_bytes:
                            raise SecurityViolationError(
                                f"Document from '{current_url}' exceeds maximum size limit of {self.max_size_bytes} bytes."
                            )

                        chunks = []
                        total_bytes = 0
                        async for chunk in response.aiter_bytes():
                            total_bytes += len(chunk)
                            if total_bytes > self.max_size_bytes:
                                raise SecurityViolationError(
                                    f"Downloaded payload exceeds maximum size limit of {self.max_size_bytes} bytes."
                                )
                            chunks.append(chunk)

                        content_bytes = b"".join(chunks)
                        content_type = response.headers.get("Content-Type", "").lower()

                        if "application/pdf" in content_type or current_url.lower().endswith(".pdf"):
                            parsed_pdf = parse_pdf_content(content_bytes)
                            main_text = parsed_pdf.main_text
                            title = parsed_pdf.title
                            author = parsed_pdf.author
                            published_at = None
                        else:
                            raw_html = content_bytes.decode("utf-8", errors="replace")
                            parsed_html = parse_html_content(raw_html, url=current_url)
                            main_text = parsed_html.main_text
                            title = parsed_html.title
                            author = parsed_html.author
                            published_at = parsed_html.published_date

                        if not main_text.strip():
                            main_text = content_bytes.decode("utf-8", errors="replace")[:10000]

                        content_hash = hashlib.sha256(main_text.encode("utf-8")).hexdigest()

                        result = FetchedContent(
                            url=url,
                            canonical_url=str(response.url),
                            title=title,
                            author=author,
                            published_at=published_at,
                            main_text=main_text,
                            content_hash=content_hash,
                            http_status=response.status_code,
                        )

                        if len(self._cache) >= self.max_cache_size:
                            self._cache.popitem(last=False)
                        self._cache[url] = result
                        return result

                except httpx.RequestError as e:
                    logger.warning("HTTP request failed", url=current_url, error=str(e))
                    raise DocumentFetchError(current_url, f"Network request error: {e}") from e

            raise DocumentFetchError(url, f"Exceeded maximum allowed redirects ({MAX_REDIRECTS}).")
