# Tathvyn — Canonical Enums and Taxonomies

## 1. Purpose

This document is the **single source of truth** for all enums, taxonomies, and categorical values used across the Tathvyn system.

When any other document references a classification, label set, or categorical type, the canonical definition lives here. If a conflict exists between this document and another, **this document takes precedence**.

All enum values should be implemented as Python enums or equivalent typed constants in the codebase.

---

## 2. How To Use This Document

- **Implementers**: Import enum definitions from this document into code. Do not invent new enum values without adding them here first.
- **Document Authors**: When referencing a taxonomy, cite this document rather than redefining the enum inline. Use the exact enum names listed below.
- **Reviewers**: Cross-check any enum reference in other documents against this file.

---

# Verdict Enums

## 3. Internal Verdict Taxonomy

These are the canonical internal verdict labels used by the Verdict Engine.

```text
SUPPORTED
REFUTED
PARTIALLY_SUPPORTED
INSUFFICIENT_EVIDENCE
UNVERIFIABLE
```

### SUPPORTED

The material proposition is substantiated by sufficiently strong, independent, temporally valid evidence, with no material unresolved contradiction.

### REFUTED

The material proposition is directly contradicted by sufficiently strong evidence, and the contradiction is not explained by scope, definition, time, or methodology differences.

### PARTIALLY_SUPPORTED

Some material components of the claim are supported while others are unsupported, contradicted, or unresolvable. This verdict also covers cases where the literal content may be accurate but the framing, omission, or context creates a materially distorted interpretation. When framing concerns are present, the verdict metadata should include a `framing_concerns` flag.

> **Design Decision**: The previously considered `MISLEADING` verdict has been deferred to V2. Automated misleading detection requires reasoning capabilities and calibration data that exceed MVP scope. The `framing_concerns` metadata flag preserves the information without introducing an unreliable verdict category. See ADR-001 for rationale.

### INSUFFICIENT_EVIDENCE

Relevant evidence was sought but the available evidence is inadequate for a reliable directional judgment. This requires that the system actually attempted investigation — it is distinct from "no search was performed."

### UNVERIFIABLE

The proposition cannot reasonably be evaluated using available external evidence. Examples include private subjective experiences, unobservable propositions, undefined criteria, and fundamentally inaccessible information.

> **Important**: A system limitation (e.g., search provider failure) must NOT be labeled UNVERIFIABLE. System failures should be reported as infrastructure errors, not epistemic conclusions.

---

## 4. Public Verdict Taxonomy

These are user-facing labels derived from internal verdicts. The mapping is deterministic.

```text
Internal                  → Public
─────────────────────────────────────
SUPPORTED                 → LIKELY TRUE
REFUTED                   → LIKELY FALSE
PARTIALLY_SUPPORTED       → PARTIALLY TRUE
INSUFFICIENT_EVIDENCE     → UNVERIFIED
UNVERIFIABLE              → UNVERIFIABLE
```

### Why "LIKELY"

Web evidence rarely establishes mathematical certainty. "LIKELY TRUE" communicates justified confidence without overclaiming. The calibrated confidence score provides the numerical precision.

---

## 5. Internal Decision States (Granular)

For internal processing, the Verdict Engine may use finer-grained states that are then mapped to the canonical internal verdict.

```text
STRONGLY_SUPPORTED        → SUPPORTED
SUPPORTED                 → SUPPORTED
WEAKLY_SUPPORTED          → SUPPORTED (with lower confidence)

STRONGLY_CONTRADICTED     → REFUTED
CONTRADICTED              → REFUTED
WEAKLY_CONTRADICTED       → REFUTED (with lower confidence)

MIXED                     → PARTIALLY_SUPPORTED
AMBIGUOUS                 → INSUFFICIENT_EVIDENCE
INSUFFICIENT              → INSUFFICIENT_EVIDENCE
OUT_OF_SCOPE              → UNVERIFIABLE
```

These are intermediate processing states, not final output values.

