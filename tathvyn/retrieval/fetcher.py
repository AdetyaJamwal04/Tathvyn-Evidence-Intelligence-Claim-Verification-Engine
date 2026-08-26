"""
Resilient Async HTTP Document Fetcher with SSRF Defense and Size Limits.

Fetches web documents over HTTP/HTTPS, enforces 10MB payload size limits,
validates SSRF security on every redirect hop, and extracts structured text.
"""

from __future__ import annotations

import asyncio
import hashlib

import httpx

from tathvyn.common.exceptions import DocumentFetchError, SecurityViolationError
from tathvyn.common.logging import get_logger
from tathvyn.retrieval.interfaces import DocumentFetcher, FetchedContent
from tathvyn.retrieval.parsers.html_parser import parse_html_content
from tathvyn.retrieval.parsers.pdf_parser import parse_pdf_content
from tathvyn.retrieval.security import validate_url_security

logger = get_logger("http_fetcher")

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB payload cap
DEFAULT_TIMEOUT_SECONDS = 4.0
MAX_REDIRECTS = 3
USER_AGENT = "VeriFact-VerificationBot/1.0 (+https://github.com/your-org/verifact)"


class HTTPDocumentFetcher(DocumentFetcher):
    """Async HTTP document acquisition engine with SSRF security and size caps."""

    def __init__(
        self,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_size_bytes: int = MAX_DOCUMENT_SIZE_BYTES,
    ) -> None:
        self.timeout = timeout
        self.max_size_bytes = max_size_bytes
        self._cache: dict[str, FetchedContent] = {}

    async def fetch(self, url: str) -> FetchedContent:
        """Download and parse a web document securely.

        Args:
            url: Target URL to fetch.

        Raises:
            SSRFAttemptError: If URL resolves to blocked IP.
            DocumentFetchError: If network error or HTTP error occurs.
            SecurityViolationError: If payload exceeds 10MB limit.

        Returns:
            FetchedContent: Clean extracted text, metadata, and hash.
        """
        # In-memory session deduplication
        if url in self._cache:
            return self._cache[url]

        # 1. Pre-fetch SSRF validation
        validated_url = validate_url_security(url)

        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf,text/plain;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        current_url = validated_url
        redirect_count = 0

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=2.0),
            follow_redirects=False,
            headers=headers,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
        ) as client:
            while redirect_count <= MAX_REDIRECTS:
                try:
                    # Validate URL before every hop
                    validate_url_security(current_url)

                    response = await client.get(current_url)

                    # Check for redirect status codes (301, 302, 303, 307, 308)
                    if response.is_redirect:
                        location = response.headers.get("Location")
                        if not location:
                            raise DocumentFetchError(
                                current_url, "Redirect received without Location header."
                            )

                        # Resolve relative redirect
                        current_url = str(response.url.join(location))
                        redirect_count += 1
                        continue

                    if response.status_code != 200:
                        raise DocumentFetchError(
                            current_url,
                            f"HTTP {response.status_code}: {response.reason_phrase}",
                            status_code=response.status_code,
                        )

                    # Check Content-Length header if present
                    content_length = response.headers.get("Content-Length")
                    if content_length and int(content_length) > self.max_size_bytes:
                        raise SecurityViolationError(
                            f"Document from '{current_url}' exceeds maximum size limit of {self.max_size_bytes} bytes."
                        )

                    content_bytes = response.content
                    if len(content_bytes) > self.max_size_bytes:
                        raise SecurityViolationError(
                            f"Downloaded payload exceeds maximum size limit of {self.max_size_bytes} bytes."
                        )

                    content_type = response.headers.get("Content-Type", "").lower()

                    # 2. Parse content based on MIME type
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
                        # Fallback to direct raw text if main article extraction was empty
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
                    self._cache[url] = result
                    return result

                except httpx.RequestError as e:
                    logger.warning("HTTP request failed", url=current_url, error=str(e))
                    raise DocumentFetchError(current_url, f"Network request error: {e}") from e

            raise DocumentFetchError(url, f"Exceeded maximum allowed redirects ({MAX_REDIRECTS}).")
