# Tathvyn — Domain Model

## 1. Purpose

This document defines the core domain model of Tathvyn.

The domain model is intentionally independent of:

- web frameworks;
- databases;
- search providers;
- vector stores;
- LLM providers;
- ML frameworks;
- orchestration frameworks;
- deployment platforms.

The objective is to establish stable concepts and contracts before implementation technology is selected.

---

# 2. Domain Model Principles

The Tathvyn domain model follows these principles:

1. **Claims and evidence are separate entities.**
2. **Atomic claims are independently verifiable units.**
3. **Evidence is passage-level and traceable to a document and source.**
4. **Source quality is represented as evidence, not as an absolute truth label.**
5. **Provenance and source independence are first-class concepts.**
6. **Temporal validity is explicitly represented.**
7. **Confidence is distinct from raw model scores.**
8. **Research resources are explicitly budgeted.**
9. **Every verdict must be traceable to evidence and intermediate assessments.**
10. **Domain objects should remain useful even if the underlying models change.**

---

# 3. Domain Overview

```text
VerificationRequest
        │
        ▼
      Claim
        │
        ├──────────────┐
        ▼              ▼
 Atomic Claims      Claim Context
        │
        ▼
 Research Tasks
        │
        ▼
    Documents
        │
        ▼
    Evidence
        │
        ├──────────────┐
        ▼              ▼
 EvidenceAssessment  Provenance
        │              │
        └──────┬───────┘
               ▼
         Evidence Graph
               │
               ▼
     Evidence Sufficiency
               │
               ▼
            Verdict
               │
               ▼
      VerificationResult
```

---

# 4. Entity Classification

The domain model distinguishes between:

### Core entities

Objects with independent identity and lifecycle.

Examples:

- VerificationRequest
- Claim
- AtomicClaim
- Entity
- Source
- Document
- Evidence
- ProvenanceGroup
- VerificationResult

### Value objects

Objects defined primarily by their attributes.

Examples:

- TemporalScope
- VerificationBudget
- EvidenceScore
- UncertaintyProfile
- ResearchObjective

### Derived objects

Objects produced through analysis.

Examples:

- EvidenceAssessment
- ResearchPlan
- EvidenceGraph
- Verdict

This distinction should influence persistence and mutation semantics later.

---

# 5. VerificationRequest

Represents one user/API request to verify a claim.

## Required fields

```text
request_id
created_at
input_text
status
```

## Optional fields

```text
user_id
client_id
language_hint
requested_depth
requested_freshness
client_metadata
```

## Status

Initial lifecycle:

```text
RECEIVED
VALIDATING
PROCESSING
COMPLETED
PARTIAL
FAILED
CANCELLED
```

## Invariants

- `request_id` must be globally unique.
- Original input must never be overwritten.
- A completed request must reference a VerificationResult unless explicitly marked failed.

---

# 6. Claim

Represents the normalized factual proposition extracted from a verification request.

## Fields

```text
claim_id
request_id
raw_text
normalized_text
language
claim_type
verifiability
entities
temporal_scope
qualifiers
atomic_claim_ids
created_at
```

## Raw vs normalized text

`raw_text` preserves exactly what the user supplied.

`normalized_text` represents the proposition in a form suitable for downstream processing.

Example:

```text
Raw:
"Is it true that India grew by 8.2% in 2024?"

Normalized:
"India's GDP grew by 8.2% in 2024."
```

## Invariants

- Raw input is immutable.
- A claim must have a unique identity.
- Atomic claims must remain traceable to their parent claim.
- Normalization must not materially alter the asserted proposition.

---

# 7. ClaimType

Claim type should support multi-dimensional classification.

Initial values:

```text
FACTUAL
NUMERICAL
TEMPORAL
CAUSAL
ATTRIBUTION
HISTORICAL
COMPARATIVE
PREDICTIVE
OPINION
COMPOUND
```

The representation should eventually support:

```text
primary_type
secondary_types[]
domain
```

Example:

```text
Claim:
"India's GDP growth exceeded China's in 2025."

primary_type:
COMPARATIVE

secondary_types:
NUMERICAL
TEMPORAL

domain:
ECONOMICS
```

---

# 8. Verifiability

