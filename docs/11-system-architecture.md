# Tathvyn — Production System Architecture

## 1. Purpose

This document translates the Tathvyn domain and ML architecture into a production-grade system architecture.

The system must support two objectives simultaneously:

### Scientific objective

Produce accurate, evidence-grounded verification results.

### Product objective

Serve potentially millions of users while maintaining:

```text
Reliability
Latency
Cost efficiency
Observability
Security
Maintainability
```

The architecture must therefore support a progression from:

```text
Single-machine prototype
        ↓
Modular application
        ↓
Distributed workers
        ↓
Autoscaled production system
```

without requiring a complete rewrite at every stage.

---

# 2. Architectural Principles

## Principle 1 — Separate Concerns

The system should separate:

```text
API
Research orchestration
Retrieval
Evidence processing
Model inference
Verdicting
Storage
Observability
```

---

## Principle 2 — Stateless Application Layer

API and orchestration services should be stateless where practical.

State should live in durable stores.

---

## Principle 3 — Expensive Work Is Asynchronous

Long-running research should not block a web request indefinitely.

The architecture should support:

```text
Synchronous quick verification
+
Asynchronous deep verification
```

---

## Principle 4 — Models Are Services or Managed Workers

Model inference should not be tightly coupled to the HTTP process as the system scales.

---

## Principle 5 — Evidence Is Durable

Retrieved evidence should be persisted sufficiently for:

- audit;
- reproducibility;
- debugging;
- caching;
- re-verification.

---

## Principle 6 — External Providers Are Untrusted Dependencies

Search APIs, web pages, and LLM APIs can fail or return malicious/incorrect content.

The system must isolate them.

---

## Principle 7 — Everything Expensive Is Measured

Every request should expose:

```text
Cost
Latency
Model usage
Search usage
Evidence volume
Cache behavior
```

---

# 3. High-Level Architecture

```text
                         ┌─────────────────────┐
                         │      Clients        │
                         │ Web / API / Mobile  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    API Gateway      │
                         │ Auth / Rate Limit   │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Verification API    │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
                    ▼                                ▼
          Quick Verification                 Deep Verification
                    │                                │
                    │                                ▼
                    │                      ┌──────────────────┐
                    │                      │ Research Queue   │
                    │                      └────────┬─────────┘
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │ Research Agent   │            │ Research Workers │
          └────────┬─────────┘            └────────┬─────────┘
                   │                               │
                   └──────────────┬────────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Retrieval Service   │
                       └──────────┬──────────┘
                                  │
                     ┌────────────┼─────────────┐
                     ▼            ▼             ▼
                 Search APIs   Web Fetch    Source APIs
                     │            │             │
                     └────────────┼─────────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Evidence Pipeline   │
                       └──────────┬──────────┘
                                  │
                       ┌──────────┼──────────┐
                       ▼          ▼          ▼
                   Reranker      NLI      Entity/Time
                       │          │          │
                       └──────────┼──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │   Evidence Graph    │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │   Verdict Engine    │
                       └──────────┬──────────┘
                                  ▼
                       ┌─────────────────────┐
                       │ Explanation Layer   │
                       └──────────┬──────────┘
                                  ▼
                              Response
```

---

# 4. Logical Components

The initial logical architecture consists of:

```text
API Gateway
Verification API
Research Orchestrator
Research Workers
Retrieval Service
Document Processing
Evidence Service
Model Inference Layer
Verdict Engine
Explanation Service
Cache
Transactional Database
Evidence Store
Vector Store
Object Storage
Queue
Observability Stack
```

These are logical boundaries.

They do not all need to be separate deployable services initially.

---

# 5. Deployment Philosophy

Do not begin with microservices merely because the final architecture may be distributed.

Initial deployment should be:

```text
Modular monolith
+
background workers
+
external search
+
local model runtime
```

This provides:

- low operational complexity;
- fast development;
- easy debugging;
- shared types;
- low infrastructure cost.

Services should be extracted when scale or ownership requires them.

---

# 6. Initial Prototype Architecture

A strong first production-oriented prototype:

```text
                  Client
                    │
                    ▼
              FastAPI / Flask
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Verification Flow     Background Worker
          │                   │
          └─────────┬─────────┘
                    ▼
             Research Core
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Search       Local ML      Storage
       │            │            │
       └────────────┼────────────┘
                    ▼
              Verdict Engine
```

The codebase should still have explicit module boundaries.

