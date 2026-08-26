# Tathvyn — Data Architecture

## 1. Purpose

This document defines the data architecture of Tathvyn.

The data layer must support two fundamentally different requirements:

### Verification quality

The system must preserve enough structured information to answer:

- What claim was checked?
- What atomic claims were derived?
- What evidence was found?
- Where did the evidence originate?
- When was it retrieved?
- Which sources are independent?
- Which models evaluated it?
- Why did the system reach its verdict?

### Product scale

The system must efficiently support:

```text
High request volume
Large document volume
Large evidence volume
Frequent model inference
Caching
Analytics
Re-verification
Auditing
```

The architecture therefore separates:

```text
Transactional state
Evidence state
Document content
Vector representations
Cache state
Analytics
```

---

# 2. Data Architecture Principles

## Principle 1 — Evidence Is First-Class Data

Evidence should not exist only inside logs or transient Python objects.

It must have a persistent identity.

---

## Principle 2 — Provenance Is First-Class

Every evidence item must be traceable to:

```text
source
document
passage
retrieval event
timestamp
```

---

## Principle 3 — Separate Content From Metadata

Large content should not unnecessarily live inside transactional tables.

Use:

```text
Metadata → PostgreSQL

Large content → Object storage

Vectors → Vector index
```

---

## Principle 4 — Immutable Evidence Records

Once evidence contributes to a completed verification, the core evidence record should be treated as append-oriented.

Corrections should create new versions rather than silently mutating historical evidence.

---

## Principle 5 — Version Everything That Changes Decisions

At minimum:

```text
Model version
Policy version
Evidence assessment version
Verdict version
Research run version
```

---

## Principle 6 — Cache Is Not Truth

Cached data represents previously observed state.

It must never automatically be treated as current truth.

---

# 3. Logical Data Domains

The data model can be divided into:

```text
Identity
Requests
Claims
Research
Sources
Documents
Evidence
Provenance
Models
Verdicts
Usage
Observability
Evaluation
```

---

# 4. High-Level Data Model

```text
User
 │
 └── Verification Request
          │
          └── Claim
                │
                ├── Atomic Claims
                │      │
                │      └── Research Tasks
                │
                └── Research Run
                       │
                       ├── Search Queries
                       ├── Documents
                       ├── Evidence
                       ├── Conflicts
                       └── Verdict
```

---

# 5. Core Entities

Initial core entities:

```text
users
organizations
verification_requests
claims
atomic_claims
research_runs
research_tasks
search_queries
sources
documents
passages
evidence
provenance_groups
evidence_relationships
conflicts
verdicts
model_runs
policy_versions
```

---

# 6. Verification Request

A verification request represents the product-level operation.

Conceptual fields:

```text
verification_id
user_id
organization_id
claim_id
mode
status
created_at
started_at
completed_at
policy_version
request_metadata
```

---

# 7. Claim

A claim represents the normalized proposition being evaluated.

Conceptual fields:

```text
claim_id
verification_id
raw_text
normalized_text
language
claim_type
domain
complexity
temporal_scope
verifiability
created_at
```

The raw claim should remain available for audit.

---

# 8. Atomic Claim

An atomic claim represents an independently assessable proposition.

Conceptual fields:

```text
atomic_claim_id
claim_id
text
materiality
claim_type
entities
temporal_scope
status
decomposition_version
```

---

# 9. Claim Decomposition Version

Because decomposition can change as models improve:

```text
claim
 ↓
decomposition_v1
 ↓
atomic claims
```

A future model may produce:

```text
decomposition_v2
```

Historical verification results should retain the original decomposition.

---

# 10. Research Run

A research run represents one complete investigation attempt.

Fields:

```text
research_run_id
verification_id
policy_version
status
started_at
completed_at
budget
budget_consumed
stop_reason
research_depth
```

A claim can have multiple research runs over time.

---

# 11. Research Task

Fields:

```text
task_id
research_run_id
atomic_claim_id
objective
priority
expected_value
estimated_cost
status
attempt_count
created_at
started_at
completed_at
```

Tasks should be append-oriented for auditability.

---

# 12. Search Query

A query should be stored independently from search results.

Fields:

```text
query_id
task_id
query_text
provider
strategy
created_at
latency
result_count
status
```

This allows query-generation performance to be evaluated.

---

# 13. Search Result

Search results should reference sources/documents rather than duplicating content.

Fields:

```text
search_result_id
query_id
source_id
rank
provider_score
retrieved_at
```

---

# 14. Source

A source represents the origin or publisher.

Fields:

```text
source_id
canonical_domain
publisher_name
source_type
authority_class
primary_status
country
language
metadata
```

Examples:

```text
Government
Scientific journal
University
News organization
Company
Blog
Social media
Forum
Unknown
```

---

# 15. Source Identity

A source should have a stable internal identity.

For example:

```text
https://www.example.com/article/123
```

should resolve to:

```text
canonical source/document identity
```

even if search providers return tracking parameters.

---

# 16. Canonical URL

URL normalization should handle:

```text
tracking parameters
fragments
redirects
protocol normalization
trailing slashes
canonical tags
```

The normalized URL should not destroy meaningful query parameters when they affect content.

---

# 17. Document

A document represents a retrievable version of source content.

Fields:

```text
document_id
source_id
canonical_url
content_hash
content_type
title
author
published_at
modified_at
retrieved_at
language
status
storage_uri
```

---

# 18. Document Versioning

The same URL can produce multiple versions.

```text
URL
 ├── Version A
 ├── Version B
 └── Version C
```

A content hash identifies the actual retrieved representation.

---

# 19. Why Content Hash Matters

If:

```text
URL = same
```

but:

```text
content_hash = different
```

the evidence state may have changed.

This supports:

```text
change detection
re-verification
cache invalidation
audit
```

---

# 20. Passage

Documents should be segmented into passages.

Fields:

```text
passage_id
document_id
sequence
text
char_start
char_end
token_count
content_hash
```

A passage is the basic retrieval/evidence unit.

---

# 21. Passage Versioning

Passage segmentation can change with:

```text
parser version
chunking strategy
document version
```

Therefore:

```text
document_version
+
segmentation_version
```

should identify the passage representation.

---

# 22. Evidence

Evidence represents a claim-relative interpretation of a passage.

Fields:

```text
evidence_id
atomic_claim_id
passage_id
relationship
relevance_score
entailment_score
contradiction_score
source_quality_score
independence_score
temporal_validity
assessment_version
created_at
```

Important:

> A passage is not automatically evidence.

Evidence exists only relative to a claim.

---

# 23. Evidence Relationships

Possible relationship:

```text
SUPPORTS
CONTRADICTS
NEUTRAL
CONTEXTUALIZES
QUALIFIES
```

This is richer than a simple entailment label.

---

# 24. Evidence Assessment

An evidence assessment records model/system judgments.

Fields:

```text
assessment_id
evidence_id
model_id
model_version
task
output
confidence
created_at
```

This allows re-evaluation without destroying historical results.

---

# 25. Evidence Snapshot

A completed verdict should reference an evidence snapshot.

Conceptually:

```text
evidence_snapshot_id
```

The snapshot identifies the exact evidence state used for the decision.

This is essential for reproducibility.

---

# 26. Evidence Snapshot Contents

A snapshot should capture:

```text
evidence IDs
assessment versions
source metadata
research policy
model versions
aggregation policy
timestamp
```

---

# 27. Provenance Group

A provenance group represents evidence that likely originates from the same underlying information.

Example:

```text
Original government report
       ↓
News article A
       ↓
News article B
       ↓
Blog C
```

may belong to one provenance group.

Fields:

```text
provenance_group_id
confidence
method
created_at
```

---

# 28. Provenance Membership

