# Tathvyn — Retrieval Architecture

## 1. Purpose

Retrieval is the most important information-access layer in Tathvyn.

A perfect verdict engine cannot recover from evidence that was never retrieved.

The retrieval system must therefore optimize for:

```text
Evidence Recall
+
Evidence Precision
+
Source Diversity
+
Freshness
+
Provenance Quality
+
Latency
+
Cost
```

The primary objective is not:

> Find documents similar to the claim.

The objective is:

> **Find the smallest, highest-quality set of evidence that materially helps determine whether the claim is true, false, misleading, or unresolved.**

---

# 2. Retrieval Is Not Search

Search answers:

> What documents match this query?

Verification retrieval answers:

> What evidence can establish, contradict, qualify, or contextualize this atomic claim?

This distinction drives the architecture.

---

# 3. Retrieval Pipeline

```text
Atomic Claim
     ↓
Claim Analysis
     ↓
Retrieval Objective
     ↓
Query Planning
     ↓
Query Generation
     ↓
Search Provider Routing
     ↓
Candidate Discovery
     ↓
Document Fetch
     ↓
Passage Extraction
     ↓
Lexical Retrieval
     +
Dense Retrieval
     ↓
Candidate Fusion
     ↓
Reranking
     ↓
Deduplication
     ↓
Provenance Analysis
     ↓
Evidence Selection
```

---

# 4. Retrieval Objectives

Every retrieval task should have an explicit objective.

Possible objectives:

```text
FIND_SUPPORT
FIND_CONTRADICTION
FIND_PRIMARY_SOURCE
FIND_ORIGINAL_REPORT
RESOLVE_ENTITY
RESOLVE_DATE
VERIFY_NUMBER
VERIFY_QUOTE
VERIFY_COMPARISON
INVESTIGATE_CONFLICT
FIND_CONTEXT
```

This prevents generic search behavior.

---

# 5. Support and Contradiction Searches

A major design requirement:

Do not only search for evidence that confirms the claim.

For each material claim, the research controller should consider:

```text
Support query
+
Contradiction query
+
Primary-source query
```

Example:

Claim:

> "X caused Y."

Queries may include:

```text
X caused Y
X Y evidence
X Y study
X did not cause Y
X Y alternative explanation
X Y systematic review
```

---

# 6. Query Planning

Query planning converts:

```text
Claim
+
Research objective
+
Domain
+
Entities
+
Time
```

into search strategies.

Conceptually:

```text
QueryPlan
├── objective
├── query_variants
├── source_constraints
├── time_constraints
├── language
├── freshness
├── expected_evidence_type
└── budget
```

---

# 7. Query Generation Hierarchy

Use a layered approach:

```text
Level 0
Deterministic templates

Level 1
Entity / keyword expansion

Level 2
Semantic query rewriting

Level 3
LLM query synthesis
```

The system should escalate only when simpler strategies fail.

---

# 8. Deterministic Query Generation

For:

> "Did Company X acquire Company Y in 2025?"

Generate:

```text
Company X acquired Company Y 2025
Company X Company Y acquisition
Company X acquisition 2025
Company X Company Y merger
```

This is cheap and predictable.

---

# 9. Query Expansion

Expand:

```text
abbreviations
aliases
entity names
product names
official names
historical names
```

Example:

```text
WHO
World Health Organization
```

---

# 10. Entity-Aware Queries

Queries should preserve entity identity.

Instead of:

```text
Washington policy
```

prefer:

```text
Washington State policy
```

when the resolved entity is Washington State.

---

# 11. Temporal Query Expansion

Time should be explicitly incorporated when relevant.

Examples:

```text
2025
"2025"
after January 2025
before election
2024-2026
```

This reduces retrieval of semantically similar but temporally invalid evidence.

---

# 12. Numerical Query Expansion

For numerical claims:

> "Inflation was 6.2% in India in 2025."

Possible queries:

```text
India inflation 6.2 2025
India CPI 2025 6.2
India inflation rate 2025 official
India CPI 2025 government
```

