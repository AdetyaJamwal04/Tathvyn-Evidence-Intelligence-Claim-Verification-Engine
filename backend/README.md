# Tathvyn Backend: Verification & Evidence Intelligence Engine

The backend of **Tathvyn** is a high-performance Python 3.12+ engine powered by FastAPI, DeBERTa NLI cross-encoders, and adaptive research graph orchestration.

---

## 🏛️ Directory Structure

```
backend/
├── src/tathvyn/
│   ├── api/              # FastAPI routers, middleware, rate limiting, schemas
│   ├── claims/           # Normalizer, clause decomposer, entity & temporal extractors
│   ├── common/           # Enums, Pydantic models, configurations, exceptions
│   ├── evidence/         # Evidence assessment, numerical & temporal validators
│   ├── models/           # CrossEncoder reranker, DeBERTa NLI, LLM fallback
│   ├── orchestration/    # Adaptive research graph, query formulator, degradation
│   ├── retrieval/        # Multi-tier search providers, HTML/PDF parsers, segmenter
│   │   ├── providers/
│   │   │   ├── tavily_provider.py        # Tavily Search API with basic depth & key stripping
│   │   │   ├── gemini_search_provider.py # Google Search Grounding via google-genai
│   │   │   ├── ddg_provider.py           # DuckDuckGo live web search fallback
│   │   │   ├── brave_provider.py         # Brave Search API provider
│   │   │   └── manager.py                # Multi-provider fallback manager
│   │   ├── fetcher.py    # Resilient async HTML/PDF document fetcher
│   │   ├── segmenter.py  # Overlapping sentence chunker
│   │   └── security.py   # SSRF protection & IP validation
│   ├── storage/          # Cache management & Redis connection pooling
│   ├── verdict/          # Epistemic aggregation, calibration, explainer
│   └── workers/          # Async job queue & background worker loop
├── scripts/              # CLI verification & benchmark runners
├── tests/                # 146 unit tests & 50-claim evaluation benchmark
├── Dockerfile            # Production Dockerfile for Cloud Run (pre-cached weights)
├── .gcloudignore         # Cloud Build optimization
├── pyproject.toml        # Hatchling build specification & dependencies
├── uv.lock               # Deterministic dependency lockfile
└── main.py               # Backend entrypoint (CLI & FastAPI server)
```

---

## 🚀 Running the Backend Locally

### 1. Install Dependencies
Using `uv`:
```powershell
uv sync --extra dev
```

### 2. Start the API Server
```powershell
uv run python main.py server --port 8000
```
Interactive Swagger docs: `http://127.0.0.1:8000/docs`

### 3. Run Tests
```powershell
uv run pytest tests/ -v
```
---

## 📈 Automated Benchmark Performance & Epistemic Calibration

Tathvyn includes an automated 50-claim seed benchmark suite evaluated across all 5 canonical epistemic verdict classes:

| Metric | Measured Value | Production Target | Status |
| :--- | :--- | :--- | :---: |
| **Overall Accuracy** | **86.0%** | $\ge 85.0\%$ | ✅ **PASS** |
| **Macro-F1 Score** | **83.3%** | $\ge 80.0\%$ | ✅ **PASS** |
| **Expected Calibration Error (ECE)** | **0.0599** | $\le 0.0800$ | ✅ **PASS** |
| **Brier Calibration Score** | **0.1457** | $\le 0.1500$ | ✅ **PASS** |
| **Decision Latency** | **~115 ms / claim** | $< 500	ext{ ms}$ | ✅ **PASS** |

Run the automated evaluation benchmark:
```powershell
uv run python scripts/run_benchmark.py --output-dir reports/
```


---

## ☁️ Production Deployment (Google Cloud Run)

The backend is deployed to **Google Cloud Run** in region `us-central1`:

```powershell
# 1. Build and push image with Cloud Build
gcloud builds submit backend --tag us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest

# 2. Deploy to Cloud Run
gcloud run deploy tathvyn-backend `
  --image us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest `
  --region us-central1 `
  --platform managed `
  --allow-unauthenticated `
  --memory 4Gi `
  --cpu 2 `
  --min-instances 1 `
  --set-env-vars "Tathvyn_ENVIRONMENT=production" `
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest,TAVILY_API_KEY=tavily-api-key:latest"
```

* **Live Cloud Run URL**: `https://tathvyn-backend-906432301218.us-central1.run.app`
* **Health Endpoint**: `/api/v1/health`


## 🩺 System Health & Readiness Endpoints

- GET /api/v1/health: Operational status and database/redis connectivity.
- GET /api/v1/health/live: Fast process liveness probe.
- GET /api/v1/health/ready: Deep dependency readiness probe verifying Redis and ML inference model status.
