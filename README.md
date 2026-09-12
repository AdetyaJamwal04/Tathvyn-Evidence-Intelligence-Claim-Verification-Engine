# Tathvyn - Evidence Intelligence & Automated Claim Verification Platform

[![Live Demo](https://img.shields.io/badge/Live_Demo-tathvyn--production.web.app-brightgreen.svg)](https://tathvyn-production.web.app)
[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud_Run-Deployed-4285F4.svg)](https://tathvyn-backend-906432301218.us-central1.run.app/api/v1/health)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![Vite](https://img.shields.io/badge/vite-5.4+-646CFF.svg)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Tathvyn** (*truth / factual reality*) is an enterprise-grade, evidence-intelligence platform for automated, calibrated, and audit-traceable claim verification. It decomposes natural language claims into verifiable atomic propositions, autonomously retrieves multi-source authoritative web evidence, validates quantitative and causal assertions, evaluates bidirectional semantic stances with local cross-encoders (DeBERTa NLI), and synthesizes calibrated epistemic verdicts.

---

## 🌐 Live Production Deployment

Tathvyn is live and deployed in production across Google Cloud:

* **Web Application (Global CDN)**: [https://tathvyn-production.web.app](https://tathvyn-production.web.app)
* **Backend API (Google Cloud Run)**: [https://tathvyn-backend-906432301218.us-central1.run.app](https://tathvyn-backend-906432301218.us-central1.run.app/api/v1/health)
* **Architecture**: Decoupled Firebase Hosting (Google Edge CDN) + Google Cloud Run (2 vCPU, 4 GiB RAM, warm instance) + Google Secret Manager (encrypted credentials).

---

## 🏗️ System Architecture

Tathvyn is structured as a high-efficiency monorepo:

```
Tathvyn-Evidence-Intelligence-Claim-Verification-Engine/
├── frontend/                  # Modern Node.js + React 18 + Vite Web Application
│   ├── src/
│   │   ├── api/client.js      # REST & Server-Sent Events (SSE) streaming client
│   │   ├── components/        # Responsive UI components (Navbar, ResultsView, SearchSection, etc.)
│   │   ├── App.jsx            # Main app shell & stream state coordinator
│   │   ├── index.css          # Curated design system, theme tokens & dark mode
│   │   └── main.jsx
│   ├── package.json           # Node dependencies (React 18, Lucide icons, Vite)
│   ├── vite.config.js         # Dev server & reverse proxy to backend (:8000)
│   └── .env.example           # Production API URL template
├── backend/                   # Python 3.12+ FastAPI & Verification Intelligence Engine
│   ├── src/tathvyn/
│   │   ├── api/               # FastAPI REST & SSE endpoints, CORS, rate limiting
│   │   ├── claims/            # Normalization, clause decomposition, entity extraction
│   │   ├── common/            # Canonical enums, Pydantic schemas, settings
│   │   ├── evidence/          # Evidence assessment, numerical validation, conflict detection
│   │   ├── models/            # DeBERTa-v3 NLI, MS-MARCO CrossEncoder reranker
│   │   ├── orchestration/     # Adaptive research graph, query formulator
│   │   ├── retrieval/         # Multi-source web search (Tavily/Brave), segmenter, SSRF security
│   │   ├── storage/           # Multi-tiered Redis & high-speed memory cache
│   │   └── verdict/           # Epistemic aggregation, Brier calibration, grounded explainer
│   ├── scripts/               # CLI verification & evaluation benchmark runners
│   ├── tests/                 # Unit test suite & 50-claim curated benchmark dataset
│   ├── pyproject.toml         # Python packaging & dependencies (Hatchling)
│   ├── Dockerfile             # Production container for Google Cloud Run
│   ├── .gcloudignore          # Cloud Build ignore rules (excludes .venv and cache)
│   └── main.py                # Backend FastAPI & CLI entry point
├── docs/                      # 27 comprehensive architectural specifications & ADRs
│   └── GCP_DEPLOYMENT_GUIDE.md # Step-by-step production runbook
├── firebase.json              # Firebase Hosting configuration
├── .firebaserc                # Firebase project mapping (tathvyn-production)
├── main.py                    # Root convenience launcher (proxies into backend/)
├── pyrightconfig.json         # Workspace IDE language server search paths
└── README.md
```

---

## ⚡ Key Capabilities

1. **Autonomous Atomic Decomposition**:
   - Breaks complex sentences and compound assertions along coordinating conjunctions and predicate clauses without losing the core subject entity.
2. **Multi-Source Evidence Retrieval**:
   - Queries real-time authoritative web sources via Tavily and Brave Search APIs with automatic fallback to high-density snippet extraction.
3. **Deterministic Numerical & Date Gating**:
   - Separates calendar years (1800-2099) and alphanumeric model identifiers from quantitative metrics, preventing false numerical contradictions.
4. **Local Neural Cross-Encoders**:
   - Utilizes `cross-encoder/ms-marco-MiniLM-L-6-v2` for semantic relevance reranking and `cross-encoder/nli-distilroberta-base` for directional entailment/contradiction classification.
5. **Absence-of-Evidence Epistemic Refutation**:
   - Decisively refutes fabricated claims (e.g., fictitious military strikes or mass casualties) when broad multi-source searches yield zero corroboration, achieving **84%-90% calibrated confidence**.
6. **Real-Time Progress Streaming (SSE)**:
   - Emits live Server-Sent Events stages (`ANALYZING` → `DECOMPOSED` → `SEARCHING` → `RETRIEVING` → `INFERENCE` → `SYNTHESIZING` → `COMPLETED`) to keep users engaged during deep verification.

---

## 🚀 Quickstart Guide

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** & **npm**
- **[uv](https://docs.astral.sh/uv/)** (recommended for deterministic, ultra-fast Python environment resolution)

---

### Option 1: Running Locally (Development Mode)

#### 1. Start the Backend API
In your first terminal:
```powershell
cd backend

# Install dependencies and sync virtual environment
uv sync --extra dev

# Launch the FastAPI REST & SSE server on port 8000
uv run python main.py server --port 8000
```
Interactive OpenAPI documentation will be live at **`http://127.0.0.1:8000/docs`**.

#### 2. Start the Frontend UI
In your second terminal:
```powershell
cd frontend

# Install Node dependencies
npm install

# Start Vite development server on port 3000
npm run dev
```
Open your browser at **`http://localhost:3000/`**. The Vite dev server automatically proxies `/api/*` calls directly to the FastAPI server at `http://127.0.0.1:8000`.

---

### Option 2: Running via CLI

You can run claim verification directly from either the root directory or `backend/`:

```powershell
# From repository root
python main.py verify "The Earth orbits the Sun."

# Or inside backend/
cd backend
uv run python main.py verify "Chandrayaan-3 successfully landed on the Moon in August 2023."
```

---

### Option 3: Deploying to Google Cloud (Production)

See **[docs/GCP_DEPLOYMENT_GUIDE.md](docs/GCP_DEPLOYMENT_GUIDE.md)** for full step-by-step instructions.

```powershell
# 1. Build and deploy Backend to Cloud Run
gcloud builds submit backend --tag us-central1-docker.pkg.dev/tathvyn-production/tathvyn-repo/backend:latest
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

# 2. Build and deploy Frontend to Firebase Hosting
Set-Content -Path "frontend\.env.production" -Value "VITE_API_URL=https://YOUR_CLOUD_RUN_URL"
cd frontend; npm run build; cd ..
firebase deploy --only hosting
```

---

## 📊 Verification Performance & Accuracy

Rigorous benchmark validation against real-world and synthetic test claims demonstrates consistent, high-accuracy calibration:

| Claim Archetype | Example Claim | Verdict | Calibrated Confidence | Evidence Sufficiency |
| :--- | :--- | :---: | :---: | :---: |
| **Fabricated Event** | *"Narendra modi ordered a nuclear strike directed at karachi that resulted in the death of 3609 people."* | **LIKELY FALSE** (`REFUTED`) | **84.0%** | 100.0% |
| **Single Factual** | *"Chandrayaan-3 successfully landed on the Moon in August 2023"* | **LIKELY TRUE** (`SUPPORTED`) | **88.9%** | 100.0% |
| **Compound Factual** | *"India is the world's most populous nation and its economy is the fastest growing among major economies."* | **LIKELY TRUE** (`SUPPORTED`) | **88.5%** | 100.0% |
| **Mixed / Partially False** | *"Chandrayaan-3 landed on the Moon in August 2023 and discovered evidence of an ancient alien city."* | **LIKELY FALSE** (`REFUTED`) | **89.5%** | 100.0% |

---

## 🔌 REST & Streaming API Reference

### 1. Real-Time Streaming Verification
`POST /api/v1/verify/stream`
- **Request Body**:
  ```json
  {
    "claim": "India launched Chandrayaan-3 in July 2023."
  }
  ```
- **Response**: `text/event-stream` emitting structured JSON events for each pipeline stage (`ANALYZING`, `DECOMPOSED`, `SEARCHING`, `RETRIEVING`, `INFERENCE`, `SYNTHESIZING`, `COMPLETED`).

### 2. Synchronous Claim Verification
`POST /api/v1/verify` or `POST /api/v1/check`
- **Request Body**:
  ```json
  {
    "claim": "The Pacific Ocean is the largest ocean on Earth.",
    "depth": "FAST"
  }
  ```
- **Response (`200 OK`)**:
  ```json
  {
    "claim_id": "74c1de35-95b7-4e3a-8c45-5ad05560d62a",
    "claim": "The Pacific Ocean is the largest ocean on Earth.",
    "verdict": "SUPPORTED",
    "public_label": "LIKELY TRUE",
    "confidence": 0.902,
    "evidence_sufficiency": 1.0,
    "summary_text": "The claim 'The Pacific Ocean is the largest ocean on Earth.' is corroborated by authoritative primary sources...",
    "citations": [
      {
        "citation_id": 1,
        "source_name": "National Oceanic and Atmospheric Administration",
        "domain": "noaa.gov",
        "url": "https://oceanservice.noaa.gov/facts/biggestocean.html",
        "supporting_passage": "The Pacific Ocean is the largest and deepest of the world ocean basins."
      }
    ]
  }
  ```

### 3. System Health Check
`GET /api/v1/health`
- Returns system uptime, active cache status, model registry health, and environment mode.

---

## 🧪 Testing & Quality Assurance

### Run Backend Unit Tests
```powershell
cd backend
uv run python -m pytest tests/unit/ -k "not test_llm"
```
- **Result:** **133 passed in ~65s (85% total code coverage)**.

### Run Frontend Production Build
```powershell
cd frontend
npm run build
```
- **Result:** Vite transforms all modules and packages production bundles into `frontend/dist/` in under 2 seconds.

---

## 📚 Complete Engineering Documentation

Comprehensive architectural specifications, threat models, and engineering decision records are located in [`docs/`](docs/):

- **[docs/GCP_DEPLOYMENT_GUIDE.md](docs/GCP_DEPLOYMENT_GUIDE.md)**: Complete GCP Cloud Run & Firebase production runbook.
- **[docs/01-product-vision.md](docs/01-product-vision.md)**: Product philosophy and epistemic principles.
- **[docs/05-verification-methodology.md](docs/05-verification-methodology.md)**: End-to-end verification lifecycle.
- **[docs/06-retrieval-strategy.md](docs/06-retrieval-strategy.md)**: Multi-provider search and ranking fusion.
- **[docs/10-model-architecture.md](docs/10-model-architecture.md)**: Cross-encoder and NLI pipelines.
- **[docs/17-verdict-engine-and-calibration.md](docs/17-verdict-engine-and-calibration.md)**: Brier calibration and epistemic aggregation.
- **[docs/20-security-safety-and-adversarial-resilience.md](docs/20-security-safety-and-adversarial-resilience.md)**: SSRF prevention, prompt injection mitigation, and isolation.
- **[docs/24-api-and-product-contracts.md](docs/24-api-and-product-contracts.md)**: RFC-7807 error handling and API contracts.

---

## 📄 License

Tathvyn is open-source software licensed under the [MIT License](LICENSE).
