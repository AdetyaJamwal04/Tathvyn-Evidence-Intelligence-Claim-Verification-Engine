"""BGE Cross-Encoder Passage Relevance Reranker.

Wraps sentence-transformers CrossEncoder (BAAI/bge-reranker-v2-m3) to compute
fine-grained relevance scores for (query, passage) pairs.
"""

import math
from typing import Any

from tathvyn.common.config import get_settings
from tathvyn.common.logging import get_logger
from tathvyn.models.interfaces import RerankedPassageItem, RerankerModel

logger = get_logger("reranker_model")

_CROSS_ENCODER_MODEL: Any = None
_RERANKER_LOAD_FAILED: bool = False


def _to_prob(val: float) -> float:
    """Safely bound cross-encoder output to [0.0, 1.0] using sigmoid if unbounded."""
    if 0.0 <= val <= 1.0:
        return val
    # Sigmoid normalization for raw logits
    try:
        if val >= 0:
            z = math.exp(-val)
            prob = 1.0 / (1.0 + z)
        else:
            z = math.exp(val)
            prob = z / (1.0 + z)
        return max(0.0, min(1.0, round(prob, 4)))
    except OverflowError:
        return 1.0 if val > 0 else 0.0


class BGERerankerModel(RerankerModel):
    """Passage relevance reranker using BAAI/bge-reranker-v2-m3."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.reranker_model_name
        self.device = device or settings.device

    def _get_model(self) -> Any:
        """Lazy load cross encoder model with fast local check."""
        global _CROSS_ENCODER_MODEL, _RERANKER_LOAD_FAILED
        if _RERANKER_LOAD_FAILED:
            return None

        if _CROSS_ENCODER_MODEL is None:
            try:
                from sentence_transformers import CrossEncoder

                logger.info(
                    "Loading CrossEncoder reranker", model=self.model_name, device=self.device
                )
                try:
                    _CROSS_ENCODER_MODEL = CrossEncoder(
                        self.model_name, device=self.device, local_files_only=True
                    )
                except Exception:
                    _CROSS_ENCODER_MODEL = CrossEncoder(self.model_name, device=self.device)
            except Exception as e:
                logger.warning(
                    "CrossEncoder not available locally, using fast lexical BM25 fallback",
                    error=str(e),
                )
                _RERANKER_LOAD_FAILED = True
                return None
        return _CROSS_ENCODER_MODEL

    async def rerank(
        self,
        query: str,
        passages: list[tuple[str, str]],  # (passage_id, passage_text)
        top_k: int = 5,
    ) -> list[RerankedPassageItem]:
        """Score (query, passage) pairs and return top_k ranked passages."""
        if not passages:
            return []

        model = self._get_model()
        if model is not None:
            import asyncio

            pairs = [[query, text] for _, text in passages]
            try:
                scores = await asyncio.to_thread(model.predict, pairs)
                scores_list = scores.tolist() if hasattr(scores, "tolist") else list(scores)
                raw_scored = [
                    (pid, text, _to_prob(float(score)))
                    for (pid, text), score in zip(passages, scores_list)
                ]
                raw_scored.sort(key=lambda item: item[2], reverse=True)
                return [
                    RerankedPassageItem(
                        passage_id=pid,
                        text=text,
                        relevance_score=score,
                        rank=idx + 1,
                    )
                    for idx, (pid, text, score) in enumerate(raw_scored[:top_k])
                ]
            except Exception as e:
                logger.warning("Reranking inference error, falling back to lexical", error=str(e))

        # Fast lexical term-overlap fallback
        q_tokens = set(query.lower().split())
        scored_lexical = []
        for pid, text in passages:
            p_tokens = set(text.lower().split())
            overlap = len(q_tokens & p_tokens) / max(len(q_tokens), 1)
            scored_lexical.append((pid, text, round(overlap, 4)))
        scored_lexical.sort(key=lambda x: x[2], reverse=True)
        return [
            RerankedPassageItem(
                passage_id=pid,
                text=text,
                relevance_score=score,
                rank=idx + 1,
            )
            for idx, (pid, text, score) in enumerate(scored_lexical[:top_k])
        ]
