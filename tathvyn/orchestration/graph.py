"""
Adaptive Research Graph Orchestrator implementing high-throughput concurrent DAG execution.
"""

from __future__ import annotations

import asyncio
import time
from uuid import UUID, uuid4

from tathvyn.claims.pipeline import ClaimIntelligencePipeline
from tathvyn.common.enums import (
    AtomicClaimVerdict,
    ClaimVerifiability,
    InternalVerdict,
    PublicVerdict,
    ResearchDepth,
    ResearchLoopDecision,
    ResearchStateStatus,
)
from tathvyn.common.logging import get_logger
from tathvyn.common.models.claim import AtomicClaim, Claim
from tathvyn.common.models.evidence import Evidence, EvidenceState
from tathvyn.common.models.provenance import ProvenanceGroup
from tathvyn.common.models.research import ResearchState
from tathvyn.common.models.source import Document, Passage
from tathvyn.common.models.verdict import Citation, VerdictDecision
from tathvyn.evidence.engine import EvidenceAssessmentEngine
from tathvyn.orchestration.budget import BudgetTracker
from tathvyn.orchestration.controller import AdaptiveLoopController
from tathvyn.orchestration.formulator import QueryFormulator
from tathvyn.retrieval.fetcher import DocumentFetcher, HTTPDocumentFetcher
from tathvyn.retrieval.interfaces import SearchProvider
from tathvyn.retrieval.providers.manager import SearchProviderManager
from tathvyn.retrieval.segmenter import segment_document_text
from tathvyn.verdict.aggregator import ParentVerdictAggregator
from tathvyn.verdict.atomic_evaluator import AtomicClaimVerdictEvaluator
from tathvyn.verdict.calibrator import ConfidenceCalibrator
from tathvyn.verdict.explainer import GroundedExplanationBuilder
from tathvyn.verdict.sufficiency import calculate_evidence_sufficiency

logger = get_logger("research_graph")


