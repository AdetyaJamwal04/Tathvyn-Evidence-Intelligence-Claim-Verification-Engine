"""Tests for BGE Dense Vector Embedding Generator."""

import pytest

from tathvyn.models.embedding import BGEEmbeddingModel


@pytest.mark.asyncio
async def test_bge_embedding_model_shape() -> None:
    """Verify BGEEmbeddingModel produces 384-dimensional dense vectors."""
    model = BGEEmbeddingModel()
    assert model.embedding_dimension == 384

    texts = [
        "The James Webb Space Telescope operates around the Sun-Earth L2 point.",
        "Penicillin was discovered by Alexander Fleming in 1928.",
    ]
    embeddings = await model.embed_texts(texts)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384


@pytest.mark.asyncio
async def test_bge_embedding_empty_batch() -> None:
    """Verify empty input batch returns empty list."""
    model = BGEEmbeddingModel()
    assert await model.embed_texts([]) == []