The system should also search the metric without the claimed number:

```text
India CPI inflation 2025 official
```

This helps detect false numerical claims.

---

# 13. Quote Retrieval

For attribution claims:

> "Person X said Y."

Queries should include:

```text
"Y"
"Person X" "Y"
Person X statement
Person X transcript
Person X interview
```

Exact quote searches can be highly valuable.

---

# 14. Source-Targeted Retrieval

When evidence requirements are known, target relevant source classes.

Examples:

```text
Scientific
→ journals / repositories

Legal
→ statutes / court decisions

Government
→ official agencies

Financial
→ filings / investor relations

Corporate
→ official announcements

Historical
→ archives / scholarly sources
```

---

# 15. Source-Aware Querying

The retrieval controller should be able to express:

```text
preferred_source_type
preferred_domains
excluded_domains
primary_source_required
```

Example:

```text
preferred_domains:
sec.gov
```

for an SEC-related financial claim.

---

# 16. Search Provider Abstraction

The system should expose:

```python
SearchProvider.search(query, constraints)
```

rather than coupling retrieval to one vendor.

Potential providers:

```text
Provider A
Provider B
Provider C
Local search index
```

The provider layer handles:

```text
authentication
rate limits
pagination
timeouts
normalization
provider-specific metadata
```

---

# 17. Search Provider Routing

Providers can be selected based on:

```text
query type
region
freshness
cost
latency
provider health
result quality
```

---

# 18. Provider Quality Model

Track provider performance:

```text
evidence recall
unique source rate
latency
error rate
cost
freshness
```

A provider should not remain primary merely because it was initially selected.

---

# 19. Search Fallback

Example:

```text
Primary Provider
       ↓ failure
Secondary Provider
       ↓ failure
Tertiary Provider
       ↓ failure
Local / degraded search
```

Provider failure must be visible in the research trace.

---

# 20. Search Result Normalization

Normalize provider outputs into:

```text
SearchResult
├── title
├── url
├── snippet
├── source
├── published_at
├── provider
├── provider_rank
└── metadata
```

This creates a provider-independent retrieval layer.

---

# 21. Candidate Discovery

Candidate discovery should optimize:

```text
high recall
```

not final precision.

The initial candidate pool can therefore be relatively large.

Example:

```text
100 candidates
```

may be reduced to:

```text
20 reranked candidates
```

and eventually:

```text
5 evidence candidates
```

---

# 22. Hybrid Retrieval

A strong retrieval architecture combines:

```text
Lexical Retrieval
+
Dense Retrieval
```

because the two approaches fail differently.

---

# 23. Lexical Retrieval

Lexical retrieval is strong for:

```text
exact names
numbers
dates
quotes
rare terms
technical identifiers
```

Potential implementation:

```text
BM25-style search
```

---

# 24. Dense Retrieval

Dense retrieval is strong for:

```text
paraphrases
semantic similarity
different wording
conceptual relationships
```

Potential implementation:

```text
embedding model
+
vector index
```

---

# 25. Why Dense-Only Retrieval Is Unsafe

Dense similarity can match:

```text
Claim:
Company X did not acquire Y.

Passage:
Company X acquired Y.
```

because both discuss the same acquisition.

Therefore semantic similarity cannot determine stance.

---

# 26. Why Lexical-Only Retrieval Is Unsafe

Lexical retrieval can miss:

```text
Claim:
The regulator prohibited the product.

Evidence:
The regulator ordered the product's withdrawal.
```

Different wording can express materially related facts.

---

# 27. Hybrid Retrieval Architecture

```text
              Claim
                │
       ┌────────┴────────┐
       ▼                 ▼
   BM25 Search      Dense Search
       │                 │
       └────────┬────────┘
                ▼
          Candidate Fusion
                ↓
             Reranker
```

---

# 28. Candidate Fusion

Potential strategies:

```text
Union
Weighted score
Reciprocal Rank Fusion
Learned fusion
```