Represents whether the claim can meaningfully be investigated.

Values:

```text
VERIFIABLE
PARTIALLY_VERIFIABLE
TIME_DEPENDENT
CONTEXT_DEPENDENT
UNVERIFIABLE
```

Verifiability is a domain property, not merely a model output.

It controls whether and how research should proceed.

---

# 9. AtomicClaim

An independently verifiable proposition derived from a Claim.

## Fields

```text
atomic_claim_id
claim_id
text
is_atomic
decomposition_depth
subject
predicate
object
qualifiers
entities
temporal_scope
claim_type
importance
status
```

> **Note on Already-Atomic Claims**: If the parent claim contains only a single indivisible proposition, the system generates exactly one `AtomicClaim` with `is_atomic=True` and `decomposition_depth=0`. Decomposition depth is capped at 1; atomic claims are never recursively decomposed.

## Example

Parent claim:

> "The government increased the EV GST rate from 12% to 18% in 2025."

Possible atomic claims:

```text
AC-001:
EV GST rate was 12%.

AC-002:
EV GST rate became 18%.

AC-003:
The rate changed in 2025.

AC-004:
The change applied to electric vehicles.

AC-005:
The change was implemented by the relevant government authority.
```

Each atomic claim can have different evidence and status.

---

# 10. Atomic Claim Importance

Not every proposition contributes equally to the overall claim.

Importance should be represented as:

```text
PRIMARY
MATERIAL
CONTEXTUAL
```

Potential future representation:

```text
importance_score ∈ [0, 1]
```

The score must not be treated as a truth probability.

It represents how materially the atomic claim affects the meaning of the overall claim.

---

# 11. Atomic Claim Status

Initial internal states:

```text
UNRESEARCHED
RESEARCHING
EVIDENCE_FOUND
EVIDENCE_ASSESSED
SUPPORTED
REFUTED
CONFLICTED
INSUFFICIENT
UNVERIFIABLE
```

Status transitions should be controlled rather than freely mutable.

---

# 12. Entity

Represents a real-world entity referenced by a claim.

## Entity types

```text
PERSON
ORGANIZATION
LOCATION
PRODUCT
EVENT
GOVERNMENT_ENTITY
FINANCIAL_ENTITY
SCIENTIFIC_ENTITY
OTHER
```

## Fields

```text
entity_id
mention
canonical_name
entity_type
canonical_identifier
confidence
ambiguity_status
```

## Important distinction

The system must preserve the difference between:

```text
mention:
"Washington"

canonical entity:
unknown
```

and:

```text
canonical entity:
Government of the United States
```

Ambiguous entity resolution must not silently become a false certainty.

---

# 13. TemporalScope

Represents the temporal meaning of a claim.

## Fields

```text
start
end
granularity
relation
reference_time
certainty
```

## Examples

### Exact date

```text
start = 2026-08-01
end = 2026-08-01
granularity = DAY
```

### Year

```text
start = 2024-01-01
end = 2024-12-31
granularity = YEAR
```

### Current

```text
relation = CURRENT
reference_time = verification_time
```

### Relative

```text
relation = BEFORE
reference_event = "2024 election"
```

TemporalScope should support uncertainty and incomplete dates.

---

# 14. Qualifier

Qualifiers modify the interpretation of a claim.

Examples:

```text
approximately
at least
only
primarily
according to X
in real terms
in India
among adults
```

Qualifiers must be preserved because removing them can change the proposition being verified.

---

# 15. Source

Represents an origin or publisher of information.

## Fields

```text
source_id
canonical_name
domain
source_type
authority_signals
expertise_signals
ownership
geographic_scope
metadata
```

## Source types

```text
GOVERNMENT
ACADEMIC
SCIENTIFIC_JOURNAL
PRIMARY_DOCUMENT
NEWS_ORGANIZATION
CORPORATE
NGO
EXPERT
SOCIAL_MEDIA
BLOG
FORUM
UNKNOWN
```

Source type is a feature, not a truth label.

---

# 16. SourceQualityProfile

Source quality should not be represented as one hard-coded trust number.

Instead:

```text
SourceQualityProfile
├── authority
├── domain_expertise
├── primary_source_status
├── methodological_transparency
├── editorial_quality
├── historical_reliability
└── domain_relevance
```

