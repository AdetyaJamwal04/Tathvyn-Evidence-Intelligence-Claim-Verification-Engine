"""End-to-End VeriFact MVP Pipeline.

Connects Claim Intelligence, Search Retrieval, Document Fetching, Passage
Segmentation, Evidence Assessment, and Verdict Determination into a unified pipeline.
"""

from uuid import UUID, uuid4

from tathvyn.claims.pipeline import ClaimIntelligencePipeline
from tathvyn.common.enums import (
    AtomicClaimVerdict,
    ClaimVerifiability,
    InternalVerdict,
    PublicVerdict,
)
from tathvyn.common.logging import get_logger
from tathvyn.common.models.claim import AtomicClaim
from tathvyn.common.models.evidence import Evidence
from tathvyn.common.models.source import Document, Passage
from tathvyn.common.models.verdict import Citation, VerdictDecision
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.retrieval.fetcher import HTTPDocumentFetcher
from tathvyn.retrieval.interfaces import DocumentFetcher, SearchProvider
from tathvyn.retrieval.providers.manager import SearchProviderManager
from tathvyn.retrieval.segmenter import segment_document_text
from tathvyn.verdict.aggregator import ParentVerdictAggregator
from tathvyn.verdict.atomic_evaluator import AtomicClaimVerdictEvaluator
from tathvyn.verdict.calibrator import ConfidenceCalibrator
from tathvyn.verdict.explainer import GroundedExplanationBuilder
from tathvyn.verdict.sufficiency import calculate_evidence_sufficiency

logger = get_logger("verifact_pipeline")