---

# 7. Request Types

The product should eventually support:

```text
QUICK
STANDARD
DEEP
```

### QUICK

Optimized for low latency.

### STANDARD

Balanced quality and cost.

### DEEP

Adaptive research with larger budgets.

These are policies over the same architecture.

---

# 8. Request Lifecycle

A request may follow:

```text
1. Receive
2. Validate
3. Normalize
4. Check cache
5. Classify
6. Select verification policy
7. Execute research
8. Aggregate evidence
9. Compute verdict
10. Generate explanation
11. Persist result
12. Return
```

---

# 9. Synchronous vs Asynchronous

## Synchronous

Appropriate when:

```text
Low research depth
Small evidence set
Predictable latency
```

Example:

```text
< 2–5 seconds target
```

The exact target must be benchmarked.

---

## Asynchronous

Appropriate when:

```text
Deep research
Many search calls
Large evidence sets
High model workload
Long-running document processing
```

The client receives:

```text
job_id
status
```

and can later retrieve the result.

---

# 10. Job Lifecycle

```text
QUEUED
  ↓
RUNNING
  ↓
RESEARCHING
  ↓
ASSESSING
  ↓
VERDICTING
  ↓
COMPLETED
```

Failure states:

```text
FAILED
CANCELLED
TIMEOUT
PARTIAL
```

---

# 11. Queue Architecture

A queue decouples API traffic from expensive processing.

Conceptually:

```text
API
 ↓
Queue
 ↓
Research Worker
 ↓
Model Workers
 ↓
Result Store
```

Potential technologies:

```text
Redis Streams
RabbitMQ
Kafka
SQS
Pub/Sub
```

The initial choice should depend on:

- throughput;
- delivery semantics;
- operational complexity;
- cloud environment.

---

# 12. Queue Selection Principle

Do not choose Kafka simply because it scales.

For an early product:

```text
Redis / SQS-class queue
```

may be sufficient.

Kafka becomes valuable when:

```text
very high throughput
+
event replay
+
multiple independent consumers
+
large event streams
```

justify it.

---

# 13. Task Queues

Potential queues:

```text
research_queue
document_fetch_queue
embedding_queue
rerank_queue
nli_queue
llm_queue
explanation_queue
```

Initially these can be logical queues implemented through one infrastructure system.

---

# 14. Backpressure

The system must prevent overload.

If:

```text
Incoming requests
>
Inference capacity
```

the queue grows.

The system should respond through:

```text
rate limiting
priority queues
request admission
budget reduction
autoscaling
graceful degradation
```

---

# 15. Priority Classes

Potential priority:

```text
P0 — Internal / critical
P1 — Paid / premium
P2 — Standard
P3 — Background
```

Priority should never bypass safety or resource limits.

---

# 16. API Layer

The API layer should handle:

```text
Authentication
Authorization
Validation
Rate limiting
Request IDs
Idempotency
Response formatting
```

It should not perform long-running ML inference directly.

---

# 17. API Contract

Conceptual endpoint:

```http
POST /v1/verifications
```

Request:

```json
{
  "claim": "India's GDP grew by 8.2% in 2024.",
  "mode": "STANDARD"
}
```

Response:

```json
{
  "verification_id": "ver_123",
  "status": "PROCESSING"
}
```

For quick requests:

```json
{
  "verification_id": "ver_123",
  "status": "COMPLETED",
  "verdict": "SUPPORTED"
}
```

---

# 18. Idempotency

Clients may retry requests.

The API should support:

```text
Idempotency-Key
```

Repeated requests with the same key should not create duplicate expensive research jobs.

---

# 19. Request Deduplication

Semantic duplicate claims may also be detected.

Example:

```text
"Did India grow 8.2% in 2024?"

"Was India's 2024 GDP growth 8.2%?"
```

Potentially share research state if:

```text
claim equivalence
+
freshness requirements
+
policy compatibility
```

are satisfied.

---

# 20. Transactional Database

A relational database is appropriate for structured state.

Potential technology:

```text
PostgreSQL
```

It can store:

```text
requests
claims
atomic claims
research tasks
verdicts
model metadata
policies
users
usage
```

A relational store provides strong consistency for transactional state.

---

# 21. Evidence Storage

Evidence has different access patterns from transactional state.

Potential storage:

```text
PostgreSQL
+
Object Storage
+
Vector Database
```

The exact split should depend on workload.

---

