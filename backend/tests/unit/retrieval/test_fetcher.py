"""Tests for HTTP Document Fetcher with SSRF and Size Limits."""

import pytest

from tathvyn.common.exceptions import SSRFAttemptError
from tathvyn.retrieval.fetcher import HTTPDocumentFetcher


@pytest.mark.asyncio
async def test_fetcher_blocks_ssrf() -> None:
    """Verify HTTPDocumentFetcher aborts before connecting to blocked endpoints."""
    fetcher = HTTPDocumentFetcher()

    with pytest.raises(SSRFAttemptError):
        await fetcher.fetch("http://127.0.0.1:8000/internal")

    with pytest.raises(SSRFAttemptError):
        await fetcher.fetch("http://169.254.169.254/latest/meta-data")


def test_fetcher_init_defaults() -> None:
    """Verify fetcher configuration defaults."""
    fetcher = HTTPDocumentFetcher(timeout=5.0, max_size_bytes=1000)
    assert fetcher.timeout == 5.0
    assert fetcher.max_size_bytes == 1000
