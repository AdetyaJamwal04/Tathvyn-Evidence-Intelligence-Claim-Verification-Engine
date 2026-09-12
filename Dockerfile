# ==============================================================================
# Tathvyn - Multi-Stage Production Dockerfile (Node Frontend + Python Backend)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Frontend Build (Node.js & Vite)
# ------------------------------------------------------------------------------
FROM node:20-slim AS frontend-builder

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Python Backend Build & Dependency Resolution
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

# Copy dependency manifests from backend/
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./backend/

# Install Python dependencies into virtual environment
ENV UV_COMPILE_BYTECODE=1
RUN cd backend && uv sync --frozen --no-dev --no-install-project

# ------------------------------------------------------------------------------
# Stage 3: Production Runtime
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
COPY --from=builder /app/backend/.venv /app/backend/.venv
ENV PATH="/app/backend/.venv/bin:$PATH" \
    PYTHONPATH="/app/backend/src:$PYTHONPATH"

# Copy backend application source code
COPY --chown=user:user backend /app/backend

# Copy compiled production frontend from frontend-builder
COPY --from=frontend-builder --chown=user:user /frontend/dist /app/frontend/dist

# Create cache directory for ML models
RUN mkdir -p /home/user/.cache/huggingface && chown -R user:user /home/user/.cache

# Switch to non-root user
USER user
ENV HOME=/home/user \
    PORT=7860

# Expose default port
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:${PORT:-7860}/api/v1/health || exit 1

# Launch FastAPI server
CMD ["sh", "-c", "python -m uvicorn tathvyn.api.app:create_app --factory --host 0.0.0.0 --port ${PORT:-7860}"]