# 22. Object Storage

Large documents should generally not be stored directly in relational rows.

Object storage can hold:

```text
raw documents
cleaned documents
snapshots
large extracted content
evaluation datasets
model artifacts
```

Potential technologies:

```text
S3-compatible storage
```

---

# 23. Vector Storage

Vector search may be implemented through:

```text
pgvector
Qdrant
OpenSearch
Elasticsearch
FAISS
```

Initial recommendation:

```text
PostgreSQL + pgvector
```

can reduce infrastructure complexity.

A dedicated vector database can be introduced if scale or workload requires it.

---

# 24. Cache Architecture

Multiple cache layers:

```text
L1 — in-process
L2 — Redis
L3 — durable storage
```

Potential cache objects:

```text
Search results
Documents
Embeddings
Reranker results
NLI results
Research state
Final verification results
```

---

# 25. Cache Invalidation

Caching is particularly difficult for fact verification.

A cache must consider:

```text
TTL
Claim type
Evidence freshness
Source modification
Policy version
Model version
Research mode
```

For current claims:

```text
short TTL
```

For historical claims:

```text
longer TTL
```

---

# 26. Search Cache

Search results may be cached using:

```text
normalized_query
provider
parameters
timestamp
```

The system should retain the retrieval timestamp.

---

# 27. Document Cache

Documents can be cached using:

```text
canonical_url
content_hash
retrieval_timestamp
```

If the document changes, the content hash changes.

---

# 28. Embedding Cache

Embeddings can be keyed by:

```text
content_hash
+
embedding_model_version
```

This allows model upgrades without incorrectly reusing old embeddings.

---

# 29. NLI Cache

NLI results can be keyed by:

```text
atomic_claim_hash
+
passage_hash
+
nli_model_version
```

---

# 30. Verdict Cache

A final verdict can only be reused if:

```text
claim equivalence
+
evidence freshness
+
research policy
+
model versions
+
aggregation policy
```

remain compatible.

---

# 31. Storage Architecture

Conceptually:

```text
                  PostgreSQL
              ┌───────────────┐
              │ Requests      │
              │ Claims        │
              │ Tasks         │
              │ Verdicts      │
              └───────┬───────┘
                      │
              ┌───────┴───────┐
              ▼               ▼
          pgvector        Object Store
              │               │
              │               ├── Documents
              │               ├── Snapshots
              │               └── Datasets
              │
              ▼
          Embeddings
```

---

# 32. Evidence Graph Storage

The evidence graph can initially be represented relationally.

Example:

```text
claims
atomic_claims
documents
passages
evidence
sources
provenance_groups
evidence_relationships
```

A graph database should only be introduced if graph traversal becomes a demonstrated bottleneck.

---

# 33. Why Not Start With Neo4j?

A graph database may look natural for provenance.

However:

```text
Graph data
```

does not automatically imply:

```text
Graph database.
```

PostgreSQL can represent many graph relationships efficiently at initial scale.

Introduce a graph database only if:

```text
complex traversal
+
large graph
+
measured performance requirement
```

justify it.

---

# 34. Document Processing

Document processing should be isolated from the API.

Pipeline:

```text
Fetch
 ↓
Validate
 ↓
Parse
 ↓
Clean
 ↓
Extract metadata
 ↓
Segment
 ↓
Fingerprint
 ↓
Store
```

---

# 35. Web Fetching

Fetch workers should enforce:

```text
timeout
maximum bytes
redirect limit
content-type restrictions
robots / provider policies
rate limits
```

The fetcher must not execute arbitrary page scripts.

---

# 36. Extraction

Extraction should support:

```text
HTML
PDF
JSON
CSV
XML
Plain text
```

Different extraction methods should be selected based on content type.

---

# 37. Content Snapshotting

When evidence is used in a verdict, the system should preserve enough information to reproduce the evidence state.

Possible representation:

```text
content_hash
passage_text
retrieval_timestamp
source_url
document_metadata
```

Full snapshots may be subject to copyright, storage, and legal constraints.

The storage policy should be carefully defined.

---

# 38. Model Inference Layer

Inference workers should expose stable interfaces.

Example:

```text
EmbeddingService
RerankerService
NLIService
EntityService
ReasoningService
```

Each service can evolve independently.

---

# 39. Initial Inference Architecture

For development:

```text
Single Python process
+
model registry
+
batched local inference
```

For scale:

```text
API
 ↓
Inference Queue
 ↓
Dedicated Worker
 ↓
Model Runtime
```

---

# 40. Model Worker Scaling

Workers can scale independently.

Example:

```text
Embedding:
10 workers

NLI:
4 workers

Reranker:
6 workers

LLM:
API-based / separate pool
```

Actual ratios should be driven by workload profiling.

---

# 41. GPU Scheduling

If GPUs are used:

```text
GPU pool
 ↓
model workers
```

Possible strategies:

```text
one model per GPU
multiple lightweight models per GPU
dynamic batching
model multiplexing
```

Memory fragmentation and model loading time must be measured.

---

# 42. Autoscaling

Scale based on:

```text
queue depth
request rate
GPU utilization
CPU utilization
latency
in-flight tasks
```

Queue depth is often a better signal than CPU utilization for asynchronous research.

---

# 43. Horizontal Scaling

Stateless services should scale horizontally:

```text
API x N
Research Workers x N
Document Workers x N
Model Workers x N
```

Durable state remains external.

---

# 44. Vertical Scaling

Vertical scaling may be useful for:

```text
GPU inference
large-memory embedding
reranking
NLI
```

The architecture should support both horizontal and vertical scaling.

---

# 45. Reliability

Important reliability mechanisms:

```text
timeouts
retries
circuit breakers
bulkheads
idempotency
dead-letter queues
health checks
graceful degradation
```

---

# 46. Retry Policy

Not all errors should be retried.

### Retryable

```text
network timeout
temporary provider error
transient worker failure
rate limit with retry-after
```

### Non-retryable

```text
invalid input
authentication failure
unsupported content
malformed request
```

Retries must have limits.

---

# 47. Dead-Letter Queue

Failed jobs after retry exhaustion should enter:

```text
Dead Letter Queue
```

This enables:

- debugging;
- manual inspection;
- replay.

A DLQ prevents silent data loss.

---

# 48. Circuit Breaker

External providers should have circuit breakers.

Example:

```text
Search Provider A
    ↓
Repeated failures
    ↓
Circuit OPEN
    ↓
Use Provider B
```

After a recovery period:

```text
HALF_OPEN
```

tests whether the provider has recovered.

---

# 49. Graceful Degradation

The system should continue operating with reduced capabilities.

Example:

```text
LLM unavailable
→ deterministic query generation

Primary search unavailable
→ fallback search

Reranker unavailable
→ embedding + lexical ranking

NLI unavailable
→ conservative evidence state
```

Degradation must never silently increase confidence.

---

# 50. Observability

The system requires three layers:

```text
Metrics
Logs
Traces
```

---

# 51. Metrics

Track:

```text
Request rate
Error rate
Latency
Queue depth
Search calls
Documents fetched
Evidence count
Model latency
Model errors
Cache hit rate
Cost
Verdict distribution
Abstention rate
```

---

# 52. Tracing

Each verification should have a trace:

```text
verification_id
    │
    ├── claim understanding
    ├── query generation
    ├── search
    ├── document fetch
    ├── embedding
    ├── reranking
    ├── NLI
    ├── research iteration
    ├── verdict
    └── explanation
```

Distributed tracing should use a standard such as OpenTelemetry.

---

# 53. Structured Logging

Logs should include:

```text
timestamp
request_id
verification_id
component
event
latency
status
error_code
model_version
provider
```

Do not log raw user content by default.

---

# 54. Cost Observability

Every request should accumulate:

```text
search_cost
llm_cost
compute_cost_estimate
storage_cost_estimate
total_estimated_cost
```

This is necessary for product-scale economics.

---

# 55. Quality Observability

Production monitoring should eventually include:

```text
user corrections
human review outcomes
benchmark drift
citation failures
abstention rate
source diversity
contradiction rate
```

Accuracy cannot be inferred from latency and uptime alone.

---

# 56. Health Checks

### Liveness

Is the process running?

### Readiness

Can the service accept traffic?

### Dependency health

Are:

```text
database
queue
search providers
model workers
cache
```

available?

---

# 57. Security Architecture

Security boundaries:

```text
Client
 ↓
API Gateway
 ↓
Application
 ↓
Workers
 ↓
External Web
```

Retrieved web content should never be allowed to access internal services.

---

# 58. SSRF Protection

Document fetching creates SSRF risk.

The fetcher should restrict:

```text
private IP ranges
localhost
internal DNS
metadata endpoints
unsafe protocols
```