---

## 6. Atomic Claim Verdict

Each atomic claim receives an independent assessment before parent-claim aggregation.

```text
SUPPORTED
REFUTED
CONFLICTED
INSUFFICIENT
UNVERIFIABLE
```

### CONFLICTED

Used when meaningful supporting AND contradicting evidence exists for this atomic claim and the conflict has not been resolved through temporal, definitional, methodological, or provenance analysis.

---

# Evidence Enums

## 7. Evidence Relationship

The relationship between an evidence passage and an atomic claim.

```text
SUPPORTS
PARTIALLY_SUPPORTS
CONTRADICTS
PARTIALLY_CONTRADICTS
QUALIFIES
CONTEXTUALIZES
NEUTRAL
```

### SUPPORTS

The passage provides information that materially increases justification for the proposition. This is stronger than mere topic similarity.

### PARTIALLY_SUPPORTS

The passage supports some aspect of the proposition but not the full claim, or supports it under conditions not stated in the claim.

### CONTRADICTS

The passage materially conflicts with the proposition under compatible entity, time, definition, scope, and measurement conditions.

### PARTIALLY_CONTRADICTS

The passage conflicts with some aspect of the proposition, or conflicts under certain interpretations but not others.

### QUALIFIES

The passage adds a condition or limitation to the claim without fully contradicting it.

Example: Claim "Drug X reduces mortality." Evidence "Drug X reduced mortality only in patients with condition Y."

### CONTEXTUALIZES

The passage provides surrounding context that helps interpret the claim without directly establishing or contradicting it.

### NEUTRAL

The passage is topically related but does not materially bear on the truth of the claim.

---

## 8. Evidence Lifecycle

```text
CANDIDATE
ASSESSED
VALIDATED
AGGREGATED
USED_IN_VERDICT
```

---

## 9. Evidence Rejection Reasons

```text
IRRELEVANT
LOW_QUALITY
DUPLICATE
DERIVATIVE
TEMPORALLY_INVALID
ENTITY_MISMATCH
INSUFFICIENT_CONTEXT
EXTRACTION_ERROR
```

---

## 10. Evidence Sufficiency Dimensions

```text
CLAIM_COVERAGE
SUPPORT_STRENGTH
CONTRADICTION_COVERAGE
SOURCE_QUALITY
INDEPENDENCE
TEMPORAL_VALIDITY
PRIMARY_EVIDENCE
CONFLICT_RESOLUTION
```

---

# Claim Enums

## 11. Claim Type

Multi-label classification. A claim may have multiple labels.

```text
FACTUAL
NUMERICAL
TEMPORAL
COMPARATIVE
CAUSAL
ATTRIBUTION
HISTORICAL
PREDICTIVE
DEFINITIONAL
LEGAL
SCIENTIFIC
POLITICAL
FINANCIAL
MEDICAL
OPINION
NORMATIVE
COMPOUND
```

---

## 12. Claim Verifiability

```text
VERIFIABLE
PARTIALLY_VERIFIABLE
UNVERIFIABLE
SUBJECTIVE
```

---

## 13. Claim Complexity

```text
SIMPLE
MODERATE
COMPLEX
HIGHLY_COMPLEX
```

---

## 14. Atomic Claim Materiality

```text
CRITICAL
MATERIAL
CONTEXTUAL
```

### CRITICAL

Failure or contradiction in this atomic claim fundamentally undermines the parent claim.

### MATERIAL

This atomic claim contributes meaningfully to the parent claim's truth value.

### CONTEXTUAL

This atomic claim provides background or minor detail. Errors in contextual claims may not overturn the parent verdict.

---

# Source Enums

## 15. Source Type

```text
GOVERNMENT
INTERNATIONAL_ORGANIZATION
SCIENTIFIC_JOURNAL
UNIVERSITY
NEWS_WIRE
NEWS_ORGANIZATION
COMPANY_OFFICIAL
REGULATORY_FILING
LEGAL_DOCUMENT
REFERENCE_WORK
BLOG
SOCIAL_MEDIA
FORUM
WIKI
AGGREGATOR
UNKNOWN
```

