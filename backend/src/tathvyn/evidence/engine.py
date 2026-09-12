"""Evidence Assessment Engine and Epistemic State Aggregator.

Coordinates passage reranking, NLI stance scoring, numerical/temporal validation,
provenance clustering, and conflict detection into an EvidenceState object.
"""

import re
from uuid import UUID

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.common.logging import get_logger
from tathvyn.common.models.claim import AtomicClaim
from tathvyn.common.models.conflict import Conflict
from tathvyn.common.models.evidence import Evidence, EvidenceState
from tathvyn.common.models.provenance import ProvenanceGroup
from tathvyn.common.models.source import Document, Passage
from tathvyn.evidence.conflict_detector import ConflictDetector
from tathvyn.evidence.provenance import ProvenanceClusterer
from tathvyn.evidence.validators.numerical_validator import validate_numerical_consistency
from tathvyn.evidence.validators.temporal_validator import validate_temporal_alignment
from tathvyn.models.interfaces import NLIModel, RerankerModel
from tathvyn.models.nli import DeBERTaNLIModel
from tathvyn.models.reranker import BGERerankerModel


# Domain-authority quality score mapping
_DOMAIN_QUALITY_MAP: dict[str, float] = {
    # Tier 1: Official government & institutional sources
    "isro.gov.in": 0.97,
    "nasa.gov": 0.97,
    "jpl.nasa.gov": 0.97,
    "esa.int": 0.95,
    "pib.gov.in": 0.95,
    "rbi.org.in": 0.95,
    "sansad.in": 0.93,
    "whitehouse.gov": 0.95,
    "federalreserve.gov": 0.95,
    "who.int": 0.95,
    "cdc.gov": 0.95,
    "fda.gov": 0.93,
    "nih.gov": 0.95,
    ".gov": 0.92,
    ".gov.in": 0.92,
    "cnsa.gov.cn": 0.90,
    # Tier 2: Authoritative news & research
    "reuters.com": 0.88,
    "bbc.com": 0.87,
    "bbc.co.uk": 0.87,
    "apnews.com": 0.88,
    "thehindu.com": 0.85,
    "ndtv.com": 0.82,
    "hindustantimes.com": 0.81,
    "indianexpress.com": 0.83,
    "timesofindia.indiatimes.com": 0.81,
    "nature.com": 0.92,
    "science.org": 0.92,
    "pubmed.ncbi.nlm.nih.gov": 0.93,
    "arxiv.org": 0.85,
    "scholar.google.com": 0.83,
    "wikipedia.org": 0.72,
}


def _get_source_quality_score(doc) -> float:
    """Derive a quality score [0.72, 0.97] from the document's domain."""
    if doc is None:
        return 0.75
    url = getattr(doc, "canonical_url", None) or getattr(doc, "url", "") or ""
    try:
        domain = url.split("/")[2].lower() if "/" in url else url.lower()
    except Exception:
        return 0.75
    # Exact match
    if domain in _DOMAIN_QUALITY_MAP:
        return _DOMAIN_QUALITY_MAP[domain]
    # Suffix match (e.g. any .gov or .gov.in)
    for suffix, score in _DOMAIN_QUALITY_MAP.items():
        if suffix.startswith(".") and domain.endswith(suffix):
            return score
    return 0.75  # Default for unrecognized sources

logger = get_logger("evidence_engine")


