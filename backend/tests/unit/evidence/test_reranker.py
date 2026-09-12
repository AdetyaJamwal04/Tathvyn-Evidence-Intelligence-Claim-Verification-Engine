"""Tests for BGE Cross-Encoder Passage Reranker."""

import pytest

from tathvyn.models.reranker import BGERerankerModel


@pytest.mark.asyncio
async def test_reranker_ranking_order() -> None:
    """Verify reranker sorts passages by relevance to the query."""
    reranker = BGERerankerModel()
    query = "James Webb Space Telescope L2 orbit"
    passages = [
        ("p1", "Vanilla ice cream is a popular frozen dessert worldwide."),
        ("p2", "The James Webb Space Telescope operates at the Sun-Earth Lagrange Point 2 (L2)."),
        ("p3", "Hubble Space Telescope was launched in 1990 into low Earth orbit."),
    ]

    ranked = await reranker.rerank(query, passages, top_k=2)

    assert len(ranked) == 2
    assert ranked[0].passage_id == "p2"
    assert ranked[0].rank == 1
    assert ranked[0].relevance_score > ranked[1].relevance_score


@pytest.mark.asyncio
async def test_reranker_empty_input() -> None:
    """Verify empty input handling."""
    reranker = BGERerankerModel()
    assert await reranker.rerank("query", []) == []
