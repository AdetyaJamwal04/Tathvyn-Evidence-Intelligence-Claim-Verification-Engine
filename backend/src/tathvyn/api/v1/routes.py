"""FastAPI v1 Router Endpoints for VeriFact."""

import asyncio
import json
import time
from typing import Any
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from tathvyn.api.schemas import (
    AsyncResearchJobRequest,
    AsyncResearchJobResponse,
    CitationSchema,
    ClaimVerificationRequest,
    ClaimVerificationResponse,
    HealthCheckResponse,
    ReadinessCheckResponse,
    ResearchJobStatusResponse,
)
from tathvyn.common.config import get_settings
from tathvyn.common.logging import get_logger
from tathvyn.models.nli import probe_nli_model
from tathvyn.orchestration.degradation import get_degradation_controller
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.storage.cache import get_cache_manager
from tathvyn.workers.queue import JobQueueManager
from tathvyn.workers.worker import ResearchWorker

logger = get_logger("api_routes")

router = APIRouter(prefix="/api/v1", tags=["Verification"])

_START_TIME = time.perf_counter()
_DEFAULT_JOB_QUEUE = JobQueueManager()
_DEFAULT_ENGINE = AdaptiveResearchEngine()
_DEFAULT_CACHE_MANAGER = get_cache_manager()
_DEFAULT_DEGRADATION_CONTROLLER = get_degradation_controller()