class EvidenceAssessmentEngine:
    """Orchestrates end-to-end evidence evaluation for atomic propositions."""

    def __init__(
        self,
        reranker: RerankerModel | None = None,
        nli_model: NLIModel | None = None,
    ) -> None:
        self.reranker = reranker or BGERerankerModel()
        self.nli_model = nli_model or DeBERTaNLIModel()
        self.provenance_clusterer = ProvenanceClusterer()
        self.conflict_detector = ConflictDetector()

    async def evaluate_atomic_claim_evidence(
        self,
        atomic_claim: AtomicClaim,
        passages: list[Passage],
        documents_by_id: dict[UUID, Document],
        top_k: int = 5,
    ) -> tuple[EvidenceState, list[ProvenanceGroup], list[Conflict]]:
        """Evaluate raw candidate passages against an atomic claim proposition.

        Args:
            atomic_claim: The proposition being assessed.
            passages: Candidate passages retrieved from search.
            documents_by_id: Map of document_id to Document object.
            top_k: Max passages to evaluate with expensive NLI inference.

        Returns:
            tuple: (EvidenceState, list[ProvenanceGroup], list[Conflict])
        """
        if not passages:
            empty_state = EvidenceState(
                atomic_claim_id=atomic_claim.atomic_claim_id,
                supporting_evidence=[],
                contradicting_evidence=[],
                context_evidence=[],
                coverage_score=0.0,
                temporal_validity=True,
                unresolved_conflict=False,
            )
            return empty_state, [], []

        passages_by_id = {p.passage_id: p for p in passages}

        # 1. Rerank candidate passages against the atomic claim text
        passage_tuples = [(str(p.passage_id), p.text) for p in passages]
        reranked_items = await self.reranker.rerank(
            query=atomic_claim.text,
            passages=passage_tuples,
            top_k=top_k,
        )

        evidence_items: list[Evidence] = []

        # 2. For each top-ranked passage, run NLI and validators
        for item in reranked_items:
            p_uuid = UUID(item.passage_id)
            passage = passages_by_id[p_uuid]
            doc = documents_by_id.get(passage.document_id)

            # NLI Stance Prediction
            stance = await self.nli_model.predict_stance(
                premise=passage.text,
                hypothesis=atomic_claim.text,
            )

            # Numerical & Temporal Deterministic Validation
            num_val = validate_numerical_consistency(atomic_claim.text, passage.text)
            temp_val = validate_temporal_alignment(
                claim_text=atomic_claim.text,
                evidence_text=passage.text,
                evidence_published_year=doc.published_at.year if doc and doc.published_at else None,
            )

            # Entity relevance gate: a passage cannot CONTRADICT a claim if it does not even mention the claim's core topic
            relationship = stance.relationship
            claim_keywords = [
                w.lower() for w in re.findall(r"\b[a-zA-Z]{3,}\b", atomic_claim.text)
                if w.lower() not in ("the", "and", "that", "this", "for", "with", "was", "are", "were", "been", "from", "most", "among")
            ]
            passage_lower = passage.text.lower()
            mentions_core_topic = any(kw in passage_lower for kw in claim_keywords)
            if relationship in (EvidenceRelationship.CONTRADICTS, EvidenceRelationship.PARTIALLY_CONTRADICTS) and not mentions_core_topic:
                relationship = EvidenceRelationship.NEUTRAL

            # If explicit numerical mismatch detected, downgrade SUPPORT to CONTRADICTION
            if not num_val.is_compatible and num_val.validation_status == "NUMERICAL_MISMATCH":
                if relationship in (EvidenceRelationship.SUPPORTS, EvidenceRelationship.PARTIALLY_SUPPORTS):
                    relationship = EvidenceRelationship.CONTRADICTS

            ev = Evidence(
                atomic_claim_id=atomic_claim.atomic_claim_id,
                passage_id=passage.passage_id,
                relationship=relationship,
                relevance_score=max(0.0, min(1.0, float(item.relevance_score))),
                entailment_score=stance.entailment_prob,
                contradiction_score=stance.contradiction_prob,
                source_quality_score=_get_source_quality_score(doc),
                independence_score=1.0,
                temporal_validity_status=temp_val.status,
            )
            evidence_items.append(ev)

        # 3. Provenance Clustering & Epistemic Independence Scoring
        clusters, updated_evidence = self.provenance_clusterer.cluster_evidence(
            evidence_items=evidence_items,
            passages_by_id=passages_by_id,
            documents_by_id=documents_by_id,
        )

        # 4. Conflict Detection
        conflicts = self.conflict_detector.detect_conflicts(
            atomic_claim_id=atomic_claim.atomic_claim_id,
            evidence_items=updated_evidence,
        )

        # 5. Build Aggregated EvidenceState
        supporting = [
            e
            for e in updated_evidence
            if e.relationship
            in (EvidenceRelationship.SUPPORTS, EvidenceRelationship.PARTIALLY_SUPPORTS)
        ]
        contradicting = [
            e
            for e in updated_evidence
            if e.relationship
            in (EvidenceRelationship.CONTRADICTS, EvidenceRelationship.PARTIALLY_CONTRADICTS)
        ]
        context = [
            e
            for e in updated_evidence
            if e.relationship
            not in (
                EvidenceRelationship.SUPPORTS,
                EvidenceRelationship.PARTIALLY_SUPPORTS,
                EvidenceRelationship.CONTRADICTS,
                EvidenceRelationship.PARTIALLY_CONTRADICTS,
            )
        ]

        # Calculate coverage score weighted by independence (including topic-relevant context evidence)
        total_ind_support = sum(e.independence_score * e.relevance_score for e in supporting)
        total_ind_contra = sum(e.independence_score * e.relevance_score for e in contradicting)
        total_ind_context = sum(e.independence_score * e.relevance_score for e in context)
        coverage = min(1.0, (total_ind_support + total_ind_contra + 0.40 * total_ind_context) / 2.0)

        evidence_state = EvidenceState(
            atomic_claim_id=atomic_claim.atomic_claim_id,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            context_evidence=context,
            coverage_score=round(coverage, 4),
            temporal_validity=all(e.temporal_validity_status == "VALID" for e in updated_evidence),
            unresolved_conflict=len(conflicts) > 0,
        )

        logger.info(
            "Evaluated atomic claim evidence",
            atomic_claim_id=str(atomic_claim.atomic_claim_id),
            supporting_count=len(supporting),
            contradicting_count=len(contradicting),
            conflicts_count=len(conflicts),
            coverage=coverage,
        )

        return evidence_state, clusters, conflicts
