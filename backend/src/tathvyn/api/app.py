"""FastAPI Application Factory for VeriFact."""

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from tathvyn.api.middleware import setup_error_handlers
from tathvyn.api.rate_limiter import RateLimitMiddleware
from tathvyn.api.v1.routes import router as v1_router
from tathvyn.common.config import get_settings
from tathvyn.common.logging import get_logger
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.workers.queue import JobQueueManager

logger = get_logger("api_app")

MAX_BODY_SIZE = 64 * 1024  # 64 KB


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforces 64KB body cap on Content-Length and chunked transfer encodings."""

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_BODY_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request body too large. Maximum allowed size is 64KB."},
            )

        # For mutating requests with chunked transfer or omitted Content-Length
        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if len(body) > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large. Maximum allowed size is 64KB."},
                )

        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager handling startup and shutdown hooks."""
    import asyncio

    logger.info("Initializing Tathvyn API server")
    # Initialize shared singletons on app.state
    app.state.job_queue = JobQueueManager()
    app.state.research_engine = AdaptiveResearchEngine()

    async def _warmup() -> None:
        try:
            from tathvyn.models.nli import DeBERTaNLIModel
            from tathvyn.models.reranker import BGERerankerModel

            nli = DeBERTaNLIModel()
            await nli.predict_batch([("Warmup premise.", "Warmup hypothesis.")])
            reranker = BGERerankerModel()
            await reranker.rerank("Warmup query", [("p1", "Warmup passage")])
            logger.info("ML models successfully warmed up in background")
        except Exception as e:
            logger.warning("Model background warmup skipped or failed", error=str(e))

    warmup_task = asyncio.create_task(_warmup())
    yield
    if not warmup_task.done():
        warmup_task.cancel()
    logger.info("Shutting down Tathvyn API server")


def create_app() -> FastAPI:
    """Construct and configure the production FastAPI application."""
    settings = get_settings()

    # Disable interactive API docs in production to reduce attack surface
    _is_production = settings.environment == "production"

    app = FastAPI(
        title="Tathvyn API",
        description="Evidence-Grounded Automated Claim Verification & Adaptive Research Platform",
        version="1.0.0",
        docs_url=None if _is_production else "/docs",
        redoc_url=None if _is_production else "/redoc",
        openapi_url=None if _is_production else "/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration — restrict wildcard origins when credentials are enabled in production
    cors_origins = list(settings.cors_origins)
    if _is_production and "*" in cors_origins:
        logger.warning("Wildcard CORS origin disallowed in production with credentials; using domain whitelist")
        cors_origins = [o for o in cors_origins if o != "*"]
        if not cors_origins:
            cors_origins = [
                "https://tathvyn.web.app",
                "https://tathvyn-production.web.app",
                "https://tathvyn-production.firebaseapp.com",
            ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    # Register Rate Limiting Middleware
    app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

    # Register Body Size Cap Middleware
    app.add_middleware(BodySizeLimitMiddleware)

    # Register RFC-7807 Problem Details Error Handlers
    setup_error_handlers(app)

    # Mount API Routers
    app.include_router(v1_router)

    # Locate web UI directory across development, container, and wheel installs
    candidate_paths = [
        os.path.join(os.getcwd(), "frontend", "dist"),
        os.path.join(os.getcwd(), "frontend"),
        os.path.join(os.getcwd(), "..", "frontend", "dist"),
        os.path.join(os.getcwd(), "..", "frontend"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend", "dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "frontend")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend")),
        "/app/frontend/dist",
        "/app/frontend",
    ]
    web_dir = next((p for p in candidate_paths if os.path.isdir(p) and os.path.isfile(os.path.join(p, "index.html"))), None)
    if web_dir:
        app.mount("/", StaticFiles(directory=web_dir, html=True), name="web_ui")

    return app