class ResearchGraphRunner:
    """Executes the iterative claim verification loop with parallelized async retrieval and evaluation."""

    def __init__(
        self,
        claims_pipeline: ClaimIntelligencePipeline | None = None,
        search_provider: SearchProvider | None = None,
        search_manager: SearchProviderManager | None = None,
        fetcher: DocumentFetcher | None = None,
        document_fetcher: DocumentFetcher | None = None,
        evidence_engine: EvidenceAssessmentEngine | None = None,
        formulator: QueryFormulator | None = None,
        controller: AdaptiveLoopController | None = None,
        atomic_evaluator: AtomicClaimVerdictEvaluator | None = None,
        aggregator: ParentVerdictAggregator | None = None,
        calibrator: ConfidenceCalibrator | None = None,
        explainer: GroundedExplanationBuilder | None = None,
    ) -> None:
        self.claims_pipeline = claims_pipeline or ClaimIntelligencePipeline()
        self.search_manager = search_manager or (
            search_provider if isinstance(search_provider, SearchProviderManager) else SearchProviderManager()
        )
        self.search_provider = search_provider or self.search_manager
        self.fetcher = fetcher or document_fetcher or HTTPDocumentFetcher()
        self.evidence_engine = evidence_engine or EvidenceAssessmentEngine()
        self.formulator = formulator or QueryFormulator()
        self.controller = controller or AdaptiveLoopController()
        self.atomic_evaluator = atomic_evaluator or AtomicClaimVerdictEvaluator()
        self.aggregator = aggregator or ParentVerdictAggregator()
        self.calibrator = calibrator or ConfidenceCalibrator()
        self.explainer = explainer or GroundedExplanationBuilder()

    async def _fetch_single_doc(
        self,
        item,
        semaphore: asyncio.Semaphore,
    ) -> tuple[Document, list[Passage]] | None:
        """Fetch and segment a single URL under concurrency limits."""
        async with semaphore:
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
                )
                passages = segment_document_text(
                    doc_id, fetched.main_text, target_token_size=300
                )
                return doc, passages
            except Exception as e:
                logger.warning("Failed to fetch search document", url=item.url, error=str(e))
                return None

    async def execute_research(
        self,
        claim_text: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        request_id: UUID | None = None,
    ) -> tuple[VerdictDecision, ResearchState]:
        """Run the full adaptive research graph for a given claim proposition."""
        req_id = request_id or uuid4()
        budget = BudgetTracker(depth=depth)

        # 1. Claim Intelligence Stage
        analysis = self.claims_pipeline.analyze(
            raw_input=claim_text,
            request_id=req_id,
        )
        claim = analysis.claim
        atomic_claims = analysis.atomic_claims

        state = ResearchState(
            verification_id=req_id,
            claim=claim,
            atomic_claims=atomic_claims,
            current_iteration=0,
            status=ResearchStateStatus.ANALYZING,
        )

        # Fast path for unverifiable subjective/normative claims
        if claim.verifiability == ClaimVerifiability.UNVERIFIABLE:
            unverifiable_citations: list[Citation] = []
            summary = self.explainer.generate_summary(
                claim_text=claim.normalized_text,
                verdict=InternalVerdict.UNVERIFIABLE,
                citations=unverifiable_citations,
                rationale=analysis.verifiability_reasoning,
            )
            decision = VerdictDecision(
                verdict=InternalVerdict.UNVERIFIABLE,
                public_label=PublicVerdict.UNVERIFIABLE,
                framing_concerns=False,
                confidence=1.0,
                evidence_sufficiency=1.0,
                stop_reason="UNVERIFIABLE",
                summary_text=summary,
                citations=unverifiable_citations,
            )
            state.status = ResearchStateStatus.COMPLETED
            return decision, state

        state.status = ResearchStateStatus.RESEARCHING

        # Track documents and passages across iterations
        docs_by_id: dict[UUID, Document] = {}
        passages_by_id: dict[UUID, Passage] = {}
        all_evidence: list[Evidence] = []
        all_clusters: list[ProvenanceGroup] = []
        executed_queries: list[str] = []
        latest_evidence_states: dict[UUID, EvidenceState] = {}
        atomic_claims_by_id = {ac.atomic_claim_id: ac for ac in atomic_claims}
        seen_urls: set[str] = set()

        # 2. Iterative Adaptive Loop
        while True:
            budget.record_iteration()
            iteration = budget.iterations_completed
            state.current_iteration = iteration

            # Formulate queries
            if iteration == 1:
                queries_to_run = self.formulator.formulate_initial_queries(
                    atomic_claims, max_queries=budget.limits.max_queries
                )
            else:
                unresolved = [
                    atomic_claims_by_id[ac_id]
                    for ac_id, st in latest_evidence_states.items()
                    if st.coverage_score < 0.60
                ]
                queries_to_run = self.formulator.formulate_refinement_queries(
                    unresolved_atomic_claims=unresolved or atomic_claims,
                    past_queries=executed_queries,
                    max_queries=3,
                )

            if not queries_to_run:
                break

            # Filter valid queries within budget
            valid_queries = []
            for ac_id, q_str in queries_to_run:
                if budget.can_consume_queries(1):
                    executed_queries.append(q_str)
                    budget.record_query(1)
                    valid_queries.append(q_str)

            if not valid_queries:
                break

            # A. Concurrent Parallel Search Execution
            search_tasks = [
                self.search_manager.search(q, max_results=3) for q in valid_queries
            ]
            search_responses = await asyncio.gather(*search_tasks, return_exceptions=True)

            # Collect unique items across all queries
            items_to_fetch = []
            for resp in search_responses:
                if isinstance(resp, Exception) or not resp or not hasattr(resp, "results"):
                    continue
                for item in resp.results:
                    if item.url not in seen_urls:
                        seen_urls.add(item.url)
                        items_to_fetch.append(item)

            # B. Concurrent Parallel Document Fetching (Semaphore capped at 8)
            fetch_semaphore = asyncio.Semaphore(8)
            fetch_tasks = [
                self._fetch_single_doc(item, fetch_semaphore) for item in items_to_fetch
            ]
            fetch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

            for res in fetch_results:
                if isinstance(res, tuple) and res is not None:
                    doc, passages = res
                    docs_by_id[doc.document_id] = doc
                    for p in passages:
                        passages_by_id[p.passage_id] = p

            # C. Concurrent Assessment Node: Evaluate all atomic claims concurrently
            all_passages = list(passages_by_id.values())
            assessment_tasks = [
                self.evidence_engine.evaluate_atomic_claim_evidence(
                    atomic_claim=ac,
                    passages=all_passages,
                    documents_by_id=docs_by_id,
                    top_k=3,
                )
                for ac in atomic_claims
            ]
            eval_results = await asyncio.gather(*assessment_tasks, return_exceptions=True)

            current_conflicts = []
            for ac, res in zip(atomic_claims, eval_results):
                if isinstance(res, Exception):
                    logger.error("Error evaluating atomic claim", error=str(res))
                    continue
                ev_state, clusters, confs = res
                latest_evidence_states[ac.atomic_claim_id] = ev_state
                current_conflicts.extend(confs)
                all_clusters.extend(clusters)
                all_evidence.extend(ev_state.supporting_evidence + ev_state.contradicting_evidence)

            state.unresolved_conflicts = current_conflicts
            state.provenance_clusters = all_clusters

            # Controller Decision Node
            loop_decision = self.controller.evaluate_loop_state(
                evidence_states=list(latest_evidence_states.values()),
                conflicts=current_conflicts,
                budget_tracker=budget,
            )

            logger.info(
                "Orchestrator loop decision",
                iteration=iteration,
                decision=loop_decision.decision.value,
                rationale=loop_decision.rationale,
            )

            if loop_decision.decision == ResearchLoopDecision.TERMINATE:
                break

        # 3. Synthesis Node: Compute final parent verdict
        state.status = ResearchStateStatus.VERDICT
        atomic_evaluations: list[tuple[AtomicClaim, AtomicClaimVerdict]] = []
        eval_confidences = []

        for ac in atomic_claims:
            ev_state_item = latest_evidence_states.get(ac.atomic_claim_id)
            if ev_state_item is not None:
                res = self.atomic_evaluator.evaluate_atomic_claim(ev_state_item)
                atomic_evaluations.append((ac, res.verdict))
                eval_confidences.append(res.confidence)
            else:
                atomic_evaluations.append((ac, AtomicClaimVerdict.INSUFFICIENT))
                eval_confidences.append(0.30)

        agg_result = self.aggregator.aggregate_verdicts(
            atomic_evaluations=atomic_evaluations,
            claim_verifiability=claim.verifiability,
        )

        suff_result = calculate_evidence_sufficiency(all_evidence)

        # Dynamic raw confidence based on atomic evaluations
        raw_conf = sum(eval_confidences) / len(eval_confidences) if eval_confidences else 0.50
        if agg_result.internal_verdict == InternalVerdict.PARTIALLY_SUPPORTED:
            raw_conf = max(raw_conf, 0.88)

        calibrated_conf = self.calibrator.calibrate(
            raw_confidence=raw_conf,
            sufficiency_score=suff_result.sufficiency_score,
            has_temporal_discrepancy=False,
            has_unresolved_conflict=len(current_conflicts) > 0,
        )

        citations = self.explainer.build_citations(
            evidence_items=all_evidence,
            passages_by_id=passages_by_id,
            documents_by_id=docs_by_id,
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

        final_verdict = VerdictDecision(
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

        state.status = ResearchStateStatus.COMPLETED
        return final_verdict, state

    execute_verification = execute_research