Each signal may have:

```text
value
confidence
basis
```

This allows source assessment to evolve as the system improves.

---

# 17. Document

Represents a specific publication or retrievable information artifact.

## Fields

```text
document_id
source_id
url
canonical_url
title
author
published_at
modified_at
retrieved_at
language
content_hash
content
extraction_status
metadata
```

## Extraction status

```text
SUCCESS
PARTIAL
FAILED
BLOCKED
PAYWALLED
EMPTY
UNSUPPORTED
```

A failed fetch must remain distinguishable from a document containing no relevant evidence.

---

# 18. Passage

Represents a bounded segment of document content.

## Fields

```text
passage_id
document_id
text
start_offset
end_offset
section
position
```

A passage is the primary unit from which Evidence objects are constructed.

---

# 19. Evidence

Represents a specific passage that may affect an atomic claim.

## Fields

```text
evidence_id
atomic_claim_id
document_id
passage_id
source_id
relationship
retrieval_scores
assessment_id
temporal_assessment
provenance_group_id
created_at
```

Evidence must be traceable to its original passage.

---

# 20. Evidence Relationship

The canonical relationship taxonomy is defined in [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md).

Values:

```text
SUPPORTS
PARTIALLY_SUPPORTS
CONTRADICTS
PARTIALLY_CONTRADICTS
QUALIFIES
CONTEXTUALIZES
NEUTRAL
```

The relationship describes the logical/empirical relationship between the evidence and the atomic claim.

It does not describe whether the source is trustworthy.

---

# 21. EvidenceAssessment

Represents the system's assessment of a candidate evidence item.

## Fields

```text
assessment_id
evidence_id
relevance_score
entailment_score
contradiction_score
specificity_score
source_quality_score
independence_score
temporal_validity_score
claim_coverage_score
assessment_method
model_version
created_at
```

## Critical rule

These scores must remain separate.

For example:

```text
semantic similarity = 0.94
```

does not mean:

```text
probability of truth = 0.94
```

Nor does:

```text
NLI entailment = 0.91
```

mean the source is factually correct.

---

# 22. ProvenanceGroup

Represents documents that share a common underlying information origin.

## Fields

```text
provenance_group_id
origin_document_id
member_document_ids
relationship_type
confidence
basis
```

## Relationship types

```text
ORIGINAL
SYNDICATED
QUOTED
REFERENCED
DERIVED
COPIED
UNKNOWN
```

Example:

```text
Original report
      ↓
News article
      ↓
Blog article
      ↓
Social post
```

These should not automatically count as four independent sources.

---

# 23. Source Independence

Independence is a relationship between evidence items or their sources.

Possible states:

```text
INDEPENDENT
DEPENDENT
LIKELY_DEPENDENT
UNKNOWN
```

Independence should be represented explicitly because evidence count without independence can create false consensus.

---

# 24. ResearchObjective

Represents a specific purpose for a research action.

Initial objectives:

```text
SUPPORT
CONTRADICT
PRIMARY_SOURCE
CLARIFY_ENTITY
CLARIFY_TIME
RESOLVE_CONFLICT
FILL_CLAIM_GAP
```

A research plan may contain multiple objectives.

---

# 25. ResearchTask

Represents one actionable unit of research.

## Fields

```text
research_task_id
claim_id
atomic_claim_id
objective
queries
preferred_source_types
priority
status
budget
created_at
completed_at
```

## Status

```text
PENDING
RUNNING
COMPLETED
FAILED
CANCELLED
```

---

# 26. ResearchPlan

Represents the planned investigation for a claim.

## Fields

```text
research_plan_id
claim_id
tasks
priority_order
verification_depth
budget
stopping_policy
created_at
```

The research plan may evolve during execution.

---

# 27. VerificationBudget

Represents resource constraints for an investigation.

## Fields

```text
max_search_calls
max_documents
max_passages
max_model_inferences
max_llm_calls
max_tokens
max_latency_ms
max_cost
max_research_depth
```

## Principle

Budget is not simply a cost limit.

It defines the maximum computational effort the controller is permitted to allocate.

---

# 28. EvidenceSufficiency

Represents whether current evidence is adequate for a decision.

