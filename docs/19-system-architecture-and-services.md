# Tathvyn — System Architecture and Services Specification

## 1. Purpose & Architectural Overview

This document specifies the technical system architecture for Tathvyn. It defines:
1. The **Modular Monolith** core package structure for early phases (Phase 0–Phase 4).
2. The **Asynchronous Worker & Queue Topology** for scaling deep verification workloads.
3. The **Service Boundaries & Extraction Path** for evolving into distributed services.
4. The **Data Flow & Inter-Module Communication Contracts**.

The guiding principle is:
> **Maintain strict logical boundaries and typed interfaces in code, allowing high-performance in-process execution early, while enabling zero-rewrite extraction into distributed microservices when throughput demands it.**

---

## 2. Canonical Modular Monolith Package Structure

All backend application code resides within the `Tathvyn` namespace package. Cyclic dependencies between modules are strictly forbidden and enforced via CI linting rules.

```text
Tathvyn/
├── __init__.py
├── main.py                                  # FastAPI application entrypoint & lifespan manager
│
├── api/                                     # HTTP / REST Presentation Layer
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── router.py                        # Root API v1 router
│   │   ├── verifications.py                 # POST /check, POST /research, GET /status
│   │   ├── evidence.py                      # GET /evidence, GET /graph
│   │   ├── health.py                        # GET /health, GET /readiness
│   │   └── admin.py                         # Evaluation & metrics endpoints
│   ├── middleware/
│   │   ├── logging.py                       # Structured request/response logging & trace IDs
│   │   ├── rate_limit.py                    # Redis token-bucket rate limiter
│   │   ├── auth.py                          # API key & tenant authentication
│   │   └── error_handler.py                 # Global exception translation to RFC-7807 JSON
│   └── schemas/                             # Pydantic v2 API Request / Response schemas
│       ├── requests.py
│       ├── responses.py
│       └── errors.py
│
├── claims/                                  # Claim Intelligence Subsystem
│   ├── __init__.py
│   ├── classifier.py                        # Multi-label claim classification
│   ├── decomposer.py                        # Atomic proposition decomposition & validation
│   ├── normalizer.py                        # Linguistic normalization & framing removal
│   ├── language.py                          # Fast language detection & English-only gate
│   ├── entity_extractor.py                  # spaCy NER & entity disambiguation
│   └── temporal_extractor.py                # Regex & semantic date/interval normalization
│
├── orchestration/                           # Research Control Plane
│   ├── __init__.py
│   ├── controller.py                        # Research state machine & loop runner
│   ├── planner.py                           # Initial research plan generation
│   ├── action_selector.py                   # EIG action selection optimization
│   ├── sufficiency_gate.py                  # Multi-dimensional stopping criteria evaluator
│   ├── budget_manager.py                    # Resource accounting & hard limit enforcement
│   └── trace.py                             # Immutable research execution trace logger
│
├── retrieval/                               # Evidence Acquisition Layer
│   ├── __init__.py
│   ├── interfaces.py                        # Abstract SearchProvider & DocumentFetcher ABCs
│   ├── router.py                            # Provider routing & failover manager
│   ├── query_generator.py                   # Support, contradiction & primary query synthesis
│   ├── fetcher.py                           # Async HTTP document downloader with SSRF protection
│   ├── parser.py                            # Trafilatura HTML & PyPDF text extractor
│   ├── passage_segmenter.py                 # Sliding-window & semantic passage chunker
│   └── providers/
│       ├── tavily.py                        # Tavily Search API implementation
│       ├── brave.py                         # Brave Search API implementation
│       └── mock.py                          # Deterministic test search provider
│
├── evidence/                                # Evidence Engineering & Graph Construction
│   ├── __init__.py
│   ├── stance_assessor.py                   # NLI model wrapper & stance classification
│   ├── numerical_evaluator.py               # Deterministic unit/metric/percentage validator
│   ├── temporal_evaluator.py                # Temporal validity interval checker
│   ├── source_scorer.py                     # Domain authority & primary source scoring
│   ├── provenance_engine.py                 # URL clustering & exact-quote duplicate detector
│   ├── conflict_detector.py                 # Direct & nuanced disagreement classifier
│   └── graph_builder.py                     # In-memory typed EvidenceGraph constructor
│
├── verdict/                                 # Decision & Calibration Layer
│   ├── __init__.py
│   ├── atomic_engine.py                     # Individual atomic claim verdict evaluator
│   ├── parent_aggregator.py                 # Materiality-weighted parent claim aggregator
│   ├── calibrator.py                        # Temperature scaling & isotonic confidence calibrator
│   ├── abstention_gate.py                   # Uncertainty ceiling & abstention enforcer
│   └── explainer.py                         # Traceable summary & citation generator
│
├── models/                                  # Local Machine Learning Runtime & Registry
│   ├── __init__.py
│   ├── registry.py                          # Model lifecycle & warm-up manager
│   ├── interfaces.py                        # ABCs for Embedding, Reranker, NLI
│   ├── embedding_service.py                 # BGE-small embedding runner
│   ├── reranker_service.py                  # BGE-reranker cross-encoder runner
│   ├── nli_service.py                       # DeBERTa-v3 NLI inference runner
│   └── llm_gateway.py                       # Anthropic / OpenAI client with retries
│
├── storage/                                 # Persistence & Data Access Layer
│   ├── __init__.py
│   ├── database.py                          # SQLAlchemy engine & async session factory
│   ├── redis_client.py                      # Redis connection pool & cache wrapper
│   ├── repositories/                        # Repository pattern data access objects
│   │   ├── claims_repo.py
│   │   ├── evidence_repo.py
│   │   ├── verdicts_repo.py
│   │   └── snapshots_repo.py
│   └── models/                              # SQLAlchemy ORM database table definitions
│       ├── request_orm.py
│       ├── claim_orm.py
│       ├── evidence_orm.py
│       └── verdict_orm.py
│
└── common/                                  # Cross-Cutting Core Utilities
    ├── __init__.py
    ├── config.py                            # Pydantic-settings configuration
    ├── enums.py                             # Python Enums matching 00-canonical-enums.md
    ├── models/                              # Core domain Pydantic schemas
    │   ├── claim.py
    │   ├── evidence.py
    │   ├── verdict.py
    │   └── research.py
    ├── exceptions.py                        # Typed domain exception hierarchy
    └── logging.py                           # Structlog JSON logger configuration
```

