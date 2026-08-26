"""Background Research Worker Execution Engine."""

import time
from uuid import UUID

from tathvyn.api.schemas import CitationSchema, ClaimVerificationResponse
from tathvyn.common.logging import get_logger
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.workers.queue import JobQueueManager

logger = get_logger("research_worker")


class ResearchWorker:
    """Executes asynchronous background research tasks."""

    def __init__(
        self,
        queue_manager: JobQueueManager,
        research_engine: AdaptiveResearchEngine | None = None,
    ) -> None:
        self.queue_manager = queue_manager
        self.research_engine = research_engine or AdaptiveResearchEngine()

    async def process_job(self, job_id: UUID) -> None:
        """Process a single queued research task by ID.

        Args:
            job_id: Task UUID.
        """
        job = await self.queue_manager.get_job_status(job_id)
        if not job:
            logger.warning("Worker attempted to process non-existent job", job_id=str(job_id))
            return

        logger.info("Worker starting task processing", job_id=str(job_id), claim=job.claim)
        await self.queue_manager.update_job_status(job_id, status="PROCESSING")

        start_time = time.perf_counter()
        try:
            decision, state = await self.research_engine.verify(
                claim_text=job.claim,
                depth=job.depth,
                request_id=job_id,
            )

            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            citations_schema = [
                CitationSchema(
                    citation_id=c.citation_id,
                    url=c.url,
                    source_name=c.source_name,
                    domain=c.domain,
                    authority_class=c.authority_class,
                    supporting_passage=c.supporting_passage,
                )
                for c in decision.citations
            ]

            response_payload = ClaimVerificationResponse(
                request_id=job_id,
                claim=job.claim,
                verdict=decision.verdict,
                public_label=decision.public_label,
                confidence=decision.confidence,
                evidence_sufficiency=decision.evidence_sufficiency,
                framing_concerns=decision.framing_concerns,
                stop_reason=decision.stop_reason,
                summary_text=decision.summary_text,
                citations=citations_schema,
                latency_ms=latency_ms,
            )

            await self.queue_manager.update_job_status(
                job_id=job_id,
                status="COMPLETED",
                result=response_payload,
            )
            logger.info("Worker completed task successfully", job_id=str(job_id), latency_ms=latency_ms)

        except Exception as e:
            logger.error("Worker failed task execution", job_id=str(job_id), error=str(e))
            await self.queue_manager.update_job_status(
                job_id=job_id,
                status="FAILED",
                error=str(e),
            )
