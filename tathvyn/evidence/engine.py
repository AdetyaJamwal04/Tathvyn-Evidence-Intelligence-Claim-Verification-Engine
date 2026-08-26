"""Evidence Assessment Engine and Epistemic State Aggregator.

Coordinates passage reranking, NLI stance scoring, numerical/temporal validation,
provenance clustering, and conflict detection into an EvidenceState object.
"""

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

            # If numerical mismatch detected, downgrade SUPPORT to CONTRADICTION / QUALIFICATION
            relationship = stance.relationship
            if not num_val.is_compatible and relationship == EvidenceRelationship.SUPPORTS:
                relationship = EvidenceRelationship.CONTRADICTS

            ev = Evidence(
                atomic_claim_id=atomic_claim.atomic_claim_id,
                passage_id=passage.passage_id,
                relationship=relationship,
                relevance_score=item.relevance_score,
                entailment_score=stance.entailment_prob,
                contradiction_score=stance.contradiction_prob,
                source_quality_score=0.80,
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

        # Calculate coverage score weighted by independence
        total_ind_support = sum(e.independence_score * e.relevance_score for e in supporting)
        total_ind_contra = sum(e.independence_score * e.relevance_score for e in contradicting)
        coverage = min(1.0, (total_ind_support + total_ind_contra) / 2.0)

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
