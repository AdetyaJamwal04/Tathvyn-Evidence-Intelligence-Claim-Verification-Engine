"""BGE Cross-Encoder Passage Relevance Reranker.

Wraps sentence-transformers CrossEncoder (BAAI/bge-reranker-v2-m3) to compute
fine-grained relevance scores for (query, passage) pairs.
"""

from typing import Any

from tathvyn.common.config import get_settings
from tathvyn.common.logging import get_logger
from tathvyn.models.interfaces import RerankedPassageItem, RerankerModel

logger = get_logger("reranker_model")

_CROSS_ENCODER_MODEL: Any = None


class BGERerankerModel(RerankerModel):
    """Passage relevance reranker using BAAI/bge-reranker-v2-m3."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.reranker_model_name
        self.device = device or settings.device

    def _get_model(self) -> Any:
        """Lazy load cross encoder model."""
        global _CROSS_ENCODER_MODEL
        if _CROSS_ENCODER_MODEL is None:
            try:
                from sentence_transformers import CrossEncoder

                logger.info(
                    "Loading CrossEncoder reranker", model=self.model_name, device=self.device
                )
                _CROSS_ENCODER_MODEL = CrossEncoder(self.model_name, device=self.device)
            except Exception as e:
                logger.warning("CrossEncoder not available locally, using fallback", error=str(e))
                return None
        return _CROSS_ENCODER_MODEL

    async def rerank(
        self,
        query: str,
        passages: list[tuple[str, str]],  # (passage_id, passage_text)
        top_k: int = 5,
    ) -> list[RerankedPassageItem]:
        """Score (query, passage) pairs and return top_k ranked passages.

        Args:
            query: The search query or atomic claim text.
            passages: List of (passage_id, text) tuples.
            top_k: Maximum number of top passages to return.

        Returns:
            list[RerankedPassageItem]: Ranked passages sorted by relevance descending.
        """
        if not passages:
            return []

        model = self._get_model()
        if model is not None:
            import asyncio

            pairs = [[query, p_text] for _, p_text in passages]
            raw_scores = await asyncio.to_thread(
                model.predict, pairs, show_progress_bar=False, batch_size=16
            )

            # Convert numpy/tensor scores to list of floats and sort
            scored_items: list[tuple[str, str, float]] = []
            for idx, (p_id, p_text) in enumerate(passages):
                score = float(raw_scores[idx])
                # Normalize cross-encoder logits via sigmoid if unbounded
                norm_score = (
                    1.0 / (1.0 + 2.718281828459045 ** (-score))
                    if score < 0.0 or score > 1.0
                    else score
                )
                scored_items.append((p_id, p_text, norm_score))

            scored_items.sort(key=lambda item: item[2], reverse=True)

            ranked: list[RerankedPassageItem] = []
            for rank_idx, (p_id, p_text, score) in enumerate(scored_items[:top_k]):
                ranked.append(
                    RerankedPassageItem(
                        passage_id=p_id,
                        text=p_text,
                        relevance_score=round(score, 4),
                        rank=rank_idx + 1,
                    )
                )
            return ranked

        # Deterministic fallback based on lexical term overlap
        query_words = set(query.lower().split())
        fallback_scored: list[tuple[str, str, float]] = []
        for p_id, p_text in passages:
            p_words = set(p_text.lower().split())
            overlap = len(query_words.intersection(p_words))
            rel = min(1.0, 0.4 + (overlap / max(1, len(query_words))) * 0.6)
            fallback_scored.append((p_id, p_text, rel))

        fallback_scored.sort(key=lambda item: item[2], reverse=True)

        return [
            RerankedPassageItem(
                passage_id=p_id,
                text=p_text,
                relevance_score=round(rel, 4),
                rank=idx + 1,
            )
            for idx, (p_id, p_text, rel) in enumerate(fallback_scored[:top_k])
        ]