---

## 3. Asynchronous Worker & Queue Topology

While synchronous verification (`FAST` mode) executes inline within the API request lifecycle (< 3.0s), deep verification and heavy background workloads are processed asynchronously via **Redis Streams**:

```text
                               ┌─────────────────────────┐
                               │   Client (HTTP / REST)  │
                               └────────────┬────────────┘
                                            │
                                            ▼
                               ┌─────────────────────────┐
                               │    FastAPI API Server   │
                               └──────┬───────────┬──────┘
                                      │           │
                     Sync Path (<3s)  │           │ Async Path (Deep / Batch)
                                      ▼           ▼
                      ┌──────────────────┐    ┌─────────────────────────┐
                      │ Inline Fast Path │    │   Enqueues Job Payload  │
                      └──────────────────┘    └───────────┬─────────────┘
                                                          │
                                                          ▼
                                              ┌───────────────────────┐
                                              │ Redis Stream:         │
                                              │ 'Tathvyn:deep_queue' │
                                              └───────────┬───────────┘
                                                          │
                                 ┌────────────────────────┼────────────────────────┐
                                 │ Consumer Group:        │ Consumer Group:        │
                                 │ 'research-workers'     │ 'research-workers'     │
                                 ▼                        ▼                        ▼
                      ┌────────────────────┐   ┌────────────────────┐   ┌────────────────────┐
                      │ Research Worker #1 │   │ Research Worker #2 │   │ Research Worker #N │
                      └─────────┬──────────┘   └─────────┬──────────┘   └─────────┬──────────┘
                                │                        │                        │
                                └────────────────────────┼────────────────────────┘
                                                         │
                                                         ▼
                                            ┌─────────────────────────┐
                                            │ PostgreSQL 16 Database  │
                                            │ Updates status & result │
                                            └─────────────────────────┘
```

### Worker Lifecycle Contract

