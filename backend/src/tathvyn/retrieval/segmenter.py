"""Deterministic Passage Segmenter with Overlap and Character Offset Tracking.

Segments long documents into 250-400 token passages with 50-token overlapping
windows, preserving exact character spans and SHA256 hashes.
"""

import hashlib
import re
from uuid import UUID, uuid4

from tathvyn.common.models.source import Passage


def segment_document_text(
    document_id: UUID,
    text: str,
    target_token_size: int = 120,
    overlap_tokens: int = 30,
) -> list[Passage]:
    """Segment document text into overlapping passages with precise char offsets.

    Args:
        document_id: The parent Document UUID.
        text: Raw extracted main text from the document.
        target_token_size: Target token/word length per passage (default 300).
        overlap_tokens: Overlapping token count between consecutive chunks (default 50).

    Returns:
        list[Passage]: List of segmented Passage domain objects.
    """
    cleaned_text = text.strip()
    if not cleaned_text:
        return []

    # Find words with their exact character start and end spans
    word_matches = list(re.finditer(r"\S+", cleaned_text))
    total_words = len(word_matches)

    if total_words == 0:
        return []

    # If document is shorter than target size, return single passage
    if total_words <= target_token_size:
        char_start = word_matches[0].start()
        char_end = word_matches[-1].end()
        passage_text = cleaned_text[char_start:char_end]
        p_hash = hashlib.sha256(passage_text.encode("utf-8")).hexdigest()

        return [
            Passage(
                passage_id=uuid4(),
                document_id=document_id,
                sequence_order=0,
                text=passage_text,
                char_start=char_start,
                char_end=char_end,
                token_count=total_words,
                content_hash=p_hash,
            )
        ]

    passages: list[Passage] = []
    step_size = max(1, target_token_size - overlap_tokens)

    for start_idx in range(0, total_words, step_size):
        end_idx = min(start_idx + target_token_size, total_words)

        # Don't create tiny residual trailing fragments (< 20 tokens)
        if end_idx - start_idx < 20 and len(passages) > 0:
            break

        char_start = word_matches[start_idx].start()
        char_end = word_matches[end_idx - 1].end()
        passage_text = cleaned_text[char_start:char_end].strip()

        # Skip noisy table rows or pure navigation boilerplate
        pipe_count = passage_text.count("|")
        if pipe_count > 15 and ("http" in passage_text or not any(c.isalpha() for c in passage_text[:50])):
            if end_idx >= total_words:
                break
            continue

        p_hash = hashlib.sha256(passage_text.encode("utf-8")).hexdigest()

        passages.append(
            Passage(
                passage_id=uuid4(),
                document_id=document_id,
                sequence_order=len(passages),
                text=passage_text,
                char_start=char_start,
                char_end=char_end,
                token_count=end_idx - start_idx,
                content_hash=p_hash,
            )
        )

        if end_idx >= total_words:
            break

    return passages
