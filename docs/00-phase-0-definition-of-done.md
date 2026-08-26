# Tathvyn — Phase 0: Definition of Done (Foundations)

## 1. Purpose

Phase 0 sets up the foundational repository structure, typing, domain models, configuration management, logging, database schemas, and baseline test harnesses. 

To prevent premature feature work before the scaffolding is rock-solid, this document establishes the **unambiguous, verifiable Definition of Done (DoD) for Phase 0**.

---

## 2. Phase 0 Deliverables Checklist

### 2.1 Repository & Environment
- [ ] Root directory layout strictly adheres to the canonical structure specified in `26-project-roadmap-and-implementation-order.md`.
- [ ] `pyproject.toml` configured with Python 3.12+, `ruff` (linter & formatter), `mypy` (strict type checking), and `pytest`.
- [ ] `README.md` in repository root with setup instructions, local development guide, and architecture overview.
- [ ] `.env.example` file specifying all environment variables (API keys, database URLs, model cache paths) without exposing real credentials.

### 2.2 Configuration Management
- [ ] `Tathvyn/common/config.py` implemented using `pydantic-settings`.
- [ ] Hierarchical configuration: default parameters, YAML override support, and environment variable overrides (`Tathvyn_*` prefix).
- [ ] Settings include typed configurations for:
  - Database & Redis connection parameters
  - Search provider keys & rate limits
  - Local model directory & device placement (`cpu`, `cuda`, `auto`)
  - LLM API credentials & timeout limits
  - Verification budget defaults (search call limits, token limits)

### 2.3 Canonical Domain Models
- [ ] Core domain objects implemented in `Tathvyn/common/models/` as typed Pydantic v2 schemas matching `00-canonical-enums.md`:
  - `Claim`, `AtomicClaim`, `ClaimType`, `Materiality`
  - `Source`, `Document`, `Passage`, `SourceType`, `AuthorityClass`
  - `Evidence`, `EvidenceRelationship`, `EvidenceState`, `EvidenceSnapshot`
  - `ProvenanceGroup`, `ProvenanceRelationship`
  - `Conflict`, `ConflictType`, `ConflictResolution`
  - `VerdictDecision`, `Verdict`, `PublicVerdict`
  - `ResearchTask`, `ResearchState`, `ResearchAction`
- [ ] All models include JSON schema serialization and deserialization validation tests.
- [ ] Domain models contain **zero third-party model inference dependencies** (pure business / data representations).

### 2.4 Abstract Provider Interfaces
- [ ] Abstract Base Classes (ABCs) created with strict type signatures:
  - `SearchProvider` (`Tathvyn/retrieval/interfaces.py`)
  - `DocumentFetcher` (`Tathvyn/retrieval/interfaces.py`)
  - `EmbeddingModel` (`Tathvyn/models/interfaces.py`)
  - `RerankerModel` (`Tathvyn/models/interfaces.py`)
  - `NLIModel` (`Tathvyn/models/interfaces.py`)
  - `ReasoningLLM` (`Tathvyn/orchestration/interfaces.py`)
- [ ] Mock / stub implementations for each interface to allow testing without live network or GPU resources.

### 2.5 Database & Storage Scaffolding
- [ ] SQLAlchemy 2.0 / SQLModel declarative schema models matching `23-data-schema-and-provenance.md`.
- [ ] Alembic migration environment initialized under `alembic/`.
- [ ] Initial migration script `001_initial_schema.py` creating:
  - `verification_requests`, `claims`, `atomic_claims`
  - `sources`, `documents`, `passages` (with `pgvector` embedding column)
  - `evidence`, `provenance_groups`, `conflicts`, `verdicts`
- [ ] Docker Compose file (`docker-compose.yml`) spinning up PostgreSQL 16 (with pgvector) and Redis 7.

### 2.6 Logging & Tracing Framework
- [ ] Structured JSON logging configured with correlation IDs (`request_id`, `verification_id`, `task_id`).
- [ ] Standardized log format capturing timestamps, log level, module name, and execution duration.
- [ ] Safe logging filter ensuring search API keys, bearer tokens, and sensitive document text are redacted.

### 2.7 Seed Benchmark & Test Harness
- [ ] `tests/benchmarks/data/benchmark_seed_v1.json` committed with the 50 annotated seed claims from `00-seed-benchmark.md`.
- [ ] `pytest` test suite configured with 100% passing tests for:
  - `tests/unit/test_domain_models.py`
  - `tests/unit/test_config.py`
  - `tests/unit/test_enum_consistency.py`
  - `tests/unit/test_mock_providers.py`
- [ ] Code formatting (`ruff format --check`) and type checking (`mypy Tathvyn`) pass with **zero errors and zero warnings**.

---

## 3. Phase 0 Verification Gate

Phase 0 is officially declared complete and Phase 1 (Claim Intelligence) may begin only when:
```bash
# Run formatting and linting
ruff check Tathvyn tests
ruff format --check Tathvyn tests

# Run strict type checking
mypy Tathvyn

# Run all unit tests
pytest tests/unit -v --cov=Tathvyn
```
All commands return exit code `0`.