Redirects must be revalidated.

---

# 59. Resource Exhaustion Protection

Limit:

```text
request body size
document size
PDF size
HTML size
redirect count
search results
model input tokens
research iterations
```

---

# 60. Authentication and Authorization

The product should eventually support:

```text
API keys
OAuth
JWT
service-to-service identity
role-based access
```

Internal services should authenticate with each other.

---

# 61. Rate Limiting

Rate limits should exist at:

```text
IP
user
API key
organization
endpoint
verification mode
```

Deep research should have stricter limits than quick verification.

---

# 62. Multi-Tenancy

At scale:

```text
Tenant
 ↓
Quota
 ↓
Budget
 ↓
Requests
```

Tenant-level isolation should apply to:

```text
usage
billing
rate limits
stored results
```

---

# 63. Data Retention

The system should define retention for:

```text
raw requests
documents
evidence
traces
logs
verdicts
usage data
```

Retention should consider:

```text
privacy
storage cost
audit requirements
legal obligations
```

---

# 64. Privacy

Do not unnecessarily store:

```text
user identity
raw personal information
sensitive claim text
```

Where possible:

```text
minimize
redact
encrypt
expire
```

---

# 65. Encryption

Use:

```text
TLS in transit
encryption at rest
secret management
key rotation
```

API keys must never be stored in source code.

---

# 66. Secret Management

Secrets include:

```text
search provider keys
LLM keys
database credentials
cloud credentials
```

Use:

```text
environment secret injection
secret manager
```

rather than repository files.

---

# 67. Deployment

A practical production path:

```text
Containerized services
        ↓
Cloud compute
        ↓
Managed database
        ↓
Managed object storage
        ↓
Managed queue
        ↓
Monitoring
```

The exact cloud provider should not be hard-coded into the architecture.

---

# 68. Containerization

Each deployable unit should have:

```text
immutable image
version
health check
resource limits
configuration
```

Images should be scanned for vulnerabilities.

---

# 69. CI/CD

Pipeline:

```text
Commit
 ↓
Lint
 ↓
Unit Tests
 ↓
Integration Tests
 ↓
Model Tests
 ↓
Security Scan
 ↓
Build Image
 ↓
Deploy Staging
 ↓
Smoke Tests
 ↓
Production
```

---

# 70. Model CI

Model changes should trigger:

```text
benchmark suite
regression suite
latency test
memory test
calibration test
adversarial test
```

A model should not reach production merely because the service still starts.

---

# 71. Data Versioning

Evaluation datasets and benchmark data should be versioned.

Example:

```text
dataset_v1
dataset_v2
```

Every model result should identify the dataset version used for evaluation.

---

# 72. Configuration Versioning

Version:

```text
research policy
retrieval policy
verdict policy
model routing policy
cost policy
```

Configuration changes can materially change verification behavior.

---

# 73. Feature Flags

Use feature flags for:

```text
new model
new reranker
new search provider
new verdict policy
new research strategy
```

This enables gradual rollout.

---

# 74. Canary Deployment

For model or policy changes:

```text
1% traffic
 ↓
monitor
 ↓
5%
 ↓
25%
 ↓
50%
 ↓
100%
```

Rollback should be automatic when quality or reliability metrics breach thresholds.

---

# 75. Disaster Recovery

Important backups:

```text
database
research metadata
configuration
evaluation datasets
critical evidence metadata
```

Recovery objectives should define:

```text
RPO
RTO
```

---

# 76. Multi-Region Evolution

At very large scale:

```text
Global Router
   ├── Region A
   ├── Region B
   └── Region C
```

Regional services may maintain:

```text
API
workers
cache
database replicas
model infrastructure
```

Global evidence storage and consistency require careful design.

Do not introduce multi-region complexity before it is necessary.

---

# 77. Global Search Considerations

Search providers may have:

```text
regional latency
regional availability
different legal requirements
different indexing
```

Provider routing can eventually account for region.

---

# 78. Million-User Architecture

At very large scale:

```text
                   Global Traffic
                         │
                         ▼
                   API Gateway
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         Region A               Region B
              │                     │
       ┌──────┴──────┐       ┌──────┴──────┐
       ▼             ▼       ▼             ▼
     API          Workers   API          Workers
       │             │       │             │
       └──────┬──────┘       └──────┬──────┘
              ▼                     ▼
          Regional Cache        Regional Cache
              │                     │
              └──────────┬──────────┘
                         ▼
                Durable Data Layer
```