Relationship:

```text
evidence_id
provenance_group_id
confidence
method
```

An evidence item can potentially participate in multiple provenance hypotheses.

---

# 29. Evidence Relationship Graph

Potential relationships:

```text
DERIVED_FROM
CITES
QUOTES
DUPLICATES
CONTRADICTS
SUPPORTS
QUALIFIES
```

This can initially be represented relationally.

---

# 30. Conflict

A conflict represents unresolved disagreement between evidence units.

Fields:

```text
conflict_id
atomic_claim_id
status
conflict_type
severity
resolution
created_at
resolved_at
```

---

# 31. Conflict Types

Examples:

```text
DIRECT_CONTRADICTION
TEMPORAL_CONFLICT
DEFINITION_CONFLICT
NUMERICAL_CONFLICT
ENTITY_CONFLICT
METHODOLOGICAL_CONFLICT
SOURCE_CONFLICT
```

---

# 32. Verdict

Fields:

```text
verdict_id
verification_id
verdict
confidence
evidence_sufficiency
stop_reason
explanation_id
created_at
verdict_engine_version
calibration_version
```

---

# 33. Verdict History

A claim may be verified multiple times.

Example:

```text
2026-01 → SUPPORTED
2026-06 → REFUTED
2026-08 → SUPPORTED
```

This is not necessarily inconsistency.

The underlying world or evidence may have changed.

Historical verdicts should remain immutable.

---

# 34. Model Run

Every significant model invocation may be represented as:

```text
model_run_id
model_id
model_version
task
input_reference
output_reference
latency
token_count
device
precision
created_at
```

Sensitive input data should not be stored unnecessarily.

---

# 35. Policy Version

Policy configuration should be versioned.

Examples:

```text
research_policy_v3
verdict_policy_v5
routing_policy_v2
```

---

# 36. Policy Table

Conceptual fields:

```text
policy_id
policy_type
version
configuration
created_at
status
```

The actual configuration can be stored as JSON with validation.

---

# 37. Relational Schema

A conceptual relational schema:

```text
users
 └── verification_requests
      └── claims
           ├── atomic_claims
           │     └── research_tasks
           │            └── search_queries
           │
           └── research_runs
                  ├── search_queries
                  ├── evidence
                  ├── conflicts
                  └── verdicts

sources
 └── documents
      └── passages
           └── evidence

evidence
 ├── assessments
 └── provenance_memberships

provenance_groups
 └── provenance_memberships
```

---

# 38. PostgreSQL as Initial System of Record

PostgreSQL is a strong initial choice because it can support:

```text
ACID transactions
JSONB
full-text search
relational joins
partitioning
extensions
pgvector
```

This reduces infrastructure complexity.

---

# 39. PostgreSQL Schema Strategy

Use separate logical schemas where useful:

```text
core
research
evidence
models
analytics
```

This improves ownership and organization without requiring separate databases.

---

# 40. UUIDs vs Sequential IDs

Public identifiers should preferably be:

```text
UUID / ULID
```

rather than exposing sequential database IDs.

ULIDs can also provide approximate time ordering.

---

# 41. Timestamps

Store timestamps consistently in:

```text
UTC
```

Use explicit timezone conversion only at presentation boundaries.

---

# 42. Temporal Data

Important dates include:

```text
claim_time
event_time
publication_time
retrieval_time
modification_time
verification_time
```

These must not be conflated.

---

# 43. Temporal Semantics

A document published today may describe:

```text
an event from 2010.
```

The data model must preserve both:

```text
publication_time = 2026
event_time = 2010
```

---

# 44. Indexing Strategy

Important indexes:

```text
verification_requests.status
verification_requests.created_at
claims.normalized_hash
atomic_claims.claim_id
research_tasks.status
research_tasks.priority
documents.canonical_url
documents.content_hash
documents.retrieved_at
passages.document_id
evidence.atomic_claim_id
evidence.relationship
verdicts.verification_id
```

