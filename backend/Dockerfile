# ==============================================================================
# Tathvyn Backend - Production Container for Google Cloud Run
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Dependency Resolution
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock README.md ./

ENV UV_COMPILE_BYTECODE=1
RUN uv sync --frozen --no-dev --no-install-project

# ------------------------------------------------------------------------------
# Stage 2: Production Runtime (Cloud Run Optimized)
# ------------------------------------------------------------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH"

COPY --chown=user:user . /app

# Cache dir for transformer model weights
RUN mkdir -p /home/user/.cache/huggingface && chown -R user:user /home/user/.cache

USER user
ENV HOME=/home/user \
    PORT=8080

# Cloud Run defaults to port 8080
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8080}/api/v1/health || exit 1

# Launch FastAPI server with Uvicorn
CMD ["sh", "-c", "python -m uvicorn tathvyn.api.app:create_app --factory --host 0.0.0.0 --port ${PORT:-8080}"]