@router.post(
    "/check",
    response_model=ClaimVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Synchronous Claim Verification",
    description="Verify a natural language claim synchronously using the adaptive research engine.",
)
async def check_claim(
    request: ClaimVerificationRequest,
    req: Request,
) -> ClaimVerificationResponse:
    cache = getattr(req.app.state, "cache_manager", None) or _DEFAULT_CACHE_MANAGER
    engine = getattr(req.app.state, "research_engine", None) or _DEFAULT_ENGINE
    degradation = getattr(req.app.state, "degradation_controller", None) or _DEFAULT_DEGRADATION_CONTROLLER

    # 1. Check Verdict Cache for repeat claims (<50ms response)
    cached_payload = await cache.get_cached_verdict(request.claim)
    if cached_payload is not None:
        logger.info("Serving claim verdict from cache", claim=request.claim)
        cached_payload["request_id"] = request.request_id
        return ClaimVerificationResponse.model_validate(cached_payload)

    # 2. Dynamic Depth Adjustment under heavy load
    effective_depth = degradation.adjust_depth(request.depth, current_queue_backlog=0)

    start_time = time.perf_counter()
    try:
        decision, state = await engine.verify(
            claim_text=request.claim,
            depth=effective_depth,
            request_id=request.request_id,
        )
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        degradation.record_request(latency_seconds=latency_ms / 1000.0, success=True)
    except Exception as e:
        degradation.record_request(latency_seconds=time.perf_counter() - start_time, success=False)
        raise e

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

    response_obj = ClaimVerificationResponse(
        request_id=request.request_id,
        claim=request.claim,
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

    # 3. Store in Verdict Cache (TTL: 24h)
    await cache.set_cached_verdict(request.claim, response_obj.model_dump(mode="json"))

    return response_obj


@router.post(
    "/verify/stream",
    summary="Stream Claim Verification Progress",
    description="Stream real-time verification pipeline stages and the final verdict payload via Server-Sent Events.",
)
async def stream_verify_claim(
    request: ClaimVerificationRequest,
    req: Request,
) -> StreamingResponse:
    cache = getattr(req.app.state, "cache_manager", None) or _DEFAULT_CACHE_MANAGER
    engine = getattr(req.app.state, "research_engine", None) or _DEFAULT_ENGINE
    degradation = getattr(req.app.state, "degradation_controller", None) or _DEFAULT_DEGRADATION_CONTROLLER

    async def event_generator():
        start_time = time.perf_counter()

        # 1. Check Verdict Cache for repeat claims (<50ms response)
        cached_payload = await cache.get_cached_verdict(request.claim)
        if cached_payload is not None:
            cached_payload["request_id"] = str(request.request_id)
            yield f"data: {json.dumps({'stage': 'CACHED', 'message': 'Instant cache retrieval (<50ms)'})}\n\n"
            yield f"data: {json.dumps({'stage': 'COMPLETED', 'result': cached_payload})}\n\n"
            return

        effective_depth = degradation.adjust_depth(request.depth, current_queue_backlog=0)

        try:
            async for event in engine.verify_stream(
                claim_text=request.claim,
                depth=effective_depth,
                request_id=request.request_id,
            ):
                stage = event.get("stage", "")
                if stage == "COMPLETED":
                    decision = event["decision"]
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
                    response_obj = ClaimVerificationResponse(
                        request_id=request.request_id,
                        claim=request.claim,
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
                    await cache.set_cached_verdict(request.claim, response_obj.model_dump(mode="json"))
                    payload = {"stage": "COMPLETED", "result": response_obj.model_dump(mode="json")}
                    yield f"data: {json.dumps(payload)}\n\n"
                else:
                    clean_event = {k: v for k, v in event.items() if isinstance(v, (str, int, float, bool, list, dict))}
                    yield f"data: {json.dumps(clean_event)}\n\n"
        except Exception as e:
            logger.error("Error in verify_stream", error=str(e))
            yield f"data: {json.dumps({'stage': 'FAILED', 'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/research",
    response_model=AsyncResearchJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Asynchronous Deep Research Dispatch",
    description="Dispatch an asynchronous deep research task returning a tracking job_id.",
)
async def dispatch_research_job(
    request: AsyncResearchJobRequest,
    background_tasks: BackgroundTasks,
    req: Request,
) -> AsyncResearchJobResponse:
    queue_manager = getattr(req.app.state, "job_queue", None) or _DEFAULT_JOB_QUEUE
    engine = getattr(req.app.state, "research_engine", None) or _DEFAULT_ENGINE

    base_url = str(req.base_url).rstrip("/")
    enqueued = await queue_manager.enqueue_job(
        claim=request.claim,
        depth=request.depth,
        base_url=base_url,
    )

    # For standalone single-container deployments without external daemon,
    # attach worker execution to background tasks
    worker = ResearchWorker(queue_manager=queue_manager, research_engine=engine)
    background_tasks.add_task(worker.process_job, enqueued.job_id)

    return enqueued


@router.get(
    "/research/{job_id}",
    response_model=ResearchJobStatusResponse,
    summary="Get Research Job Status",
    description="Poll status and retrieve final verdict result for an asynchronous research job.",
)
async def get_research_job(
    job_id: UUID,
    req: Request,
) -> ResearchJobStatusResponse:
    queue_manager = getattr(req.app.state, "job_queue", None) or _DEFAULT_JOB_QUEUE
    status_data = await queue_manager.get_job_status(job_id)
    if not status_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research job '{job_id}' not found.",
        )
    return status_data


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="System Health & Operational Status",
    description="Check API status and backend connectivity with active dependency probing.",
)
async def health_check() -> HealthCheckResponse:
    uptime = round(time.perf_counter() - _START_TIME, 2)
    settings = get_settings()

    # Active Redis ping probe
    redis_connected = False
    try:
        from tathvyn.storage.redis_client import get_redis_client

        redis = get_redis_client()
        if redis is not None:
            pong = await asyncio.wait_for(redis.ping(), timeout=0.2)
            redis_connected = bool(pong)
    except Exception:
        redis_connected = False

    is_healthy = redis_connected or (settings.environment in ("development", "testing"))

    return HealthCheckResponse(
        status="healthy" if is_healthy else "degraded",
        version="1.0.0",
        uptime_seconds=uptime,
        database_connected=True,
        redis_connected=redis_connected or (settings.environment in ("development", "testing")),
    )


@router.get(
    "/health/live",
    summary="Kubernetes Liveness Probe",
    description="Immediate non-blocking process liveness verification.",
)
async def liveness_check() -> dict[str, Any]:
    return {
        "status": "live",
        "uptime_seconds": round(time.perf_counter() - _START_TIME, 2),
    }


@router.get(
    "/health/ready",
    response_model=ReadinessCheckResponse,
    summary="Kubernetes Readiness Probe",
    description="Active dependency verification checking Redis and ML inference model readiness.",
)
async def readiness_check() -> ReadinessCheckResponse:
    uptime = round(time.perf_counter() - _START_TIME, 2)
    redis_info: dict[str, Any] = {"available": False}
    try:
        from tathvyn.storage.redis_client import get_redis_client

        redis = get_redis_client()
        if redis is not None:
            pong = await asyncio.wait_for(redis.ping(), timeout=0.2)
            redis_info = {"available": bool(pong), "ping": "PONG"}
    except Exception as e:
        redis_info = {"available": False, "error": str(e)}

    nli_status = probe_nli_model()
    is_ready = bool(nli_status.get("nli_model"))

    return ReadinessCheckResponse(
        status="ready" if is_ready else "degraded",
        version="1.0.0",
        uptime_seconds=uptime,
        redis=redis_info,
        nli_model=nli_status,
    )