Indexes should be created based on measured query patterns.

---

# 45. Claim Hash

Normalized claims should receive a deterministic hash.

Example:

```text
normalized_claim
      ↓
SHA-256
      ↓
claim_hash
```

This can support:

```text
exact cache lookup
deduplication
analytics
```

---

# 46. Semantic Claim Cache

Exact hashes cannot detect paraphrases.

A semantic cache can use:

```text
claim embedding
+
similarity threshold
+
freshness policy
+
policy compatibility
```

It must be conservative.

False cache matches can be worse than cache misses.

---

# 47. Vector Storage

Vectors may be stored using:

```text
pgvector
```

initially.

Vectors should include metadata:

```text
document_id
passage_id
language
domain
timestamp
embedding_model_version
```

---

# 48. Vector Index Strategy

Potential index methods:

```text
HNSW
IVFFlat
```

HNSW is often attractive for low-latency retrieval, while index build/memory characteristics must be evaluated for the actual workload.

---

# 49. Hybrid Retrieval Data

Store lexical and dense retrieval representations.

```text
Dense:
embedding vector

Lexical:
PostgreSQL FTS / search index
```

The retrieval layer can combine:

```text
BM25-style score
+
dense similarity
```

---

# 50. Document Fingerprinting

Use multiple fingerprints when useful:

```text
URL hash
content hash
title hash
simhash / locality-sensitive fingerprint
```

This can help identify near-duplicate content.

---

# 51. Deduplication

Deduplication should happen at multiple levels:

```text
URL deduplication
Content deduplication
Passage deduplication
Semantic deduplication
Provenance deduplication
```

Each solves a different problem.

---

# 52. Search Result Deduplication

Two providers may return:

```text
same URL
```

Normalize before counting.

---

# 53. Content Deduplication

Different URLs may host identical content.

Use:

```text
content_hash
```

to detect exact duplicates.

---

# 54. Semantic Deduplication

Slightly modified copies may require:

```text
embedding similarity
+
text similarity
```

to detect near duplicates.

---

# 55. Provenance Deduplication

Two articles may contain different wording but derive from:

```text
same original report
```

This requires provenance analysis rather than simple text deduplication.

---

# 56. Data Consistency

Different data types need different consistency guarantees.

### Strong consistency

Use for:

```text
verification state
job status
verdict record
billing / quota
```

### Eventual consistency

Acceptable for:

```text
search cache
analytics
derived embeddings
recommendation metadata
```

---

# 57. Transaction Boundaries

Example:

```text
Create verification
+
create research run
```

should be atomic.

Evidence ingestion may be asynchronous.

Verdict creation should only occur after the required evidence snapshot is successfully persisted.

---

# 58. Idempotent Writes

External retries can cause duplicate events.

Use unique constraints such as:

```text
(provider, query_hash, timestamp_window)
(document_content_hash)
(model_run_id)
```

where appropriate.

---

# 59. Data Partitioning

At high volume, partition large tables.

Candidates:

```text
research_tasks
search_queries
model_runs
evidence
events
```

Partitioning may use:

```text
time
tenant
```

The exact strategy should be based on actual query patterns.

---

# 60. Time-Based Partitioning

For append-heavy tables:

```text
model_runs
events
research_tasks
```

monthly or weekly partitions may simplify:

```text
retention
archival
maintenance
```

---

# 61. Evidence Partitioning

Evidence may grow extremely quickly.

Potential partition key:

```text
created_at
```

or:

```text
research_run_id hash
```

depending on workload.

Avoid premature partitioning.

---

# 62. Archival

Old data can move through:

```text
Hot
 ↓
Warm
 ↓
Cold
 ↓
Deleted
```

Example:

```text
Hot:
recent verifications

Warm:
historical verification metadata

Cold:
large document snapshots
```

---

# 63. Retention Policy

Retention should differ by data type.

