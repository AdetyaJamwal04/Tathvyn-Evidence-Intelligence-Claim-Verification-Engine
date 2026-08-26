"""Abstract Interfaces for Machine Learning Models and Inferencers."""

from abc import ABC, abstractmethod

from pydantic import BaseModel

from tathvyn.common.enums import EvidenceRelationship


class StanceScoreResult(BaseModel):
    """Normalized NLI probability distribution and predicted stance."""

    relationship: EvidenceRelationship
    entailment_prob: float
    contradiction_prob: float
    neutral_prob: float


class RerankedPassageItem(BaseModel):
    """Scored passage candidate returned by a Cross-Encoder Reranker."""

    passage_id: str
    text: str
    relevance_score: float
    rank: int


class EmbeddingModel(ABC):
    """Abstract Base Class for dense vector embedding models."""

    @property
    @abstractmethod
    def embedding_dimension(self) -> int:
        """Vector dimensionality (e.g. 384 for bge-small)."""
        pass

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Compute dense vector representations for a batch of strings."""
        pass


class RerankerModel(ABC):
    """Abstract Base Class for Cross-Encoder relevance rerankers."""

    @abstractmethod
    async def rerank(
        self,
        query: str,
        passages: list[tuple[str, str]],  # (passage_id, passage_text)
        top_k: int = 5,
    ) -> list[RerankedPassageItem]:
        """Score (query, passage) pairs and return top_k ranked passages."""
        pass


class NLIModel(ABC):
    """Abstract Base Class for Natural Language Inference (Stance) models."""

    @abstractmethod
    async def predict_stance(
        self,
        premise: str,  # The evidence passage
        hypothesis: str,  # The atomic claim
    ) -> StanceScoreResult:
        """Evaluate logical relationship (entailment, contradiction, neutral)."""
        pass