A simple RRF baseline is attractive because it combines rankings without requiring score calibration.

---

# 29. Reciprocal Rank Fusion

Conceptually:

\[
RRF(d)=
\sum_r
\frac{1}{k+rank_r(d)}
\]

where:

- \(d\) = document;
- \(r\) = retrieval system;
- \(k\) = smoothing constant.

The exact value should be tuned empirically.

---

# 30. Retrieval Granularity

Retrieval can operate at:

```text
Document
Passage
Sentence
```

A practical architecture:

```text
Document discovery
        ↓
Passage extraction
        ↓
Passage retrieval
        ↓
Sentence-level evidence extraction
```

---

# 31. Document-Level Retrieval

Useful for:

```text
source discovery
primary-source discovery
long-form context
```

---

# 32. Passage-Level Retrieval

Useful for:

```text
evidence ranking
NLI
citation
```

---

# 33. Sentence-Level Evidence

Useful for:

```text
precise support
precise contradiction
explanation
```

But sentence-only retrieval can lose surrounding qualifiers.

Therefore preserve neighboring context.

---

# 34. Context Windows

When a sentence is selected:

```text
target sentence
+
previous sentence
+
next sentence
```

may provide essential context.

The context window should be dynamically sized.

---

# 35. Chunking Strategy

Chunking should avoid arbitrary fixed-size chunks as the only method.

Potential strategy:

```text
HTML structure
 ↓
paragraphs
 ↓
sections
 ↓
sentences
 ↓
adaptive windows
```

---

# 36. Chunking Constraints

Chunks should preserve:

```text
semantic coherence
entity references
qualifiers
negation
numbers
citations
```

---

# 37. Retrieval Metadata

Every candidate should retain:

```text
retrieval_method
query_id
provider
rank
dense_score
lexical_score
publication_time
source_type
```

This is essential for evaluation.

---

# 38. Reranking

The reranker receives:

```text
atomic claim
+
candidate passage
```

and estimates:

```text
relevance to verification objective
```

It should not be asked for final truth.

---

# 39. Objective-Aware Reranking

The same passage can have different utility depending on the objective.

Example:

```text
FIND_SUPPORT
```

vs:

```text
FIND_CONTRADICTION
```

Therefore reranking may eventually incorporate:

```text
claim
objective
passage
```

rather than claim + passage only.

---

# 40. Reranker Candidate Size

Example:

```text
Search:
200 candidates

Deduplicate:
120

Hybrid fusion:
80

Rerank:
50

Evidence selection:
10
```

These are illustrative.

The actual numbers should be determined through recall/cost experiments.

---

# 41. Reranker Cost

Cross-encoders are more expensive than embeddings because they jointly process:

```text
claim
+
passage
```

Therefore:

```text
retrieve broadly
rerank narrowly
```

is the preferred architecture.

---

# 42. Evidence Selection

After reranking, the system should select evidence using:

```text
relevance
stance
source quality
independence
temporal validity
coverage
diversity
```

---

# 43. Evidence Diversity

Selecting the top 10 passages from the same document is often inferior to:

```text
3 passages
from
3 independent high-quality sources
```

Diversity should therefore be an explicit selection objective.

---

# 44. Source Diversity

Potential constraint:

```text
max N passages/source
```

unless a single primary source contains uniquely important information.

---

# 45. Provenance-Aware Selection

If:

```text
Source A
Source B
Source C
```

all derive from:

```text
Original Report
```

they should not necessarily count as three independent evidence units.

---

# 46. Temporal Filtering

Candidate evidence should be filtered by:

```text
publication time
event time
claim time
retrieval time
```

Example:

Claim:

> "X is currently CEO."

A 2018 article may be highly relevant semantically but invalid temporally.

---

# 47. Temporal Ranking

Temporal relevance can be a ranking feature:

```text
current claim
→ recent sources preferred

historical claim
→ contemporaneous sources preferred
```

Recency should not blindly override source quality.

---

# 48. Freshness-Aware Retrieval

