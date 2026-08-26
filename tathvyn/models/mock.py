"""Deterministic Mock ML Inferencers for Embeddings, Reranking, and NLI."""

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.models.interfaces import (
    EmbeddingModel,
    NLIModel,
    RerankedPassageItem,
    RerankerModel,
    StanceScoreResult,
)


class MockEmbeddingModel(EmbeddingModel):
    """Deterministic embedding generator producing normalized synthetic vectors."""

    def __init__(self, dimension: int = 384) -> None:
        self._dim = dimension

    @property
    def embedding_dimension(self) -> int:
        return self._dim

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        results: list[list[float]] = []
        for text in texts:
            # Deterministic pseudo-embedding based on string length and character hash
            val = float(len(text) % 100) / 100.0
            vec = [val] * self._dim
            results.append(vec)
        return results


class MockRerankerModel(RerankerModel):
    """Deterministic cross-encoder reranker."""

    async def rerank(
        self,
        query: str,
        passages: list[tuple[str, str]],
        top_k: int = 5,
    ) -> list[RerankedPassageItem]:
        scored: list[RerankedPassageItem] = []
        for idx, (p_id, p_text) in enumerate(passages):
            # Rank score decaying with index
            score = max(0.1, 0.98 - (idx * 0.15))
            scored.append(
                RerankedPassageItem(
                    passage_id=p_id,
                    text=p_text,
                    relevance_score=score,
                    rank=idx + 1,
                )
            )
        return scored[:top_k]


class MockNLIModel(NLIModel):
    """Deterministic NLI stance model."""

    def __init__(
        self, default_relationship: EvidenceRelationship = EvidenceRelationship.SUPPORTS
    ) -> None:
        self.default_relationship = default_relationship

    async def predict_stance(
        self,
        premise: str,
        hypothesis: str,
    ) -> StanceScoreResult:
        if self.default_relationship == EvidenceRelationship.SUPPORTS:
            return StanceScoreResult(
                relationship=EvidenceRelationship.SUPPORTS,
                entailment_prob=0.92,
                contradiction_prob=0.03,
                neutral_prob=0.05,
            )
        elif self.default_relationship == EvidenceRelationship.CONTRADICTS:
            return StanceScoreResult(
                relationship=EvidenceRelationship.CONTRADICTS,
                entailment_prob=0.02,
                contradiction_prob=0.94,
                neutral_prob=0.04,
            )
        else:
            return StanceScoreResult(
                relationship=EvidenceRelationship.NEUTRAL,
                entailment_prob=0.10,
                contradiction_prob=0.10,
                neutral_prob=0.80,
            )
