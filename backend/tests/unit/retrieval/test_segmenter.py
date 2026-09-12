"""Tests for Passage Segmenter and Token Chunking."""

from uuid import uuid4

from tathvyn.retrieval.segmenter import segment_document_text


def test_short_document_single_passage() -> None:
    """Verify short documents produce a single passage with correct offsets."""
    doc_id = uuid4()
    text = "The James Webb Space Telescope operates around the Sun-Earth Lagrange Point 2."
    passages = segment_document_text(doc_id, text, target_token_size=300)

    assert len(passages) == 1
    assert passages[0].document_id == doc_id
    assert passages[0].char_start == 0
    assert passages[0].char_end == len(text)
    assert passages[0].sequence_order == 0
    assert len(passages[0].content_hash) == 64


def test_long_document_overlapping_passages() -> None:
    """Verify long documents are sliced into multiple overlapping passages."""
    doc_id = uuid4()
    words = [f"word{i}" for i in range(500)]
    long_text = " ".join(words)

    passages = segment_document_text(
        doc_id,
        long_text,
        target_token_size=100,
        overlap_tokens=20,
    )

    assert len(passages) > 1
    assert passages[0].sequence_order == 0
    assert passages[1].sequence_order == 1
    # Check that sequence orders are monotonically increasing
    for idx, p in enumerate(passages):
        assert p.sequence_order == idx
        assert p.char_end > p.char_start


def test_empty_text_segmentation() -> None:
    """Verify empty text returns an empty list."""
    assert segment_document_text(uuid4(), "") == []