Potential dimensions:

```text
claim_coverage
support_strength
contradiction_coverage
source_quality
source_independence
temporal_validity
evidence_consistency
primary_source_availability
```

The final implementation should not collapse these dimensions until the aggregation methodology has been validated.

---

# 29. UncertaintyProfile

Represents why a verification result may be uncertain.

Potential dimensions:

```text
claim_ambiguity
entity_ambiguity
temporal_uncertainty
evidence_scarcity
source_disagreement
source_quality_uncertainty
provenance_uncertainty
retrieval_uncertainty
model_uncertainty
```

This allows the system to say not only:

> "Confidence is low."

but:

> "Confidence is low because the available sources disagree and the primary source could not be located."

---

# 30. Verdict

Represents the final interpretation of the available evidence. Canonical taxonomies are defined in [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md).

## Values

```text
SUPPORTED
REFUTED
PARTIALLY_SUPPORTED
INSUFFICIENT_EVIDENCE
UNVERIFIABLE
```

> **Framing & Distortion**: Claims with accurate literal elements but distorted framing receive `PARTIALLY_SUPPORTED` with `framing_concerns: true` in metadata. Standalone `MISLEADING` verdict is deferred to V2.

## Fields

```text
verdict
confidence
evidence_sufficiency
uncertainty_profile
supporting_evidence_ids
contradicting_evidence_ids
unresolved_atomic_claim_ids
method_version
created_at
```

Confidence is only a calibrated probability-like quantity once empirical calibration exists.

Before calibration, raw model scores must not be exposed as probability of truth.

---

# 31. EvidenceGraph

Represents relationships among claims, evidence, documents, sources, and provenance.

## Nodes

```text
Claim
AtomicClaim
Entity
Document
Passage
Evidence
Source
ProvenanceGroup
```

## Edges

Potential edge types:

```text
CONTAINS
ASSERTS
MENTIONS
SUPPORTED_BY
CONTRADICTED_BY
DERIVED_FROM
PUBLISHED_BY
EXTRACTED_FROM
SAME_PROVENANCE_AS
REFERS_TO
TEMPORALLY_RELEVANT_TO
```

The graph should support explainability and evidence aggregation.

> **Storage Implementation Note**: The "Evidence Graph" is an in-memory typed Python graph structure constructed on-demand from relational PostgreSQL tables (`claims`, `atomic_claims`, `evidence`, `provenance_groups`, `conflicts`). It does NOT require a dedicated graph database (e.g. Neo4j) for MVP.

---

# 32. VerificationResult

Represents the complete output of a verification request.

## Fields

```text
result_id
request_id
claim
verdict
evidence_graph
supporting_evidence
contradicting_evidence
unresolved_claims
uncertainty_profile
research_summary
processing_metrics
model_versions
policy_version
created_at
```

## Processing metrics

Should include:

```text
latency
search_calls
documents_processed
passages_processed
model_inferences
llm_calls
tokens
estimated_cost
cache_hits
```

This makes product economics measurable per verification.

---

# 33. Domain Relationships

```text
VerificationRequest
        │
        │ 1:1
        ▼
      Claim
        │
        │ 1:N
        ▼
 AtomicClaim
        │
        │ 1:N
        ▼
     Evidence
        │
        ├───────────────┐
        │               │
        ▼               ▼
    Document          Source
        │
        ▼
     Passage
        │
        ▼
EvidenceAssessment
        │
        ▼
ProvenanceGroup

Claim
  │
  ▼
ResearchPlan
  │
  ▼
ResearchTask
  │
  ▼
Evidence

AtomicClaims + Evidence + Provenance
                  │
                  ▼
            EvidenceGraph
                  │
                  ▼
               Verdict
                  │
                  ▼
        VerificationResult
```

---

# 34. Immutability and Versioning

Some objects should be treated as immutable after creation.

### Immutable or append-only

- original user input;
- retrieved passage snapshot;
- evidence snapshot;
- assessment record;
- model version;
- policy version;
- final result record.

### Mutable during processing

- research plan;
- research task status;
- request status;
- resource budget consumption.

This distinction is important for reproducibility.

---

# 35. Model and Policy Versioning

