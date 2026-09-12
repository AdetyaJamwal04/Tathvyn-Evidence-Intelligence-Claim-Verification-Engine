"""FastAPI Application Factory for VeriFact."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tathvyn.api.middleware import setup_error_handlers
from tathvyn.api.v1.routes import router as v1_router
from tathvyn.common.config import get_settings
from tathvyn.common.logging import get_logger
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.workers.queue import JobQueueManager

logger = get_logger("api_app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager handling startup and shutdown hooks."""
    logger.info("Initializing Tathvyn API server")
    # Initialize shared singletons on app.state
    app.state.job_queue = JobQueueManager()
    app.state.research_engine = AdaptiveResearchEngine()
    yield
    logger.info("Shutting down Tathvyn API server")


def create_app() -> FastAPI:
    """Construct and configure the production FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Tathvyn API",
        description="Evidence-Grounded Automated Claim Verification & Adaptive Research Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Rate Limiting Middleware
    from tathvyn.api.rate_limiter import RateLimitMiddleware

    app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

    # Register RFC-7807 Problem Details Error Handlers
    setup_error_handlers(app)

    # Mount API Routers
    app.include_router(v1_router)

    # Mount Web Dashboard (HTML5 SPA)
    import os

    from fastapi.staticfiles import StaticFiles

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