The retrieval controller should specify:

```text
freshness_requirement
```

Examples:

```text
REAL_TIME
LAST_24_HOURS
LAST_7_DAYS
CURRENT
HISTORICAL
ANY
```

---

# 49. Source Quality Filtering

Quality should influence ranking but not necessarily hard-filter every low-authority source.

Low-quality sources can sometimes reveal:

```text
origin of a rumor
original quotation
claim propagation
```

Their role should be contextual rather than automatically evidentiary.

---

# 50. Primary Source Escalation

If secondary sources repeatedly report the same fact:

```text
search for original source
```

Example:

```text
News article
 ↓
Official report
 ↓
Original dataset
```

---

# 51. Retrieval of Primary Evidence

Strategies:

```text
domain targeting
exact title search
citation extraction
quoted phrase search
reference following
official entity lookup
```

---

# 52. Citation Following

If a useful article references:

```text
Study X
Report Y
Dataset Z
```

the retrieval system should be able to follow those references.

This can be more effective than issuing unrelated searches.

---

# 53. Citation Graph Traversal

Conceptually:

```text
Article
 ├── cites → Paper
 ├── cites → Report
 └── cites → Dataset
```

Traversal should be budget-limited.

---

# 54. Search Depth

Potential levels:

```text
Depth 0:
search results

Depth 1:
direct sources

Depth 2:
citations / primary sources

Depth 3:
underlying datasets / original records
```

The research controller decides when deeper traversal is worthwhile.

---

# 55. Retrieval Stopping

Retrieval should stop when:

```text
evidence sufficiency reached
+
contradiction search completed
+
marginal expected value is low
```

Not merely when:

```text
N documents retrieved
```

---

# 56. Information Gain

A retrieval action should ideally estimate:

\[
IG =
H(EvidenceState_{before})
-
H(EvidenceState_{after})
\]

where \(H\) represents uncertainty.

Exact probabilistic entropy is not required initially.

A heuristic information-gain score can be used.

---

# 57. Retrieval Value

A practical heuristic:

\[
Value =
ExpectedEvidenceImpact
-
RetrievalCost
\]

This allows cost-aware research.

---

# 58. Retrieval Budget

Each verification should have budgets:

```text
max_search_calls
max_documents
max_bytes
max_model_calls
max_time
max_cost
```

---

# 59. Budget Allocation

The budget can be allocated dynamically:

```text
Primary evidence search
      ↓
Contradiction search
      ↓
Conflict resolution
      ↓
Deep source traversal
```

If early evidence is decisive, later stages may receive less budget.

---

# 60. Retrieval Cache

Cache:

```text
query results
normalized URLs
documents
passages
embeddings
reranker scores
```

with appropriate version and freshness metadata.

---

# 61. Query Cache Key

A query cache key should include:

```text
normalized_query
provider
search_parameters
language
region
freshness_constraint
```

---

# 62. Retrieval Result Cache

A search result cache should retain:

```text
retrieval_timestamp
provider
query
results
provider metadata
```

Never discard retrieval time.

---

# 63. Document Fetch Cache

Use:

```text
canonical_url
+
content_hash
```

to avoid repeatedly fetching unchanged content.

---

# 64. Retrieval Deduplication

Deduplicate in this order:

```text
URL
 ↓
content
 ↓
near-duplicate
 ↓
semantic
 ↓
provenance
```

---

# 65. Near-Duplicate Detection

Useful methods:

```text
SimHash
MinHash
shingling
embedding similarity
```

The implementation should be selected based on measured workload.

---

# 66. Search Result Diversity

A search engine may return many pages from the same domain.

Candidate selection should apply:

```text
domain diversity
source-type diversity
geographic diversity
temporal diversity
```

when appropriate.

---

# 67. Retrieval Failure Modes

Initial taxonomy:

