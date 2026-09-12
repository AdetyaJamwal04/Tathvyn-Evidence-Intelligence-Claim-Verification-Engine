"""
Adaptive Research Graph Orchestrator implementing high-throughput concurrent DAG execution.
"""

from __future__ import annotations

import asyncio
from typing import Any, AsyncGenerator
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
from tathvyn.common.models.claim import AtomicClaim
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
        """Fetch and segment a single URL under concurrency limits with title grounding and snippet fallback."""
        async with semaphore:
            doc_id = uuid4()
            title = getattr(item, "title", "") or ""
            try:
                fetched = await self.fetcher.fetch(item.url)
                doc_title = fetched.title or title or "Web Source"
                doc = Document(
                    document_id=doc_id,
                    source_id=uuid4(),
                    url=fetched.url,
                    canonical_url=fetched.canonical_url,
                    content_hash=fetched.content_hash,
                    title=doc_title,
                    author=fetched.author,
                )
                # Ground passages with article title for semantic coherence
                doc_text = fetched.main_text
                if doc_title and len(doc_title.split()) >= 3 and doc_title.lower() not in doc_text[:120].lower():
                    combined_text = f"{doc_title}. {doc_text}"
                else:
                    combined_text = doc_text

                passages = segment_document_text(
                    doc_id, combined_text, target_token_size=120
                )
                # Also include search snippet with title as high-density passage
                snippet = getattr(item, "snippet", "") or ""
                if snippet.strip() and doc_title:
                    snippet_text = f"{doc_title}. {snippet}"
                    snippet_passages = segment_document_text(doc_id, snippet_text, target_token_size=120)
                    passages.extend(snippet_passages)
                elif not passages and snippet.strip():
                    passages = segment_document_text(doc_id, snippet, target_token_size=120)

                return doc, passages
            except Exception as e:
                logger.warning("Failed to fetch search document, falling back to snippet", url=item.url, error=str(e))
                snippet = getattr(item, "snippet", "") or ""
                if snippet.strip():
                    import hashlib
                    doc_title = title or "Web Source"
                    snippet_text = f"{doc_title}. {snippet}" if doc_title else snippet
                    h = hashlib.sha256(snippet_text.encode("utf-8")).hexdigest()
                    doc = Document(
                        document_id=doc_id,
                        source_id=uuid4(),
                        url=item.url,
                        canonical_url=item.url,
                        content_hash=h,
                        title=doc_title,
                        author=None,
                    )
                    passages = segment_document_text(doc_id, snippet_text, target_token_size=120)
                    return doc, passages
                return None

    async def execute_research_stream(
        self,
        claim_text: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        request_id: UUID | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Run the full adaptive research graph for a given claim proposition, streaming stage events."""
        req_id = request_id or uuid4()
        budget = BudgetTracker(depth=depth)

        yield {
            "stage": "ANALYZING",
            "message": "Analyzing claim syntax and decomposing into atomic propositions...",
        }

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
            yield {"stage": "COMPLETED", "decision": decision, "state": state}
            return

        state.status = ResearchStateStatus.RESEARCHING
        domain_name = claim.domain.value if hasattr(claim.domain, "value") else str(claim.domain)
        yield {
            "stage": "DECOMPOSED",
            "message": f"Extracted {len(atomic_claims)} atomic proposition(s) in {domain_name} domain.",
            "atomic_claims": [ac.text for ac in atomic_claims],
            "domain": domain_name,
        }

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
            for _ac_id, q_str in queries_to_run:
                if budget.can_consume_queries(1):
                    executed_queries.append(q_str)
                    budget.record_query(1)
                    valid_queries.append(q_str)

            if not valid_queries:
                break

            yield {
                "stage": "SEARCHING",
                "message": f"Querying multi-source evidence: {', '.join(valid_queries[:2])}...",
                "queries": valid_queries,
            }

            # A. Concurrent Parallel Search Execution
            search_tasks = [
                self.search_manager.search(q, max_results=5) for q in valid_queries
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

            yield {
                "stage": "RETRIEVING",
                "message": f"Extracted and segmented {len(passages_by_id)} evidence passages from authoritative web sources...",
            }
            yield {
                "stage": "INFERENCE",
                "message": "Evaluating evidence passages with NLI cross-encoders...",
            }

            # C. Concurrent Assessment Node: Evaluate all atomic claims concurrently
            all_passages = list(passages_by_id.values())
            assessment_tasks = [
                self.evidence_engine.evaluate_atomic_claim_evidence(
                    atomic_claim=ac,
                    passages=all_passages,
                    documents_by_id=docs_by_id,
                    top_k=8,
                )
                for ac in atomic_claims
            ]
            eval_results = await asyncio.gather(*assessment_tasks, return_exceptions=True)

            current_conflicts = []
            for ac, res in zip(atomic_claims, eval_results, strict=False):
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
        yield {
            "stage": "SYNTHESIZING",
            "message": "Calibrating truthfulness confidence & synthesizing epistemic verdict...",
        }
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
            docs_retrieved=len(docs_by_id),
        )

        suff_result = calculate_evidence_sufficiency(all_evidence)

        # Dynamic raw confidence based on atomic evaluations
        raw_conf = sum(eval_confidences) / len(eval_confidences) if eval_confidences else 0.50
        if agg_result.internal_verdict == InternalVerdict.PARTIALLY_SUPPORTED:
            raw_conf = max(raw_conf, 0.88)
        elif agg_result.internal_verdict == InternalVerdict.REFUTED:
            raw_conf = max(raw_conf, 0.78)

        is_refuted = (agg_result.internal_verdict == InternalVerdict.REFUTED)

        calibrated_conf = self.calibrator.calibrate(
            raw_confidence=raw_conf,
            sufficiency_score=suff_result.sufficiency_score,
            has_temporal_discrepancy=False,
            has_unresolved_conflict=len(current_conflicts) > 0,
            is_negative_evidence_refuted=is_refuted,
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
        yield {"stage": "COMPLETED", "decision": final_verdict, "state": state}

    async def execute_research(
        self,
        claim_text: str,
        depth: ResearchDepth = ResearchDepth.STANDARD,
        request_id: UUID | None = None,
    ) -> tuple[VerdictDecision, ResearchState]:
        """Run the full adaptive research graph for a given claim proposition."""
        async for event in self.execute_research_stream(
            claim_text=claim_text, depth=depth, request_id=request_id
        ):
            if event["stage"] == "COMPLETED":
                return event["decision"], event["state"]
        raise RuntimeError("Research stream finished without completion event.")

    execute_verification = execute_research
