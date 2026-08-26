"""Tests for Mock Provider Implementations."""

import pytest

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.models.mock import MockEmbeddingModel, MockNLIModel, MockRerankerModel
from tathvyn.retrieval.providers.mock import MockDocumentFetcher, MockSearchProvider


@pytest.mark.asyncio
async def test_mock_search_provider() -> None:
    """Verify MockSearchProvider generates structured search responses."""
    provider = MockSearchProvider()
    response = await provider.search("India GDP growth 2024", max_results=3)

    assert response.provider_name == "mock_search"
    assert len(response.results) == 3
    assert "https://example.org" in response.results[0].url
    assert response.results[0].provider_score > 0.0


@pytest.mark.asyncio
async def test_mock_document_fetcher() -> None:
    """Verify MockDocumentFetcher returns parsed content with hash."""
    fetcher = MockDocumentFetcher()
    doc = await fetcher.fetch("https://example.org/article/1")

    assert doc.http_status == 200
    assert len(doc.content_hash) == 64
    assert "Full extracted text" in doc.main_text


@pytest.mark.asyncio
async def test_mock_embedding_model() -> None:
    """Verify MockEmbeddingModel outputs 384-dimensional dense vectors."""
    model = MockEmbeddingModel(dimension=384)
    assert model.embedding_dimension == 384

    embeddings = await model.embed_texts(["First text", "Second text"])
    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384


@pytest.mark.asyncio
async def test_mock_reranker_model() -> None:
    """Verify MockRerankerModel ranks passage tuples."""
    reranker = MockRerankerModel()
    passages = [
        ("p1", "Passage one text"),
        ("p2", "Passage two text"),
        ("p3", "Passage three text"),
    ]
    ranked = await reranker.rerank("query text", passages, top_k=2)
    assert len(ranked) == 2
    assert ranked[0].rank == 1
    assert ranked[0].relevance_score >= ranked[1].relevance_score


@pytest.mark.asyncio
async def test_mock_nli_model() -> None:
    """Verify MockNLIModel produces structured stance scores."""
    nli = MockNLIModel(default_relationship=EvidenceRelationship.SUPPORTS)
    stance = await nli.predict_stance("Premise text", "Hypothesis claim")

    assert stance.relationship == EvidenceRelationship.SUPPORTS
    assert stance.entailment_prob > 0.90
