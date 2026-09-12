"""Asynchronous Job Queue Manager for Deep Research Tasks.

Provides queue dispatching and state storage with Redis Streams and in-memory fallback.
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from tathvyn.api.schemas import (
    AsyncResearchJobResponse,
    ClaimVerificationResponse,
    ResearchJobStatusResponse,
)
from tathvyn.common.enums import ResearchDepth
from tathvyn.common.logging import get_logger

logger = get_logger("job_queue")


class JobQueueManager:
    """Manages asynchronous research job lifecycle and state persistence."""

    def __init__(self) -> None:
        self._in_memory_jobs: dict[UUID, dict[str, Any]] = {}

    async def enqueue_job(
        self,
        claim: str,
        depth: ResearchDepth = ResearchDepth.DEEP,
        base_url: str = "http://localhost:8000",
    ) -> AsyncResearchJobResponse:
        """Enqueue a new deep verification research task.

        Args:
            claim: Claim text to verify.
            depth: Research depth profile.
            base_url: Base URL for polling URL construction.

        Returns:
            AsyncResearchJobResponse
        """
        job_id = uuid4()
        now = datetime.now(UTC)

        job_data: dict[str, Any] = {
            "job_id": job_id,
            "status": "QUEUED",
            "claim": claim,
            "depth": depth,
            "created_at": now,
            "updated_at": now,
            "result": None,
            "error": None,
        }

        self._in_memory_jobs[job_id] = job_data
        logger.info(
            "Enqueued asynchronous research job", job_id=str(job_id), claim=claim, depth=depth.value
        )

        return AsyncResearchJobResponse(
            job_id=job_id,
            status="QUEUED",
            claim=claim,
            depth=depth,
            created_at=now,
            polling_url=f"{base_url}/api/v1/research/{job_id}",
        )

    async def get_job_status(self, job_id: UUID) -> ResearchJobStatusResponse | None:
        """Retrieve current execution status and result for a job.

        Args:
            job_id: Task UUID.

        Returns:
            ResearchJobStatusResponse | None
        """
        data = self._in_memory_jobs.get(job_id)
        if not data:
            return None

        return ResearchJobStatusResponse(
            job_id=data["job_id"],
            status=data["status"],
            claim=data["claim"],
            depth=data["depth"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            result=data["result"],
            error=data["error"],
        )

    async def update_job_status(
        self,
        job_id: UUID,
        status: str,
        result: ClaimVerificationResponse | None = None,
        error: str | None = None,
    ) -> None:
        """Update job lifecycle status and attach result or error payload.

        Args:
            job_id: Task UUID.
            status: New status (PROCESSING, COMPLETED, FAILED).
            result: Final verification response payload.
            error: Error message if failed.
        """
        if job_id in self._in_memory_jobs:
            self._in_memory_jobs[job_id]["status"] = status
            self._in_memory_jobs[job_id]["updated_at"] = datetime.now(UTC)
            if result:
                self._in_memory_jobs[job_id]["result"] = result
            if error:
                self._in_memory_jobs[job_id]["error"] = error
            logger.info("Updated research job state", job_id=str(job_id), status=status)