```text
MISSED_PRIMARY_SOURCE
MISSED_CONTRADICTION
SEMANTIC_MISMATCH
LEXICAL_MISMATCH
TEMPORAL_MISMATCH
ENTITY_MISMATCH
SOURCE_COLLAPSE
DUPLICATE_OVERCOUNT
STALE_RESULT
SEARCH_PROVIDER_FAILURE
FETCH_FAILURE
PARSER_FAILURE
RERANKING_ERROR
```

---

# 68. Retrieval Evaluation

Retrieval must be evaluated independently from final verdict accuracy.

Primary metrics:

```text
Recall@K
Precision@K
MRR
nDCG
MAP
Evidence Recall
Source Recall
Primary Source Recall
Contradiction Recall
```

---

# 69. Evidence Recall

The most important domain-specific metric:

> What fraction of the evidence required to correctly verify a claim is retrieved?

A system can have excellent generic search metrics while still missing the evidence necessary for verification.

---

# 70. Contradiction Recall

Measure:

```text
Did the system retrieve strong contradicting evidence when it existed?
```

This is critical because confirmation-biased retrieval can produce false confidence.

---

# 71. Primary Source Recall

Measure:

```text
When a primary source exists,
did the system retrieve it?
```

This should be tracked separately.

---

# 72. Source Diversity Metric

Possible metric:

```text
unique independent sources / selected evidence units
```

But raw source count is insufficient.

Provenance-adjusted diversity is preferable.

---

# 73. Provenance-Adjusted Recall

Measure whether the system retrieved:

```text
independent evidence clusters
```

rather than many derivative copies.

---

# 74. Retrieval Ablation Study

Compare:

```text
Lexical only
Dense only
Hybrid
Hybrid + reranker
Hybrid + reranker + provenance
```

Measure:

```text
retrieval metrics
+
final verdict metrics
```

---

# 75. End-to-End Retrieval Impact

Ultimately measure:

```text
Retrieval change
      ↓
Evidence change
      ↓
Verdict accuracy change
```

A retrieval improvement that does not improve verification may not justify its cost.

---

# 76. Retrieval Benchmark Dataset

Each benchmark example should contain:

```text
claim
atomic claims
gold evidence
gold contradictory evidence
primary source
source metadata
temporal requirements
difficulty
domain
```

---

# 77. Hard-Negative Dataset

Include passages that are:

```text
highly similar
but wrong
```

Examples:

```text
same entity
different year

same metric
different country

same event
different outcome

same wording
opposite negation
```

These are essential for reranker evaluation.

---

# 78. Query Benchmark

For each claim:

```text
gold query intents
relevant sources
relevant documents
```

can be evaluated.

The exact query wording need not be fixed.

What matters is retrieval effectiveness.

---

# 79. Retrieval Latency Budget

Measure:

```text
query generation
search API
fetch
parse
embedding
vector search
lexical search
fusion
reranking
```

independently.

---

# 80. Retrieval Cost Model

Approximate:

\[
C_R =
C_{search}
+
C_{fetch}
+
C_{embedding}
+
C_{rerank}
\]

The system should know the marginal cost of retrieving one additional evidence candidate.

---

# 81. Adaptive Retrieval

Eventually, retrieval should become policy-driven.

Example:

```text
Claim
 ↓
Initial retrieval
 ↓
Evidence state
 ↓
Need identified
 ├── support gap → support search
 ├── contradiction gap → contradiction search
 ├── provenance gap → source traversal
 ├── temporal gap → time-targeted search
 └── entity gap → entity search
```

This is superior to fixed query counts.

---

# 82. Retrieval as Active Search

The research agent can select:

```text
next query
```

based on:

```text
expected information gain
cost
latency
uncertainty
```

This turns retrieval from static search into active evidence acquisition.

---

# 83. Learned Retrieval Policy

A future policy could learn:

\[
q^* =
\arg\max_q
\frac{ExpectedInformationGain(q)}
{ExpectedCost(q)}
\]

This can eventually replace hand-designed heuristics.

---

# 84. Retrieval Safety

Retrieved pages are untrusted.

The retrieval system must protect against:

```text
prompt injection
malicious redirects
SSRF
oversized content
malformed documents
tracking abuse
resource exhaustion
```

---

# 85. Prompt Injection Boundary

Retrieved text should be represented as:

```text
<EVIDENCE>
...
</EVIDENCE>
```

and never as executable instructions.

The reasoning layer must treat it as data.

---

# 86. Search Result Poisoning

Search results themselves can be manipulated.

The system should therefore avoid:

```text
top result = truth
```

and instead combine:

```text
multiple retrieval paths
source quality
independence
primary evidence
```

---

# 87. Retrieval Observability

Every retrieval action should record:

```text
query
objective
provider
timestamp
results
latency
cost
cache_hit
selected_documents
```

---

# 88. Retrieval Trace

Example:

```text
Atomic Claim
 ↓
Query Q1
 ↓
Provider A
 ↓
30 results
 ↓
15 unique documents
 ↓
Hybrid retrieval
 ↓
10 candidates
 ↓
Reranker
 ↓
4 evidence passages
```

This allows debugging.

---

# 89. Retrieval Data Model

Core objects:

```text
QueryPlan
SearchQuery
SearchResult
Document
Passage
RetrievalCandidate
RerankResult
EvidenceCandidate
RetrievalRun
```

---

# 90. Retrieval API

Conceptually:

```python
retrieve(
    atomic_claim,
    objective,
    constraints,
    budget
) -> RetrievalResult
```

Output:

```text
candidate_evidence
retrieval_trace
budget_consumed
coverage
```

---

# 91. Retrieval Service Interface

Potential interfaces:

```python
search(query)
fetch(url)
parse(document)
embed(passages)
retrieve_dense(query)
retrieve_lexical(query)
rerank(query, passages)
deduplicate(candidates)
```

The orchestration layer should compose these operations.

---

# 92. Retrieval Pipeline Pseudocode

```text
retrieve(claim, objective):

    plan = build_query_plan(
        claim,
        objective
    )

    queries = generate_queries(plan)

    results = parallel_search(
        queries
    )

    candidates = normalize(results)

    candidates = deduplicate(candidates)

    documents = fetch_documents(
        candidates
    )

    passages = extract_passages(
        documents
    )

    lexical = lexical_retrieve(
        claim,
        passages
    )

    dense = dense_retrieve(
        claim,
        passages
    )

    candidates = fuse(
        lexical,
        dense
    )

    ranked = rerank(
        claim,
        candidates
    )

    selected = select_diverse_evidence(
        ranked
    )

    return selected
```

---

# 93. Retrieval Policy

The retrieval policy should specify:

```text
query budget
provider order
source constraints
freshness
candidate count
reranker depth
diversity constraints
primary-source requirements
contradiction search
```

Version it.

---

# 94. Retrieval Modes

### FAST

```text
few queries
small candidate set
minimal reranking
```

### STANDARD

```text
hybrid retrieval
multiple query strategies
reranking
```

### DEEP

```text
adaptive search
primary-source traversal
contradiction hunting
provenance investigation
```

---

# 95. Retrieval Quality vs Cost

A deeper search does not always produce a better verdict.

The system should optimize:

```text
marginal verification quality
```

per:

```text
marginal retrieval cost
```

---

# 96. Retrieval Scaling

At scale:

```text
API
 ↓
Retrieval Queue
 ↓
Search Workers
 ↓
Document Workers
 ↓
Embedding Workers
 ↓
Reranker Workers
```

Each stage can scale independently.

---

# 97. Search Rate Limits

Provider-specific rate limits should be modeled:

```text
provider
quota
requests_used
reset_time
cost
```

Routing can then select healthy providers.

---

# 98. Provider Cost Optimization

For equivalent quality:

```text
cheaper provider
```

should be preferred.

But:

```text
cheaper ≠ better
```

The routing system should use measured:

```text
quality / cost
```

---

# 99. Retrieval Provider Learning

The system can maintain per-provider performance by:

```text
domain
claim type
query type
region
freshness class
```

Example:

```text
Provider A:
excellent for news

Provider B:
excellent for technical sources

Provider C:
excellent for government documents
```

---

# 100. Final Retrieval Architecture

```text
                    Atomic Claim
                         │
                         ▼
                 ┌───────────────┐
                 │ Claim Analyzer│
                 └───────┬───────┘
                         ▼
                 ┌───────────────┐
                 │ Query Planner │
                 └───────┬───────┘
                         ▼
              ┌──────────────────────┐
              │ Query Generation      │
              │ templates + expansion│
              │ + optional LLM       │
              └──────────┬───────────┘
                         ▼
              ┌──────────────────────┐
              │ Provider Router      │
              └──────────┬───────────┘
                         ▼
                 ┌───────────────┐
                 │ Search Layer  │
                 └───────┬───────┘
                         ▼
                 Candidate URLs
                         │
                         ▼
                 ┌───────────────┐
                 │ Document Fetch│
                 └───────┬───────┘
                         ▼
                    Documents
                         │
                         ▼
                ┌─────────────────┐
                │ Passage Extract │
                └────────┬────────┘
                         ▼
              ┌─────────────────────┐
              │ Hybrid Retrieval    │
              │ lexical + dense     │
              └──────────┬──────────┘
                         ▼
                 Candidate Passages
                         │
                         ▼
                 ┌───────────────┐
                 │ Cross Encoder │
                 │ Reranker      │
                 └───────┬───────┘
                         ▼
                 Ranked Evidence
                         │
                         ▼
             ┌──────────────────────┐
             │ Diversity / Provenance│
             │ / Temporal Filtering │
             └──────────┬───────────┘
                        ▼
                 Evidence Candidates
                        │
                        ▼
                  Evidence Layer
```

---

# 101. Retrieval Invariants

### INV-R-001

Retrieval must optimize evidence recall, not only semantic similarity.

### INV-R-002

Support and contradiction retrieval must be separately considered.

### INV-R-003

Primary-source discovery must be an explicit retrieval capability.

### INV-R-004

Dense similarity cannot establish truth.

### INV-R-005

Lexical and dense retrieval should complement one another.

### INV-R-006

Dependent sources must not be counted as independent evidence.

### INV-R-007

Temporal validity must influence retrieval.

### INV-R-008

Retrieval must be budget-aware.

### INV-R-009

Retrieved content is untrusted input.

### INV-R-010

Retrieval improvements must be validated against end-to-end verification quality.

---

# 102. Key Research Questions

The retrieval system should empirically answer:

1. What candidate pool size maximizes evidence recall per unit cost?
2. How much does hybrid retrieval outperform dense-only retrieval?
3. How much does reranking improve final verdict accuracy?
4. How much does source diversity improve calibration?
5. How effective is contradiction-first retrieval?
6. How often can primary-source traversal resolve uncertainty?
7. What is the optimal passage size?
8. How much can retrieval caching reduce cost?
9. What is the safe semantic-cache threshold?
10. How should retrieval policies differ by claim type?
11. How much does adaptive retrieval outperform fixed-depth retrieval?
12. Which search provider performs best for which claim classes?

---

# 103. Final Principle

> **Retrieve for uncertainty reduction, not document accumulation.**

A high-quality Tathvyn retrieval system should not return the largest pile of sources.

It should return the smallest set of:

```text
Relevant
Independent
Temporally valid
High-quality
Provenance-aware
Contradiction-aware
```

evidence that allows the Verdict Engine to make the strongest justified decision.

---

# 104. Next Step

The next document should be:

**`14-evidence-engineering.md`**

It will define the layer between retrieval and verdict:

- document normalization;
- passage extraction;
- evidence extraction;
- stance assessment;
- source quality;
- provenance;
- contradiction detection;
- evidence graphs;
- evidence clustering;
- evidence confidence;
- evidence compression;
- citation grounding;
- and the formal representation of evidence that the Verdict Engine consumes.