This is a future architecture, not the initial deployment.

---

# 79. Capacity Planning

Capacity should be modeled using:

```text
Requests/sec
Average research depth
Average documents/request
Average model inferences/request
Average tokens/request
Average latency
Peak traffic
```

For example:

\[
InferenceLoad =
Requests/sec
\times
Inferences/request
\]

This determines model worker capacity.

---

# 80. Queueing Model

The system should monitor:

```text
arrival rate λ
service rate μ
concurrency N
```

If:

\[
\lambda \geq N\mu
\]

the queue will grow without bound.

Autoscaling and admission control must keep utilization below sustainable capacity.

---

# 81. Cost Model

Approximate verification cost:

\[
C_{verification}
=
C_{search}
+
C_{fetch}
+
C_{embedding}
+
C_{rerank}
+
C_{NLI}
+
C_{LLM}
+
C_{storage}
\]

The system should track actual measurements rather than relying only on theoretical estimates.

---

# 82. Quality-Cost Frontier

The product should continuously evaluate:

```text
Accuracy
vs
Cost
vs
Latency
```

Example operating points:

```text
FAST
$0.00X / request
1.5 sec
92% benchmark accuracy

STANDARD
$0.0X / request
4 sec
95%

DEEP
$0.X / request
15 sec
97%
```

These numbers are illustrative only.

The real values must come from benchmarks.

---

# 83. Admission Control

If the system is overloaded:

```text
Reject
Queue
Degrade
or
Reduce research depth
```

The system should avoid accepting unlimited deep-research work.

---

# 84. Graceful Degradation Modes

Potential fallback hierarchy:

```text
DEEP
 ↓
STANDARD
 ↓
FAST
 ↓
UNVERIFIED
```

If resource availability becomes constrained, the system may reduce research depth while explicitly recording the degraded policy.

---

# 85. Reliability Target

The product should eventually define SLOs for:

```text
API availability
Verification completion
Latency
Queue delay
Model availability
Search availability
```

The initial prototype should measure these before committing to aggressive targets.

---

# 86. System Failure Taxonomy

Initial failures:

```text
API_FAILURE
QUEUE_FAILURE
DATABASE_FAILURE
CACHE_FAILURE
SEARCH_PROVIDER_FAILURE
FETCH_FAILURE
MODEL_FAILURE
RESOURCE_EXHAUSTION
TIMEOUT
DATA_CORRUPTION
CONFIGURATION_ERROR
SECURITY_EVENT
```

Operational failures must remain distinct from verification failures.

---

# 87. System-Level Verification Trace

A complete trace should connect:

```text
Request
 ↓
Research Plan
 ↓
Task
 ↓
Tool
 ↓
Search
 ↓
Document
 ↓
Passage
 ↓
Evidence
 ↓
Model Assessment
 ↓
Evidence Graph
 ↓
Verdict
 ↓
Explanation
```

Every important transition should have an identifier.

---

# 88. Distributed Correlation IDs

Use:

```text
request_id
verification_id
job_id
task_id
trace_id
span_id
```

These allow a single verification to be reconstructed across services.

---

# 89. API Versioning

Use:

```text
/v1/...
/v2/...
```

rather than breaking existing clients.

Schema evolution should be backward-compatible where practical.

---

# 90. Service Boundaries

A future decomposition may look like:

```text
gateway-service
verification-service
research-service
retrieval-service
document-service
evidence-service
model-service
verdict-service
explanation-service
```

But initial deployment can keep several of these in one application.

---

# 91. Domain Boundary Rule

Extract a service when one or more are true:

```text
Independent scaling required
Independent deployment required
Different runtime required
Different ownership required
Strong fault isolation required
```

Do not extract services simply to make architecture diagrams larger.

---

# 92. Initial Repository Architecture

A practical codebase:

```text
Tathvyn/
├── api/
├── domain/
├── application/
├── research/
├── retrieval/
├── evidence/
├── verdict/
├── models/
├── storage/
├── workers/
├── policies/
├── observability/
├── security/
└── tests/
```

This provides service-like boundaries without deployment complexity.

---

# 93. Dependency Direction

Prefer:

```text
API
 ↓
Application
 ↓
Domain
```

Infrastructure should implement domain/application interfaces rather than the domain depending directly on infrastructure.

Example:

