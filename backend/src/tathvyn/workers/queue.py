"""Asynchronous Job Queue Manager for Deep Research Tasks.

Provides distributed queue dispatching and state persistence with Redis
and bounded, LRU in-memory fallback.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import OrderedDict
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from tathvyn.api.schemas import (
    AsyncResearchJobResponse,
    ClaimVerificationResponse,
    ResearchJobStatusResponse,
)
from tathvyn.common.config import get_settings
from tathvyn.common.enums import ResearchDepth
from tathvyn.common.logging import get_logger
from tathvyn.storage.redis_client import get_redis_client

logger = get_logger("job_queue")

QUEUE_KEY = "tathvyn:queue:research_jobs"
JOB_PREFIX = "tathvyn:jobs:"
DEFAULT_JOB_TTL = 86400  # 24 hours
MAX_IN_MEMORY_JOBS = 500


class JobQueueManager:
    """Manages asynchronous research job lifecycle with Redis and resilient in-memory fallback."""

    def __init__(self, use_redis: bool | None = None) -> None:
        settings = get_settings()
        self.use_redis = use_redis if use_redis is not None else bool(settings.redis_url)
        self._in_memory_jobs: OrderedDict[UUID, dict[str, Any]] = OrderedDict()
        self._in_memory_queue: asyncio.Queue[UUID] = asyncio.Queue()
        self._redis_offline_until: float = 0.0

    def _job_key(self, job_id: UUID) -> str:
        return f"{JOB_PREFIX}{job_id}"

    async def enqueue_job(
        self,
        claim: str,
        depth: ResearchDepth = ResearchDepth.DEEP,
        base_url: str = "http://localhost:8000",
    ) -> AsyncResearchJobResponse:
        """Enqueue a new deep verification research task.

        Persists job metadata in Redis (or in-memory) and registers the task in the work queue.
        """
        job_id = uuid4()
        now = datetime.now(UTC)
        now_iso = now.isoformat()

        job_dict: dict[str, Any] = {
            "job_id": str(job_id),
            "status": "QUEUED",
            "claim": claim,
            "depth": depth.value if hasattr(depth, "value") else str(depth),
            "created_at": now_iso,
            "updated_at": now_iso,
            "result": None,
            "error": None,
        }

        # 1. Store in bounded in-memory state as local buffer/fallback
        if len(self._in_memory_jobs) >= MAX_IN_MEMORY_JOBS:
            self._in_memory_jobs.popitem(last=False)
        self._in_memory_jobs[job_id] = job_dict
        await self._in_memory_queue.put(job_id)

        # 2. Persist to Redis if available
        if self.use_redis and time.time() >= self._redis_offline_until:
            try:
                redis = get_redis_client()
                if redis is not None:
                    job_key = self._job_key(job_id)
                    await redis.set(job_key, json.dumps(job_dict), ex=DEFAULT_JOB_TTL)
                    await redis.lpush(QUEUE_KEY, str(job_id))
                    logger.debug("redis_job_enqueued", job_id=str(job_id))
            except Exception as e:
                self._redis_offline_until = time.time() + 60.0
                logger.warning("redis_enqueue_failed_fallback_to_memory", error=str(e), job_id=str(job_id))

        logger.info(
            "Enqueued asynchronous research job",
            job_id=str(job_id),
            claim=claim,
            depth=depth.value if hasattr(depth, "value") else str(depth),
        )

        return AsyncResearchJobResponse(
            job_id=job_id,
            status="QUEUED",
            claim=claim,
            depth=depth,
            created_at=now,
            polling_url=f"{base_url}/api/v1/research/{job_id}",
        )

    async def dequeue_job(self, timeout: float = 1.0) -> UUID | None:
        """Retrieve the next pending job ID from Redis or in-memory queue.

        Args:
            timeout: Maximum wait time in seconds.

        Returns:
            UUID of the job to process, or None if queue is empty.
        """
        # Try Redis first
        if self.use_redis and time.time() >= self._redis_offline_until:
            try:
                redis = get_redis_client()
                if redis is not None:
                    # RPOP from Redis list
                    raw_id = await redis.rpop(QUEUE_KEY)
                    if raw_id:
                        return UUID(raw_id)
            except Exception as e:
                self._redis_offline_until = time.time() + 60.0
                logger.warning("redis_dequeue_failed_fallback_to_memory", error=str(e))

        # In-memory queue fallback
        try:
            return await asyncio.wait_for(self._in_memory_queue.get(), timeout=timeout)
        except TimeoutError:
            return None

    async def get_job_status(self, job_id: UUID) -> ResearchJobStatusResponse | None:
        """Retrieve current execution status and result for a job."""
        # 1. Try Redis
        if self.use_redis and time.time() >= self._redis_offline_until:
            try:
                redis = get_redis_client()
                if redis is not None:
                    raw_val = await redis.get(self._job_key(job_id))
                    if raw_val:
                        data = json.loads(raw_val)
                        return self._dict_to_response(data)
            except Exception as e:
                self._redis_offline_until = time.time() + 60.0
                logger.debug("redis_get_job_failed_fallback_to_memory", error=str(e))

        # 2. In-Memory fallback
        data = self._in_memory_jobs.get(job_id)
        if not data:
            return None

        return self._dict_to_response(data)

    async def update_job_status(
        self,
        job_id: UUID,
        status: str,
        result: ClaimVerificationResponse | None = None,
        error: str | None = None,
    ) -> None:
        """Update job lifecycle status and attach result or error payload."""
        now = datetime.now(UTC).isoformat()
        serialized_result = result.model_dump(mode="json") if result else None

        # 1. Update in-memory cache
        if job_id in self._in_memory_jobs:
            self._in_memory_jobs[job_id]["status"] = status
            self._in_memory_jobs[job_id]["updated_at"] = now
            if serialized_result is not None:
                self._in_memory_jobs[job_id]["result"] = serialized_result
            if error is not None:
                self._in_memory_jobs[job_id]["error"] = error
            self._in_memory_jobs.move_to_end(job_id)

        # 2. Update Redis
        if self.use_redis and time.time() >= self._redis_offline_until:
            try:
                redis = get_redis_client()
                if redis is not None:
                    job_key = self._job_key(job_id)
                    raw_val = await redis.get(job_key)
                    if raw_val:
                        job_data = json.loads(raw_val)
                    else:
                        job_data = self._in_memory_jobs.get(job_id, {
                            "job_id": str(job_id),
                            "created_at": now,
                        })
                    job_data["status"] = status
                    job_data["updated_at"] = now
                    if serialized_result is not None:
                        job_data["result"] = serialized_result
                    if error is not None:
                        job_data["error"] = error
                    await redis.set(job_key, json.dumps(job_data), ex=DEFAULT_JOB_TTL)
            except Exception as e:
                self._redis_offline_until = time.time() + 60.0
                logger.warning("redis_update_job_failed", error=str(e), job_id=str(job_id))

        logger.info("Updated research job state", job_id=str(job_id), status=status)

    def _dict_to_response(self, data: dict[str, Any]) -> ResearchJobStatusResponse:
        """Convert serialized job dictionary to ResearchJobStatusResponse."""
        result_payload = None
        if data.get("result"):
            try:
                result_payload = ClaimVerificationResponse.model_validate(data["result"])
            except Exception:
                result_payload = data["result"]

        created_at = data["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data["updated_at"]
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return ResearchJobStatusResponse(
            job_id=UUID(str(data["job_id"])),
            status=data["status"],
            claim=data["claim"],
            depth=ResearchDepth(data["depth"]),
            created_at=created_at,
            updated_at=updated_at,
            result=result_payload,
            error=data.get("error"),
        )