Example policy:

```text
API logs → short
raw request content → configurable
research metadata → longer
verdict metadata → long
evaluation datasets → persistent
large snapshots → lifecycle-managed
```

Actual durations should be defined by product/legal requirements.

---

# 64. Evidence Retention

Evidence required to reproduce a verdict should remain available for the configured audit period.

If full document retention is not possible, preserve:

```text
passage
source
URL
hash
retrieval timestamp
metadata
```

subject to applicable legal/copyright constraints.

---

# 65. Data Privacy

User-generated claims may contain sensitive information.

Data architecture should support:

```text
encryption
redaction
access control
retention
deletion
```

---

# 66. Right-to-Delete Considerations

If user data must be deleted:

```text
User
 ↓
Verification requests
 ↓
Claims
 ↓
Private metadata
```

should be removable without necessarily deleting public source records.

The data model should separate:

```text
user-owned data
```

from:

```text
public evidence metadata
```

---

# 67. Multi-Tenant Data Isolation

Tenant-scoped tables should contain:

```text
organization_id
```

where required.

Queries should enforce tenant boundaries.

Row-level security may be considered where appropriate.

---

# 68. Access Control

Data access should be separated into:

```text
Public
Internal
Restricted
Sensitive
```

Examples:

```text
Public:
source metadata

Internal:
research traces

Restricted:
user claims

Sensitive:
credentials / private account data
```

---

# 69. Data Lineage

Every final verdict should be traceable:

```text
Verdict
 ↓
Evidence Snapshot
 ↓
Evidence
 ↓
Passage
 ↓
Document
 ↓
Source
 ↓
Retrieval Event
```

And:

```text
Verdict
 ↓
Policy Version
 ↓
Model Versions
 ↓
Research Run
```

---

# 70. Data Lineage IDs

Use stable IDs:

```text
verification_id
claim_id
atomic_claim_id
research_run_id
task_id
query_id
document_id
passage_id
evidence_id
assessment_id
verdict_id
```

These IDs form the backbone of observability.

---

# 71. Evidence Snapshot Design

An evidence snapshot may be represented as:

```text
snapshot_id
research_run_id
created_at
evidence_ids[]
assessment_versions[]
policy_version
model_versions[]
```

For large snapshots, store the manifest in object storage and retain the metadata in PostgreSQL.

---

# 72. Immutable Decision Records

Completed verdicts should be immutable.

If a new verdict is generated:

```text
new verdict record
```

rather than:

```text
overwrite old verdict
```

This supports auditability.

---

# 73. Data Migrations

Schema changes should use:

```text
versioned migrations
```

Example:

```text
001_initial_schema
002_add_provenance
003_add_evidence_snapshot
```

Migrations must be tested against realistic datasets.

---

# 74. Backward Compatibility

Application releases should tolerate:

```text
old rows
+
new rows
```

during rolling deployments.

Avoid destructive schema changes without migration plans.

---

# 75. Analytics Data

Operational database queries should not become the primary analytics system at large scale.

Eventually:

```text
Operational DB
 ↓
Event stream
 ↓
Analytics warehouse
```

Potential warehouse:

```text
BigQuery
Snowflake
ClickHouse
Redshift
```

The choice depends on product scale and query patterns.

---

# 76. Event Data

Useful events:

```text
verification.created
research.started
research.task_created
search.executed
document.fetched
evidence.created
conflict.detected
verdict.created
verification.completed
```

Events can support:

```text
analytics
billing
monitoring
experimentation
```

---

# 77. Usage Data

Track:

```text
verification count
mode
latency
search calls
LLM tokens
compute time
cache hits
evidence count
```

This supports:

```text
cost modeling
quotas
billing
product analytics
```

---

# 78. Data Quality Metrics

The data platform should monitor:

```text
duplicate document rate
missing publication dates
invalid URLs
missing source types
orphan evidence
orphan passages
broken provenance links
stale vectors
```

