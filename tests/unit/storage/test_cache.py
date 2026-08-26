"""Unit Tests for Multi-Tier Cache Subsystem."""

import pytest

from tathvyn.retrieval.interfaces import SearchResultItem
from tathvyn.storage.cache import CacheManager


@pytest.mark.asyncio
async def test_cache_manager_basic_get_set() -> None:
    cache = CacheManager(use_redis=False)
    cache.clear_memory_cache()

    # Initial get should be None
    assert await cache.get("test", "nonexistent_key") is None

    # Set value
    await cache.set("test", "my_key", {"status": "ok", "value": 42}, ttl_seconds=60)

    # Get cached value
    val = await cache.get("test", "my_key")
    assert val is not None
    assert val["status"] == "ok"
    assert val["value"] == 42


@pytest.mark.asyncio
async def test_verdict_caching() -> None:
    cache = CacheManager(use_redis=False)
    claim = "The Eiffel Tower was completed in 1889."
    verdict_data = {
        "claim": claim,
        "verdict": "SUPPORTED",
        "confidence": 0.95,
    }

    assert await cache.get_cached_verdict(claim) is None

    await cache.set_cached_verdict(claim, verdict_data, ttl_seconds=3600)
    cached = await cache.get_cached_verdict(claim)
    assert cached is not None
    assert cached["verdict"] == "SUPPORTED"
    assert cached["confidence"] == 0.95


@pytest.mark.asyncio
async def test_search_results_caching() -> None:
    cache = CacheManager(use_redis=False)
    query = "James Webb Space Telescope launch date"
    provider = "tavily"

    results = [
        SearchResultItem(
            url="https://nasa.gov/jwst",
            title="JWST Launch Details",
            snippet="Launched December 2021",
            provider_score=0.98,
        )
    ]

    assert await cache.get_cached_search_results(query, provider) is None

    await cache.set_cached_search_results(query, provider, results, ttl_seconds=1800)
    cached_results = await cache.get_cached_search_results(query, provider)

    assert cached_results is not None
    assert len(cached_results) == 1
    assert cached_results[0].url == "https://nasa.gov/jwst"
    assert cached_results[0].title == "JWST Launch Details"


@pytest.mark.asyncio
async def test_embedding_caching() -> None:
    cache = CacheManager(use_redis=False)
    text = "Sample sentence for embedding."
    embedding = [0.123, -0.456, 0.789]

    assert await cache.get_cached_embedding(text) is None

    await cache.set_cached_embedding(text, embedding)
    cached_emb = await cache.get_cached_embedding(text)

    assert cached_emb is not None
    assert len(cached_emb) == 3
    assert pytest.approx(cached_emb[0]) == 0.123