A verification result must be associated with the versions of the systems that produced it.

At minimum:

```text
claim_understanding_version
retrieval_version
reranker_version
nli_version
source_scoring_version
aggregation_policy_version
research_policy_version
explanation_version
```

A future model improvement should not make historical results impossible to interpret.

---

# 36. Domain Invariants

The following invariants should be enforced:

### INV-001

Every Evidence object must point to a valid Passage.

### INV-002

Every Passage must belong to a Document.

### INV-003

Every Document must have a Source where source identity is known.

### INV-004

Every Evidence object must belong to an AtomicClaim.

### INV-005

Every AtomicClaim must belong to exactly one Claim.

### INV-006

Every Claim must belong to a VerificationRequest.

### INV-007

A verdict cannot claim SUPPORT or REFUTATION without associated evidence assessments.

### INV-008

Raw model confidence cannot automatically become calibrated confidence.

### INV-009

Duplicate or dependent sources must not automatically count as independent corroboration.

### INV-010

Absence of evidence must not automatically become REFUTED.

### INV-011

Retrieved document content must be treated as data rather than executable instructions.

### INV-012

Historical verification must retain the relevant temporal context.

---

# 37. Example End-to-End Object Graph

Claim:

> "India's GDP grew by 8.2% in 2024."

Conceptual representation:

```text
Claim
├── type: NUMERICAL
├── domain: ECONOMICS
├── temporal_scope: 2024
│
├── AtomicClaim A
│   └── "India's GDP grew in 2024."
│
└── AtomicClaim B
    └── "Growth was 8.2%."
```

Research:

```text
ResearchPlan
├── SUPPORT
│   └── India GDP 2024 official statistics
├── CONTRADICT
│   └── India GDP 2024 revised growth
└── PRIMARY_SOURCE
    └── official GDP statistics 2024
```

Evidence:

```text
Evidence A
├── Source: Government statistical agency
├── Passage: "..."
├── Relationship: SUPPORTS
└── Provenance: ORIGINAL

Evidence B
├── Source: Financial publication
├── Passage: "..."
├── Relationship: SUPPORTS
└── Provenance: DERIVED_FROM_A

Evidence C
├── Source: Independent institution
├── Passage: "..."
├── Relationship: CONTEXT
└── Provenance: INDEPENDENT
```

Final result:

```text
Verdict
├── SUPPORTED
├── evidence_sufficiency: HIGH
├── uncertainty: LOW
└── supporting_evidence:
    └── Evidence A
```

Notice that Evidence B should not automatically count as an independent second confirmation if it derives from Evidence A.

---

# 38. Persistence Implications

The domain model does not yet prescribe a database.

However, it implies several categories of storage:

```text
Transactional State
    ├── requests
    ├── claims
    ├── research tasks
    └── verdicts

Evidence Store
    ├── documents
    ├── passages
    ├── evidence
    └── provenance

Model Artifacts
    ├── embeddings
    └── model metadata

Evaluation Store
    ├── benchmark results
    ├── traces
    └── experiments
```

The final architecture may use different storage technologies for these workloads.

---

# 39. Why This Model Is Deliberately More Complex Than a Typical RAG Schema

A conventional RAG application might only need:

```text
Document
Chunk
Embedding
Metadata
```

Tathvyn requires more because its problem is different.

It needs to represent:

```text
Claim
Atomic Claim
Evidence
Support / Contradiction
Source
Source Independence
Provenance
Temporal Validity
Research Objective
Research Budget
Evidence Sufficiency
Uncertainty
Verdict
```

The additional structure exists because **verification is a reasoning problem over evidence, not simply retrieval followed by generation**.

---

# 40. Next Step

With the domain model established, the next document should define the actual verification methodology:

**`05-verification-methodology.md`**

That document will answer:

- How an atomic claim is verified.
- How evidence is judged.
- How support and contradiction are defined.
- How source quality is incorporated.
- How source independence is estimated.
- How temporal validity is evaluated.
- How evidence is aggregated.
- How conflicting evidence is handled.
- How evidence sufficiency is determined.
- How the final verdict is derived.
- Where deterministic rules, specialized ML, and LLM reasoning are allowed.

Only after that should we select the concrete ML/retrieval architecture.