---

# 79. Orphan Detection

Examples:

```text
Evidence without passage
Passage without document
Document without source
Verdict without evidence snapshot
```

These should be detected automatically.

---

# 80. Referential Integrity

Use database constraints for core relationships:

```text
foreign keys
unique constraints
check constraints
```

Do not rely entirely on application code.

---

# 81. Soft Delete vs Hard Delete

For user data:

```text
soft delete
```

may help audit workflows.

For data subject to deletion requirements:

```text
hard deletion
```

may be necessary.

The product's retention policy should determine the strategy.

---

# 82. Data Compression

Large content can be compressed in object storage.

For PostgreSQL:

```text
TOAST
```

handles some large values automatically, but very large documents should generally remain outside transactional rows.

---

# 83. Storage Cost Optimization

Cost can be reduced by:

```text
content deduplication
compression
tiered storage
TTL
selective snapshots
embedding reuse
document reuse
```

---

# 84. Data Locality

Keep frequently accessed data together.

Example:

```text
Verification
+
Verdict
+
Evidence metadata
```

should be quickly joinable.

Large document bodies should remain external.

---

# 85. Cache Consistency

A cached verdict must carry:

```text
cache_timestamp
evidence_timestamp
policy_version
model_versions
```

This prevents accidental reuse of stale results.

---

# 86. Cache Stampede Protection

If many users request the same claim simultaneously:

```text
100 requests
 ↓
same expensive research
```

should become:

```text
1 research job
 ↓
100 subscribers
```

Use:

```text
request coalescing
distributed locks
job deduplication
```

---

# 87. Single-Flight Research

A useful pattern:

```text
Claim arrives
 ↓
Check active research
 ↓
Already running?
   ├── yes → attach request
   └── no  → start research
```

This can dramatically reduce duplicate work.

---

# 88. Semantic Research Reuse

For equivalent claims:

```text
claim A
≈
claim B
```

the system may reuse evidence if:

```text
semantic equivalence
+
same temporal requirements
+
same domain
+
freshness valid
```

This requires conservative matching.

---

# 89. Freshness Model

Every evidence object should have:

```text
retrieved_at
published_at
event_time
expires_at (optional)
freshness_class
```

---

# 90. Freshness Classes

Potential:

```text
REAL_TIME
SHORT_LIVED
MEDIUM_LIVED
STABLE
HISTORICAL
```

Examples:

```text
Stock price → REAL_TIME

Current office holder → SHORT_LIVED

Scientific constant → STABLE

Historical event → HISTORICAL
```

---

# 91. Freshness-Aware Cache

Cache TTL should depend on claim type.

Conceptually:

\[
TTL = f(claim\_type, freshness\_class)
\]

A fixed global TTL is inappropriate.

---

# 92. Reverification Triggers

Reverification may be triggered by:

```text
TTL expiration
source update
policy update
model update
user request
known event
```

---

# 93. Incremental Reverification

Do not necessarily repeat the entire research process.

Potential approach:

```text
Existing evidence
      ↓
Detect changed sources
      ↓
Retrieve updated evidence
      ↓
Recompute affected atomic claims
      ↓
Recompute verdict
```

This can significantly reduce cost.

---

# 94. Dependency Graph

A verdict should know which evidence it depends on.

```text
Verdict
 ↓
Atomic Claim
 ↓
Evidence
 ↓
Document
```

If one document changes:

```text
Affected verdicts
```

can be identified.

---

# 95. Data Architecture for Millions of Users

At scale:

```text
PostgreSQL
 ↓
Partitioned transactional data

Object Storage
 ↓
Documents / snapshots

Vector Infrastructure
 ↓
Embeddings

Redis
 ↓
Hot cache

Warehouse
 ↓
Analytics

Event Stream
 ↓
System events
```

---

# 96. Sharding

Sharding should be considered only after:

```text
vertical scaling
+
read replicas
+
partitioning
+
query optimization
```

