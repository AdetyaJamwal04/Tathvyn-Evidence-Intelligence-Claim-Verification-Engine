# Tathvyn Backend: Verification & Evidence Intelligence Engine

The backend of **Tathvyn** is a high-performance Python 3.12+ engine powered by FastAPI, DeBERTa NLI cross-encoders, and adaptive research graph orchestration.

---

## 📁 Directory Structure

```
backend/
├── src/tathvyn/
│   ├── api/              # FastAPI routers, middleware, rate limiting, schemas
│   ├── claims/           # Normalizer, clause decomposer, entity & temporal extractors
│   ├── common/           # Enums, Pydantic models, configurations, exceptions
│   ├── evidence/         # Evidence assessment, numerical & temporal validators
│   ├── models/           # CrossEncoder reranker, DeBERTa NLI, LLM fallback
│   ├── orchestration/    # Adaptive research graph, query formulator, degradation
│   ├── retrieval/        # Tavily & Brave providers, HTML/PDF parsers, segmenter
│   ├── storage/          # Cache management & Redis connection pooling
│   ├── verdict/          # Epistemic aggregation, calibration, explainer
│   └── workers/          # Async job queue & background worker loop
├── scripts/              # CLI verification & benchmark runners
├── tests/                # Unit test suite & 50-claim evaluation benchmark
├── pyproject.toml        # Hatchling build specification & dependencies
├── uv.lock               # Deterministic dependency lockfile
└── main.py               # Backend entrypoint (CLI & FastAPI server)
```

---

## 🚀 Running the Backend

### 1. Install Dependencies
Using `uv`:
```powershell
uv sync --extra dev
```

### 2. Start the API Server
```powershell
uv run python main.py server --host 127.0.0.1 --port 8000
```
- Interactive Docs: `http://127.0.0.1:8000/docs`
- Health Check: `http://127.0.0.1:8000/api/v1/health`

### 3. Verify a Claim via CLI
```powershell
uv run python main.py verify "The Pacific Ocean is the largest ocean on Earth."
```

### 4. Run the Test Suite
```powershell
uv run python -m pytest tests/unit/ -k "not test_llm"
```