---

## 16. Source Authority Class

```text
PRIMARY
SECONDARY
TERTIARY
DERIVATIVE
UNKNOWN
```

### PRIMARY

The originating source of the information (e.g., government report, original research paper, official filing).

### SECONDARY

Independent reporting or analysis of primary information (e.g., news coverage of a government report).

### TERTIARY

Compilation or summary of secondary sources (e.g., encyclopedia, textbook).

### DERIVATIVE

Content that reproduces or paraphrases other sources without independent verification or analysis.

---

# Research Enums

## 17. Research Objective

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

---

## 18. Research Task Type

```text
SEARCH_SUPPORT
SEARCH_CONTRADICTION
SEARCH_PRIMARY
SEARCH_ENTITY
SEARCH_TEMPORAL
SEARCH_CONFLICT
FETCH_DOCUMENT
FOLLOW_CITATION
VERIFY_NUMERIC_VALUE
```

---

## 19. Research Action Type

```text
SEARCH
SEARCH_PRIMARY_SOURCE
SEARCH_CONTRADICTION
SEARCH_TEMPORAL
SEARCH_NUMERICAL
SEARCH_ENTITY
FETCH_DOCUMENT
RETRY
RERANK
RESOLVE_ENTITY
RESOLVE_CONFLICT
STOP
```

---

## 20. Research Stop Reason

```text
SUFFICIENT_EVIDENCE
STRONG_CONTRADICTION
RESOLVED_CONFLICT
UNVERIFIABLE
BUDGET_EXHAUSTED
LOW_EXPECTED_VALUE
TIMEOUT
SYSTEM_LIMIT
NO_RELEVANT_SOURCES
```

---

## 21. Research State

```text
RECEIVED
ANALYZING
PLANNED
RESEARCHING
EVALUATING
CONFLICT_RESOLUTION
RECOVERY
READY_FOR_VERDICT
VERDICT
COMPLETED
FAILED
CANCELLED
TIMEOUT
PARTIAL
```

---

## 22. Research Depth

```text
DEPTH_0     # Basic validation (trivially false/true)
DEPTH_1     # Single-stage retrieval
DEPTH_2     # Multi-source evidence assessment
DEPTH_3     # Contradiction + primary-source search
DEPTH_4     # Adaptive deep research
```

---

## 23. Research Mode (Product)

```text
FAST        # Minimal search depth, optimized for latency
STANDARD    # Balanced evidence acquisition
DEEP        # High coverage and contradiction investigation
```

---

# Conflict Enums

## 24. Conflict Type

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

## 25. Conflict Severity

```text
CRITICAL
MAJOR
MINOR
```

---

## 26. Conflict Resolution Status

```text
UNRESOLVED
RESOLVED_TEMPORAL
RESOLVED_DEFINITION
RESOLVED_METHODOLOGY
RESOLVED_ENTITY
RESOLVED_SCOPE
UNRESOLVABLE
```

---

# Provenance Enums

## 27. Provenance Relationship

```text
DERIVED_FROM
CITES
QUOTES
DUPLICATES
CONTRADICTS
SUPPORTS
QUALIFIES
```

---

## 28. Provenance Detection Method (MVP)

For MVP, provenance detection uses only:

```text
URL_DOMAIN_CLUSTERING
EXACT_QUOTATION_OVERLAP
```

V2 will add:

```text
CITATION_GRAPH
SEMANTIC_SIMILARITY
PUBLICATION_METADATA
EXPLICIT_ATTRIBUTION
```

---

# Infrastructure Enums

## 29. Request Status

```text
QUEUED
RUNNING
RESEARCHING
ASSESSING
VERDICTING
COMPLETED
FAILED
CANCELLED
TIMEOUT
PARTIAL
```

---

## 30. Request Type

