"""DeBERTa-v3 Natural Language Inference (NLI) Stance Classifier.

Evaluates empirical and logical stance between an evidence passage (premise)
and an atomic claim proposition (hypothesis), outputting 3-way probabilities
and mapping to EvidenceRelationship.
"""

from typing import Any

from tathvyn.common.config import get_settings
from tathvyn.common.enums import EvidenceRelationship
from tathvyn.common.logging import get_logger
from tathvyn.models.interfaces import NLIModel, StanceScoreResult

logger = get_logger("nli_model")

_NLI_PIPELINE: Any = None
_NLI_LOAD_FAILED: bool = False


class DeBERTaNLIModel(NLIModel):
    """NLI stance classifier using microsoft/deberta-v3-large-mnli."""

    def __init__(self, model_name: str | None = None, device: str | None = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.nli_model_name
        self.device = device or settings.device

    def _get_pipeline(self) -> Any:
        """Lazy load HuggingFace NLI pipeline with fast local fallback."""
        global _NLI_PIPELINE, _NLI_LOAD_FAILED
        if _NLI_LOAD_FAILED:
            return None

        if _NLI_PIPELINE is None:
            try:
                from transformers import pipeline

                device_idx = 0 if self.device == "cuda" else -1
                logger.info(
                    "Loading DeBERTa NLI pipeline", model=self.model_name, device=self.device
                )
                try:
                    # Attempt loading local weights first to prevent DNS retry hangs
                    _NLI_PIPELINE = pipeline(
                        "text-classification",
                        model=self.model_name,
                        device=device_idx,
                        top_k=None,
                        model_kwargs={"local_files_only": True},
                    )
                except Exception:
                    _NLI_PIPELINE = pipeline(
                        "text-classification",
                        model=self.model_name,
                        device=device_idx,
                        top_k=None,
                    )
            except Exception as e:
                logger.warning(
                    "DeBERTa pipeline not available locally, using fast deterministic fallback",
                    error=str(e),
                )
                _NLI_LOAD_FAILED = True
                return None
        return _NLI_PIPELINE

    async def predict_stance(
        self,
        premise: str,
        hypothesis: str,
    ) -> StanceScoreResult:
        """Evaluate logical stance between premise (evidence) and hypothesis (claim)."""
        pipe = self._get_pipeline()
        if pipe is not None:
            import asyncio

            try:
                pair_input = {"text": premise, "text_pair": hypothesis}
                outputs = await asyncio.to_thread(pipe, pair_input, truncation=True, max_length=512)
                raw_outputs = outputs[0] if isinstance(outputs, list) and len(outputs) > 0 and isinstance(outputs[0], list) else outputs
                scores_by_label = {item["label"].upper(): float(item["score"]) for item in raw_outputs}

                entailment_p = scores_by_label.get(
                    "ENTAILMENT", scores_by_label.get("LABEL_0", 0.0)
                )
                neutral_p = scores_by_label.get("NEUTRAL", scores_by_label.get("LABEL_1", 0.0))
                contradiction_p = scores_by_label.get(
                    "CONTRADICTION", scores_by_label.get("LABEL_2", 0.0)
                )

                return self._map_probabilities_to_relationship(
                    entailment_p, contradiction_p, neutral_p
                )
            except Exception as e:
                logger.warning("Inference error in NLI model, falling back", error=str(e))

        return self._deterministic_fallback_stance(premise, hypothesis)

    def _map_probabilities_to_relationship(
        self,
        entailment_prob: float,
        contradiction_prob: float,
        neutral_prob: float,
    ) -> StanceScoreResult:
        """Map 3-way probabilities to canonical EvidenceRelationship enum."""
        if contradiction_prob >= 0.65 and contradiction_prob > neutral_prob:
            rel = EvidenceRelationship.CONTRADICTS
        elif contradiction_prob >= 0.50 and contradiction_prob > entailment_prob and contradiction_prob > neutral_prob:
            rel = EvidenceRelationship.PARTIALLY_CONTRADICTS
        elif entailment_prob >= 0.55:
            rel = EvidenceRelationship.SUPPORTS
        elif entailment_prob >= 0.35:
            rel = EvidenceRelationship.PARTIALLY_SUPPORTS
        else:
            rel = EvidenceRelationship.NEUTRAL

        return StanceScoreResult(
            relationship=rel,
            entailment_prob=entailment_prob,
            contradiction_prob=contradiction_prob,
            neutral_prob=neutral_prob,
        )

    def _deterministic_fallback_stance(
        self,
        premise: str,
        hypothesis: str,
    ) -> StanceScoreResult:
        """Rule-based lexical polarity fallback when DeBERTa is unavailable."""
        p_lower = premise.lower()
        h_lower = hypothesis.lower()

        negation_terms = [" not ", " never ", " no ", " refuted ", " debunked ", " false "]
        contradiction_signals = ["however", "contrary to", "despite", "refuted by", "in contrast"]

        has_negation_premise = any(term in p_lower for term in negation_terms)
        has_negation_hyp = any(term in h_lower for term in negation_terms)
        has_contradiction_signal = any(sig in p_lower for sig in contradiction_signals)

        shared_tokens = set(p_lower.split()) & set(h_lower.split())
        overlap_ratio = len(shared_tokens) / max(len(h_lower.split()), 1)

        if has_contradiction_signal or (has_negation_premise != has_negation_hyp):
            return StanceScoreResult(
                relationship=EvidenceRelationship.CONTRADICTS,
                entailment_prob=0.10,
                contradiction_prob=0.75,
                neutral_prob=0.15,
            )
        elif overlap_ratio > 0.35:
            return StanceScoreResult(
                relationship=EvidenceRelationship.SUPPORTS,
                entailment_prob=0.80,
                contradiction_prob=0.08,
                neutral_prob=0.12,
            )
        else:
            return StanceScoreResult(
                relationship=EvidenceRelationship.NEUTRAL,
                entailment_prob=0.20,
                contradiction_prob=0.15,
                neutral_prob=0.65,
            )


def probe_nli_model() -> dict:
    """Probe NLI model load status. Call at startup to surface fallback mode."""
    global _NLI_LOAD_FAILED, _NLI_PIPELINE
    model = DeBERTaNLIModel()
    pipe = model._get_pipeline()
    if pipe is not None:
        return {"nli_model": "loaded", "mode": "deberta", "fallback": False}
    return {"nli_model": "fallback", "mode": "lexical_deterministic", "fallback": True}