# ==============================================================================
# Tathvyn - Multi-Stage Production Dockerfile (Hugging Face & Cloud Ready)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build & Dependency Resolution
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast deterministic dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency manifests
COPY pyproject.toml uv.lock ./

# Install Python dependencies into virtual environment
ENV UV_COMPILE_BYTECODE=1
RUN uv sync --frozen --no-dev --no-install-project

# ------------------------------------------------------------------------------
# Stage 2: Production Runtime
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user (Hugging Face compatible user 1000)
RUN useradd -m -u 1000 user

# Copy installed virtual environment from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

# Copy application source code
COPY --chown=user:user . /app

# Create cache directory for ML models
RUN mkdir -p /home/user/.cache/huggingface && chown -R user:user /home/user/.cache

# Switch to non-root user
USER user
ENV HOME=/home/user \
    PORT=7860

# Expose default Hugging Face Spaces port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/api/v1/health || exit 1

# Launch FastAPI web server and UI on $PORT
CMD ["sh", "-c", "python -m uvicorn tathvyn.api.app:create_app --factory --host 0.0.0.0 --port ${PORT:-7860}"]