```python
class ResearchWorker:
    def __init__(self, worker_id: str, redis_pool: Redis, db_session: AsyncSession):
        self.worker_id = worker_id
        self.redis = redis_pool
        self.db = db_session
        self.is_running = False

    async def start(self):
        self.is_running = True
        logger.info("Worker started", worker_id=self.worker_id)
        while self.is_running:
            # Block for new job from Redis Stream (XREADGROUP)
            entries = await self.redis.xreadgroup(
                groupname="research-workers",
                consumername=self.worker_id,
                streams={"Tathvyn:deep_queue": ">"},
                count=1,
                block=2000
            )
            if not entries:
                continue
                
            stream, messages = entries[0]
            for message_id, job_data in messages:
                try:
                    await self.process_job(job_data)
                    await self.redis.xack(stream, "research-workers", message_id)
                except Exception as e:
                    logger.error("Job processing failed", job_id=job_data.get("job_id"), error=str(e))
                    await self.handle_job_failure(stream, message_id, job_data, e)
```

---

## 4. Subsystem Interfaces and Communication Contracts

### 4.1 Claim Intelligence $\rightarrow$ Research Orchestrator
```python
async def decompose_and_analyze(raw_claim: str, config: VerificationConfig) -> ClaimAnalysis:
    """
    1. Runs fast language detection (rejects non-English).
    2. Classifies multi-label claim types (NUMERICAL, TEMPORAL, etc.).
    3. Normalizes text and extracts named entities and temporal constraints.
    4. Decomposes compound claims into AtomicClaim list (or 1-element list if atomic).
    """
```

### 4.2 Research Orchestrator $\rightarrow$ Retrieval Subsystem
```python
async def execute_search(
    queries: list[GeneratedQuery], 
    budget: RemainingBudget
) -> list[CandidateDocument]:
    """
    1. Routes queries to primary provider (Tavily), falling back to Brave on error.
    2. Enforces per-domain and per-query rate limits.
    3. Downloads and parses main text content with SSRF filters.
    4. Splits text into passages and computes passage embeddings.
    """
```

### 4.3 Evidence Subsystem $\rightarrow$ Verdict Engine
```python
def evaluate_evidence_graph(
    claim: Claim, 
    graph: EvidenceGraph, 
    policy: VerificationPolicy
) -> VerdictDecision:
    """
    1. Assesses passage-to-claim stance via local DeBERTa NLI.
    2. Runs deterministic numerical & temporal interval checks.
    3. Clusters evidence into independent provenance groups.
    4. Aggregates atomic results with materiality weights.
    5. Applies calibrated confidence and abstention thresholds.
    """
```

---

## 5. Persistence Tier Architecture

Tathvyn strictly separates **metadata & relational entities** from **raw document text** and **vector embeddings**:

| Data Type | Target Storage System | Lifecycle & Eviction Policy |
|---|---|---|
| Claims, Atomic Claims, Tasks, Verdicts | **PostgreSQL (ACID Tables)** | Permanent append-only audit trail; immutable after verification completion |
| Passage Dense Vector Embeddings (384-d) | **PostgreSQL (`pgvector` Extension)** | Indexed via `HNSW` (Cosine metric); retained with document passage lifecycle |
| Raw Downloaded HTML / Full Document Text | **Object Storage (S3 / Local FS)** | Retention: 90 days for audit/debugging; evictable under storage pressure |
| Search Result & Embedding Cache | **Redis Key-Value Cache** | TTL: 1 hr (current events) to 30 days (historical facts); LRU eviction |
| Job Queues & Worker Locks | **Redis Streams & Redis Redlock** | Auto-acknowledged and trimmed via `XTRIM` (max 10,000 entries) |

---

## 6. Service Extraction Roadmap (Future Distributed Evolution)

When traffic exceeds **500 requests per second**, the modular monolith separates cleanly into three autonomous microservices:

```text
┌─────────────────────────┐     gRPC      ┌─────────────────────────┐
│   Tathvyn API Gateway  │ ────────────> │ Claim & Research Agent  │
│   (Auth, Routing, Rate) │               │ (Orchestrator Service)  │
└─────────────────────────┘               └───────────┬─────────────┘
                                                      │
                                                      │ gRPC / Queue
                                                      ▼
                                          ┌─────────────────────────┐
                                          │ ML Inference & Verdict  │
                                          │ (Triton Model Server)   │
                                          └─────────────────────────┘
```

Because all internal interfaces are typed Pydantic/dataclass contracts, transitioning from in-process function calls to gRPC / Protocol Buffers requires zero changes to core domain logic.