```text
SYNC_FAST
SYNC_STANDARD
ASYNC_DEEP
BATCH
```

---

## 31. Model Lifecycle

```text
REGISTERED
DOWNLOADING
LOADED
WARM
SERVING
UNLOADING
FAILED
```

---

## 32. Priority Class

```text
P0_CRITICAL
P1_PREMIUM
P2_STANDARD
P3_BACKGROUND
```

---

# Failure Enums

## 33. Retrieval Failure Mode

```text
RF_001_QUERY_FAILURE
RF_002_SEARCH_FAILURE
RF_003_RANKING_FAILURE
RF_004_EXTRACTION_FAILURE
RF_005_PASSAGE_FAILURE
RF_006_DUPLICATE_FAILURE
RF_007_TEMPORAL_FAILURE
RF_008_SOURCE_FAILURE
RF_009_DOMAIN_FAILURE
RF_010_ADVERSARIAL_RETRIEVAL
```

---

## 34. Evidence Failure Mode

```text
WRONG_PASSAGE
WRONG_ENTITY
WRONG_TIME
WRONG_DEFINITION
FALSE_ENTAILMENT
MISSED_CONTRADICTION
SOURCE_OVERTRUST
SOURCE_UNDERTRUST
DOUBLE_COUNTING
PROVENANCE_ERROR
TEMPORAL_ERROR
CONTEXT_LOSS
NUMERICAL_MISMATCH
CAUSAL_OVERCLAIM
ATTRIBUTION_ERROR
```

---

## 35. Verdict Failure Mode

```text
FALSE_SUPPORT
FALSE_REFUTATION
OVERCONFIDENCE
UNDERCONFIDENCE
DOUBLE_COUNTING
MISSED_CONTRADICTION
WRONG_MATERIALITY
WRONG_ATOMIC_AGGREGATION
TEMPORAL_ERROR
SOURCE_WEIGHTING_ERROR
PROVENANCE_ERROR
DEFINITION_ERROR
CAUSAL_OVERCLAIM
INSUFFICIENT_EVIDENCE_ERROR
UNVERIFIABLE_ERROR
```

---

## 36. Agent Failure Mode

```text
BAD_PLAN
WRONG_TASK_PRIORITY
PREMATURE_STOP
OVER_RESEARCH
TOOL_MISSELECTION
QUERY_REPETITION
CONFIRMATION_BIAS
MISSED_CONTRADICTION
MISSED_PRIMARY_SOURCE
BUDGET_WASTE
FAILURE_RECOVERY_ERROR
STATE_CORRUPTION
```

---

# 37. Enum Governance

### Adding New Values

1. Define the value in this document first.
2. Add a one-line description.
3. Update the corresponding Python enum in the codebase.
4. Update any dependent documentation.

### Removing Values

1. Mark as `DEPRECATED` in this document with a migration note.
2. Remove from code only after all references are updated.

### Renaming Values

1. Add the new name alongside the old name marked `DEPRECATED`.
2. Update code to support both during migration.
3. Remove the old name after one release cycle.

---

# 38. Cross-Reference

This document is referenced by:

- `02-problem-definition.md` — Verdict taxonomy
- `03-requirements.md` — All functional classification enums
- `04-domain-model.md` — Evidence relationship, materiality, source types
- `05-verification-methodology.md` — Verdict taxonomy, evidence lifecycle
- `07-evidence-model.md` — Evidence relationship, sufficiency dimensions
- `09-verdict-engine.md` — Verdict taxonomy, decision states
- `12-data-architecture.md` — Evidence relationship, conflict types
- `14-evidence-engineering.md` — Evidence relationship, lifecycle
- `15-query-and-claim-intelligence.md` — Claim type taxonomy
- `17-verdict-engine-and-calibration.md` — Verdict classes, decision states
- `18-research-orchestrator.md` — Research state, action types, stop reasons
- `24-api-and-product-contracts.md` — Public verdict taxonomy