```text
Domain
  ↓
SearchProvider interface

Infrastructure
  ↓
TavilyProvider
BraveProvider
...
```

---

# 94. Hexagonal Architecture

The core can follow:

```text
                External World
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    Search        Database       Model
    Adapter        Adapter       Adapter
       │             │             │
       └─────────────┼─────────────┘
                     ▼
              Application Core
                     │
                  Domain
```

This makes infrastructure replaceable.

---

# 95. Event-Driven Evolution

Important events may eventually include:

```text
VerificationRequested
ResearchStarted
EvidenceDiscovered
ConflictDetected
ResearchCompleted
VerdictGenerated
VerificationFailed
```

Events can support:

- analytics;
- replay;
- asynchronous processing;
- audit;
- downstream consumers.

---

# 96. Event Idempotency

Consumers must safely handle duplicate events.

Each event should include:

```text
event_id
aggregate_id
event_type
timestamp
version
```

---

# 97. Audit Trail

A verification audit trail should retain:

```text
claim
policy
research actions
evidence IDs
source IDs
model versions
verdict
timestamp
```

This is particularly important for research-grade evaluation.

---

# 98. Reproducibility Boundary

Perfect reproduction of the live web is impossible.

Therefore reproducibility should target:

```text
Evidence snapshot
+
metadata
+
model versions
+
policy versions
+
decision logic
```

rather than assuming the original web page will remain unchanged.

---

# 99. System Architecture Invariants

### INV-SA-001

API services should remain stateless where practical.

### INV-SA-002

Long-running research must be asynchronously executable.

### INV-SA-003

Expensive inference must be measurable.

### INV-SA-004

External provider failure must not become an epistemic conclusion.

### INV-SA-005

Retrieved web content must be isolated from internal control flow.

### INV-SA-006

Evidence used for verdicts must remain traceable.

### INV-SA-007

Model versions and policy versions must be recorded.

### INV-SA-008

All asynchronous jobs must be idempotent.

### INV-SA-009

System overload must trigger backpressure or graceful degradation.

### INV-SA-010

Microservices should be introduced only when justified by scale or isolation requirements.

---

# 100. Recommended Evolution Path

## Phase 0 — Research Prototype

```text
Single machine
Flask/FastAPI
PostgreSQL
Local models
External search
```

Goal:

```text
Validate verification quality
```

---

## Phase 1 — Production-Oriented Prototype

```text
API
+
Worker
+
PostgreSQL
+
Redis
+
Object storage
```

Goal:

```text
Reliability
Observability
Caching
```

---

## Phase 2 — Scale-Out

```text
API cluster
Research workers
Document workers
Model workers
Managed database
```

Goal:

```text
Horizontal scaling
```

---

## Phase 3 — Specialized Inference

```text
Embedding workers
Reranker workers
NLI workers
Reasoning service
```

Goal:

```text
Independent model scaling
```

---

## Phase 4 — Large-Scale Platform

```text
Multi-region
Autoscaling
Advanced routing
Dedicated vector infrastructure
Advanced provenance graph
Learned research policy
```

Goal:

```text
Millions of users
```

---

# 101. What "Millions of Users" Actually Means

User count alone is not a capacity metric.

The meaningful variables are:

```text
Daily active users
Requests/user/day
Peak requests/sec
Deep-verification percentage
Average research depth
Average model workload
Average document volume
```

For example:

```text
1,000,000 users
×
1 verification/day
=
1,000,000 verifications/day
```

But:

```text
1,000,000 users
×
10 verifications/day
=
10,000,000 verifications/day
```

These are completely different infrastructure problems.

---

# 102. Scale Assumption

The architecture should therefore be parameterized by:

```text
RPS
Concurrency
Verification depth
Evidence volume
Model inference volume
```

rather than marketing user counts.

---

# 103. Final System Architecture Principle

> **Build the first version as a modular, observable system that can evolve into distributed infrastructure without prematurely paying the complexity cost of distributed infrastructure.**

The production architecture should scale the expensive components independently while keeping the domain and verification logic stable.

---

# 104. Next Step

The next document should be:

**`12-data-architecture.md`**

It will define the data layer in detail:

- PostgreSQL schema strategy;
- evidence storage;
- document storage;
- vector storage;
- provenance representation;
- cache design;
- indexing;
- data lifecycle;
- retention;
- consistency;
- migrations;
- partitioning;
- archival;
- and how the data architecture supports both verification quality and million-user scale.