class VeriFactPipeline:
    """End-to-End Automated Fact Verification Pipeline."""

    def __init__(
        self,
        search_provider: SearchProvider | None = None,
        document_fetcher: DocumentFetcher | None = None,
        evidence_engine: EvidenceAssessmentEngine | None = None,
    ) -> None:
        self.claim_pipeline = ClaimIntelligencePipeline()
        self.search_manager = SearchProviderManager(primary_provider=search_provider)
        self.fetcher = document_fetcher or HTTPDocumentFetcher()
        self.evidence_engine = evidence_engine or EvidenceAssessmentEngine()
        self.atomic_evaluator = AtomicClaimVerdictEvaluator()
        self.aggregator = ParentVerdictAggregator()
        self.calibrator = ConfidenceCalibrator()
        self.explainer = GroundedExplanationBuilder()

    async def verify_claim(
        self,
        claim_text: str,
        request_id: UUID | None = None,
    ) -> VerdictDecision:
        """Execute end-to-end verification of a user claim.

        Args:
            claim_text: Raw input claim text.
            request_id: Optional client request UUID.

        Returns:
            VerdictDecision: Calibrated verdict, public label, confidence, and citations.
        """
        req_id = request_id or uuid4()
        logger.info("Starting verification pipeline", request_id=str(req_id), claim=claim_text)

        # 1. Claim Intelligence Stage
        analysis = self.claim_pipeline.analyze(claim_text, request_id=req_id)
        claim = analysis.claim
        atomic_claims = analysis.atomic_claims

        # Fast path: Unverifiable claims (Opinions / Normative statements)
        if claim.verifiability == ClaimVerifiability.UNVERIFIABLE:
            unverifiable_citations: list[Citation] = []
            summary = self.explainer.generate_summary(
                claim_text=claim.normalized_text,
                verdict=InternalVerdict.UNVERIFIABLE,
                citations=unverifiable_citations,
                rationale=analysis.verifiability_reasoning,
            )
            return VerdictDecision(
                verdict=InternalVerdict.UNVERIFIABLE,
                public_label=PublicVerdict.UNVERIFIABLE,
                framing_concerns=False,
                confidence=1.0,
                evidence_sufficiency=1.0,
                stop_reason="UNVERIFIABLE",
                summary_text=summary,
                citations=unverifiable_citations,
            )

        # 2. Retrieval, Fetching, and Evidence Assessment per Atomic Claim
        atomic_evaluations: list[tuple[AtomicClaim, AtomicClaimVerdict]] = []
        all_evidence: list[Evidence] = []
        all_passages_by_id: dict[UUID, Passage] = {}
        all_docs_by_id: dict[UUID, Document] = {}

        for atomic in atomic_claims:
            # Search candidate sources
            search_resp = await self.search_manager.search(atomic.text, max_results=3)

            # Fetch top documents
            passages_for_atomic: list[Passage] = []
            for item in search_resp.results:
                try:
                    fetched = await self.fetcher.fetch(item.url)
                    doc_id = uuid4()
                    doc = Document(
                        document_id=doc_id,
                        source_id=uuid4(),
                        url=fetched.url,
                        canonical_url=fetched.canonical_url,
                        content_hash=fetched.content_hash,
                        title=fetched.title or item.title,
                        author=fetched.author,
                        published_at=None,
                    )
                    all_docs_by_id[doc_id] = doc

                    # Segment into passages
                    doc_passages = segment_document_text(
                        doc_id, fetched.main_text, target_token_size=300
                    )
                    for p in doc_passages:
                        all_passages_by_id[p.passage_id] = p
                        passages_for_atomic.append(p)
                except Exception as e:
                    logger.warning(
                        "Failed to fetch/parse search result", url=item.url, error=str(e)
                    )
                    continue

            # Evaluate Evidence for Atomic Claim
            ev_state, _, _ = await self.evidence_engine.evaluate_atomic_claim_evidence(
                atomic_claim=atomic,
                passages=passages_for_atomic,
                documents_by_id=all_docs_by_id,
                top_k=3,
            )

            # Evaluate Atomic Verdict
            eval_result = self.atomic_evaluator.evaluate_atomic_claim(
                evidence_state=ev_state,
                is_subjective_or_opinion=False,
            )
            atomic_evaluations.append((atomic, eval_result.verdict))
            all_evidence.extend(ev_state.supporting_evidence + ev_state.contradicting_evidence)

        # 3. Parent Verdict Aggregation
        agg_result = self.aggregator.aggregate_verdicts(
            atomic_evaluations=atomic_evaluations,
            claim_verifiability=claim.verifiability,
        )

        # 4. Evidence Sufficiency & Confidence Calibration
        suff_result = calculate_evidence_sufficiency(all_evidence)
        calibrated_conf = self.calibrator.calibrate(
            raw_confidence=0.85,
            sufficiency_score=suff_result.sufficiency_score,
            has_temporal_discrepancy=False,
            has_unresolved_conflict=False,
        )

        # 5. Build Citations & Grounded Explanation
        citations = self.explainer.build_citations(
            evidence_items=all_evidence,
            passages_by_id=all_passages_by_id,
            documents_by_id=all_docs_by_id,
            max_citations=5,
        )

        summary = self.explainer.generate_summary(
            claim_text=claim.normalized_text,
            verdict=agg_result.internal_verdict,
            citations=citations,
            rationale=agg_result.rationale,
        )

        supporting_ids = [e.evidence_id for e in all_evidence if "SUPPORT" in e.relationship.value]
        contradicting_ids = [
            e.evidence_id for e in all_evidence if "CONTRADICT" in e.relationship.value
        ]

        return VerdictDecision(
            verdict=agg_result.internal_verdict,
            public_label=agg_result.public_label,
            framing_concerns=agg_result.framing_concerns,
            confidence=calibrated_conf,
            evidence_sufficiency=suff_result.sufficiency_score,
            stop_reason="SUFFICIENT_EVIDENCE"
            if suff_result.is_sufficient
            else "EVALUATION_COMPLETE",
            summary_text=summary,
            citations=citations,
            supporting_evidence_ids=supporting_ids,
            contradicting_evidence_ids=contradicting_ids,
            unresolved_atomic_claim_ids=[
                ac.atomic_claim_id
                for ac, v in atomic_evaluations
                if v in (AtomicClaimVerdict.INSUFFICIENT, AtomicClaimVerdict.CONFLICTED)
            ],
        )