are insufficient.

Potential shard keys:

```text
tenant
region
hash(user_id)
```

A poor shard key can create severe hotspots.

---

# 97. Read Replicas

Read-heavy workloads can use:

```text
Primary
 ↓
Read replicas
```

Suitable for:

```text
historical verdict lookup
analytics-adjacent reads
source metadata
```

Strongly consistent writes remain on primary.

---

# 98. Database Hotspots

Potential hotspots:

```text
active research state
popular claim cache
job queue
usage counters
```

Use:

```text
Redis
partitioning
atomic counters
batched writes
```

where appropriate.

---

# 99. Batch Persistence

High-frequency model results should not necessarily perform one database write per inference.

Instead:

```text
Model worker
 ↓
batch results
 ↓
bulk insert
```

This can reduce database overhead significantly.

---

# 100. Data Architecture Invariants

### INV-DA-001

Every verdict must be traceable to an evidence snapshot.

### INV-DA-002

Every evidence item must be traceable to a passage and source.

### INV-DA-003

Every document version must be identifiable by content hash.

### INV-DA-004

Historical verdicts must remain immutable.

### INV-DA-005

Model and policy versions must be retained with decisions.

### INV-DA-006

Cache entries must not bypass freshness policy.

### INV-DA-007

Duplicate evidence must not artificially increase confidence.

### INV-DA-008

User-owned data must remain separable from public source data.

### INV-DA-009

Large content should not unnecessarily burden transactional storage.

### INV-DA-010

Data deletion and retention must be policy-driven.

---

# 101. Initial Technology Recommendation

For the first serious implementation:

```text
PostgreSQL
├── transactional state
├── evidence metadata
├── provenance metadata
└── pgvector

Redis
├── cache
├── locks
├── request coalescing
└── lightweight queues if needed

Object Storage
├── document snapshots
├── extracted content
└── evaluation artifacts
```

This is intentionally conservative.

---

# 102. Evolution Path

## Phase 1

```text
PostgreSQL
+
pgvector
+
Redis
+
object storage
```

## Phase 2

```text
Read replicas
+
partitioning
+
analytics warehouse
```

## Phase 3

```text
Dedicated vector infrastructure
+
event streaming
+
specialized storage
```

## Phase 4

```text
Multi-region
+
sharding where justified
+
advanced evidence graph infrastructure
```

---

# 103. Data Research Questions

The implementation should experimentally determine:

1. How large can pgvector remain before dedicated vector infrastructure becomes necessary?
2. What is the optimal passage length?
3. How much semantic cache reuse is safe?
4. How aggressively can document snapshots be deduplicated?
5. Which evidence metadata deserves relational indexing?
6. What freshness TTLs optimize quality versus cost?
7. How much database write amplification comes from model traces?
8. When does an event stream become worthwhile?
9. Which tables require partitioning first?
10. What data should remain hot versus cold?

---

# 104. Final Data Architecture Principle

> **Store enough information to reproduce and audit a decision, but do not store every artifact indefinitely or in the most expensive storage tier.**

The data architecture should preserve the epistemic chain:

```text
Claim
 ↓
Research
 ↓
Source
 ↓
Document
 ↓
Passage
 ↓
Evidence
 ↓
Assessment
 ↓
Verdict
```

while optimizing:

```text
Storage
Query performance
Freshness
Cost
Privacy
Scalability
```

---

# 105. Next Step

The next document should be:

**`13-retrieval-architecture.md`**

It will define the retrieval system in detail:

- query planning;
- hybrid search;
- lexical retrieval;
- dense retrieval;
- query expansion;
- source-aware retrieval;
- freshness-aware retrieval;
- reranking;
- deduplication;
- provenance-aware retrieval;
- search-provider routing;
- retrieval caching;
- and retrieval evaluation using Recall@K, MRR, nDCG, evidence recall, and end-to-end verification impact.
