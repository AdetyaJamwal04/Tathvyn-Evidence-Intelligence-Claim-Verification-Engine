# Tathvyn — Concrete Technology Stack Selection (Phase 0 / MVP)

## 1. Purpose

While Tathvyn remains model-agnostic and provider-agnostic by architectural design, building and benchmarking require concrete starting dependencies. 

This document locks the **concrete technology stack for Phase 0 and the initial MVP**. Every choice includes an architectural rationale and a clear "Revisit When" condition so changes can be managed via Architecture Decision Records (ADRs).

---

## 2. Core Stack Summary

| Layer / Component | Chosen Technology | Primary Alternative | Revisit When |
|---|---|---|---|
| **Runtime Language** | Python 3.12+ | Python 3.11 | Python 3.13 stability verified across all ML dependencies |
| **Web / API Framework** | FastAPI (ASGI / Uvicorn) | Litestar / Flask | Need specialized high-throughput C++ / Rust gateway |
| **Relational Database** | PostgreSQL 16 | SQLite (dev-only) | Relational queries become bottleneck at >10M records |
| **Vector Storage** | `pgvector` (PostgreSQL extension) | Qdrant / Milvus | Vector index operations exceed PG memory / latency limits |
| **Cache & Task Queue** | Redis (Key-value cache + Redis Streams) | RabbitMQ / Celery | Distributed multi-consumer event streaming requires Kafka |
| **Search Providers** | Tavily API (Primary) + Brave Search (Fallback) | Google Custom Search / Bing | Cost / rate limits or specialized scientific domains require Serper / Semantic Scholar |
| **NLI (Stance / Entailment)** | `microsoft/deberta-v3-large-mnli` (Local) | `roberta-large-mnli` / API LLM | Latency requires quantized `deberta-v3-base` or custom fine-tuned weights |
| **Dense Embeddings** | `BAAI/bge-small-en-v1.5` (Local) | `bge-large-en-v1.5` / `all-MiniLM-L6-v2` | Recall drop observed on verification benchmark suite |
| **Reranking** | `BAAI/bge-reranker-v2-m3` (Local Cross-Encoder) | `ms-marco-MiniLM-L-6-v2` | Inference latency exceeds latency budget under heavy load |
| **NER / Entity Extraction** | spaCy `en_core_web_trf` (Transformer) | `en_core_web_sm` / GLiNER | Memory constraints require smaller CNN model |
| **Reasoning LLM (Planning/Adjudication)** | Anthropic Claude 3.5 Sonnet / Opus (API) | OpenAI GPT-4o / Local LLaMA 3 70B | Cost per request exceeds target or offline air-gapped deployment required |
| **Data Validation & Settings** | Pydantic v2 + Pydantic Settings | attrs / dataclasses | Pydantic v2 is canonical standard for FastAPI |
| **Testing & Benchmarking** | `pytest`, `pytest-asyncio`, `pytest-benchmark` | unittest | Standard Python testing ecosystem |
| **Document Parsing** | `trafilatura` (HTML) + `pypdf` (PDF) | BeautifulSoup / unstructured | Document extraction failures exceed benchmark error threshold |
| **Containerization** | Docker (Multi-stage Python 3.12 slim images) | Distroless | Production deployment requirements dictate orchestration (K8s) |

---

## 3. Component Details & Rationale

### 3.1 Programming Language & Runtime
- **Selection**: Python 3.12
- **Rationale**: Optimal performance improvements over 3.10/3.11, excellent support for asynchronous I/O, native integration with PyTorch, Hugging Face Transformers, spaCy, and FastAPI.
- **Type Checking**: Strict typing enforced via `mypy` / `pyright`.

### 3.2 Web & Application Framework
- **Selection**: FastAPI with `uvicorn` / `gunicorn`
- **Rationale**: Native asynchronous support, automatic OpenAPI/Swagger documentation, deep integration with Pydantic v2 for request/response serialization, high developer productivity.

### 3.3 Primary Data Store & Vector Index
- **Selection**: PostgreSQL 16 with `pgvector`
- **Rationale**: Avoids premature infrastructure sprawl. Allows transactional metadata (claims, atomic claims, evidence snapshots, provenance graphs, verdicts) and passage vector embeddings to reside within the same ACID-compliant database.
- **Migration Tooling**: Alembic for versioned, reproducible schema migrations.

### 3.4 In-Memory Cache & Asynchronous Broker
- **Selection**: Redis 7.x
- **Rationale**: Low latency in-memory cache for search queries, document content hashes, passage embeddings, and normalized entity representations. Redis Streams provides lightweight, durable task queuing for asynchronous deep verification without heavyweight Celery or Kafka dependencies in early phases.

### 3.5 Information Retrieval (Search APIs)
- **Primary Provider**: Tavily Search API
  - *Rationale*: Built specifically for LLM/RAG workflows; provides clean text extraction, domain filtering, and topic-specific queries.
- **Secondary / Fallback Provider**: Brave Search API
  - *Rationale*: High index independence from Google/Bing, strong privacy guarantees, independent web crawl index.

### 3.6 Machine Learning Models (Local Inference)
- **Dense Retrieval**: `BAAI/bge-small-en-v1.5`
  - Runs efficiently on CPU/GPU, producing 384-dimensional dense vectors with leading benchmark scores on MTEB retrieval.
- **Cross-Encoder Reranker**: `BAAI/bge-reranker-v2-m3`
  - Jointly scores `(query, passage)` pairs to filter candidate evidence down to high-precision passages.
- **Natural Language Inference (NLI)**: `microsoft/deberta-v3-large-mnli`
  - State-of-the-art transformer for entailment, neutral, and contradiction classification over premise-hypothesis pairs.

### 3.7 LLM Reasoning Layer (API-Driven)
- **Primary Orchestrator & Explainer**: Anthropic Claude 3.5 Sonnet / Claude 3 Opus
  - *Rationale*: Superior complex reasoning, structured tool invocation, low hallucination rate, and strong nuanced reasoning for claim decomposition and conflict analysis.
- **Fallback Orchestrator**: OpenAI GPT-4o
  - *Rationale*: Redundant provider failover if Anthropic API suffers latency or availability outages.

---

## 4. Hardware & Deployment Requirements (Phase 0 / MVP)

### Minimum Local Development Machine:
- **OS**: Windows 11 / Linux (Ubuntu 22.04+) / macOS (Apple Silicon)
- **RAM**: 16 GB minimum (32 GB recommended for running local DeBERTa-large + BGE-reranker alongside Postgres & Redis)
- **GPU**: Optional for Phase 0 (CPU inference is fully supported via ONNX Runtime or standard PyTorch CPU; CUDA GPU accelerates reranking and NLI).
- **Disk**: 20 GB free space for model cache (`~/.cache/huggingface`) and PostgreSQL databases.

---

## 5. Decision Governance

Any modification to this selected stack MUST be accompanied by:
1. An Architecture Decision Record created under `docs/adr/` (following `00-adr-template.md`).
2. Empirical benchmark comparison demonstrating accuracy, latency, or cost benefits.
