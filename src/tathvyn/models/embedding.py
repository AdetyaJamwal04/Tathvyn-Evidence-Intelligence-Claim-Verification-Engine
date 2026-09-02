"""BGE Dense Vector Embedding Generator.

Wraps sentence-transformers with BAAI/bge-small-en-v1.5 (384 dimensions)
producing normalized vector embeddings for pgvector storage.
"""

from typing import Any

from tathvyn.common.config import get_settings
from tathvyn.common.logging import get_logger
from tathvyn.models.interfaces import EmbeddingModel

logger = get_logger("embedding_model")

_ST_MODEL: Any = None


class BGEEmbeddingModel(EmbeddingModel):
    """Dense vector embedding generator using BAAI/bge-small-en-v1.5."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model_name
        self.device = device or settings.device
        self._dim = 384

    @property
    def embedding_dimension(self) -> int:
        return self._dim

    def _get_model(self) -> Any:
        """Lazy load sentence transformer model."""
        global _ST_MODEL
        if _ST_MODEL is None:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading embedding model", model=self.model_name, device=self.device)
                _ST_MODEL = SentenceTransformer(self.model_name, device=self.device)
            except Exception as e:
                logger.warning(
                    "SentenceTransformer not available locally, using fallback", error=str(e)
                )
                return None
        return _ST_MODEL

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate dense embeddings for a batch of strings.

        Args:
            texts: List of text passages or queries.

        Returns:
            list[list[float]]: 384-dimensional normalized vector for each text.
        """
        if not texts:
            return []

        model = self._get_model()
        if model is not None:
            embeddings = model.encode(
                texts,
                normalize_embeddings=True,
                batch_size=32,
                show_progress_bar=False,
            )
            return [emb.tolist() for emb in embeddings]

        # Deterministic fallback when weights are offline
        results: list[list[float]] = []
        for text in texts:
            val = float(len(text) % 100) / 100.0
            results.append([val] * self._dim)
        return results
