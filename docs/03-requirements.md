# Tathvyn — Product & System Requirements

## 1. Purpose

This document translates the Tathvyn product vision and problem definition into explicit, testable requirements.

Requirements are divided into:

- Functional Requirements (FR)
- Quality Requirements (QR)
- Non-Functional Requirements (NFR)
- Security Requirements (SEC)
- Observability Requirements (OBS)
- Evaluation Requirements (EV)
- Product and Scalability Constraints (PSC)

These requirements are implementation-agnostic. Specific models, frameworks, databases, search providers, and infrastructure choices must be justified against them.

---

# 2. Product Requirements

## 2.1 Verification Request

### FR-001 — Claim Submission

The system SHALL accept a user-provided claim for verification.

Supported initial input forms:

- plain text;
- a factual statement;
- a question containing an implicit factual claim.

The system SHALL preserve the original user input for auditability.

### FR-002 — Request Identity

Every verification request SHALL receive a unique request identifier.

The identifier SHALL allow all downstream operations to be associated with the originating request.

### FR-003 — Input Validation

The system SHALL reject malformed, empty, excessively large, or unsupported requests before expensive processing begins.

### FR-004 — Input Normalization

The system SHALL produce a normalized representation of the submitted claim without destroying the original input.

Normalization MAY include:

- whitespace normalization;
- quotation normalization;
- linguistic cleanup;
- removal of verification framing such as "is it true that";
## FR-004b — Language Scope and Rejection
The system SHALL detect input language and enforce English-first processing in MVP. Non-English claims ($\ge 0.85$ confidence) SHALL be rejected with structured code `UNSUPPORTED_LANGUAGE` as specified in [00-language-and-scope.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-language-and-scope.md).

---

# 3. Claim Understanding Requirements

## FR-005 — Claim Classification

The system SHALL classify the claim into one or more relevant semantic categories.

Initial categories:

- FACTUAL
- NUMERICAL
- TEMPORAL
- CAUSAL
- ATTRIBUTION
- HISTORICAL
- COMPARATIVE
- PREDICTIVE
- OPINION
- COMPOUND

The representation SHALL allow multi-label classification in future versions.

## FR-006 — Verifiability Assessment

The system SHALL determine whether the claim is:

- VERIFIABLE;
- PARTIALLY_VERIFIABLE;
- TIME_DEPENDENT;
- CONTEXT_DEPENDENT;
- UNVERIFIABLE.

The system SHOULD avoid expensive research for claims that are clearly unverifiable.

## FR-007 — Atomic Claim Decomposition

The system SHALL identify independently verifiable propositions within compound claims.

Each atomic claim SHALL have a unique identifier and remain traceable to its parent claim.

## FR-007b — Single-Element Decomposition and Max Depth
If a claim is already atomic (contains exactly one proposition), the system SHALL generate a single-element atomic claim list with `is_atomic=True`. The system SHALL enforce a maximum decomposition depth of 1 (atomic claims SHALL NOT be recursively decomposed). All generated atomic sub-claims SHALL be verified against the parent claim to prevent hallucinated sub-propositions.

## FR-008 — Atomic Claim Coverage

The system SHALL determine whether all materially important components of the original claim have been represented by atomic claims.

## FR-009 — Entity Identification

The system SHALL identify relevant entities appearing in claims.

Initial entity classes SHOULD include:

- PERSON
- ORGANIZATION
- LOCATION
- PRODUCT
- EVENT
- GOVERNMENT_ENTITY
- FINANCIAL_ENTITY
- SCIENTIFIC_ENTITY
- OTHER

## FR-010 — Entity Disambiguation

Where an entity mention is ambiguous, the system SHALL represent the ambiguity rather than silently selecting an arbitrary entity.

## FR-011 — Temporal Extraction

The system SHALL identify explicit and implicit temporal constraints.

Examples:

- specific dates;
- years;
- date ranges;
- "currently";
- "recently";
- "last year";
- "before";
- "after";
- historical periods.

## FR-012 — Claim Context

The system SHOULD preserve qualifiers that materially affect interpretation.

Examples:

- "according to";
- "approximately";
- "at least";
- "only";
- "primarily";
- "in real terms";
- geographic constraints;
- population constraints.

---

# 4. Research Planning Requirements

## FR-013 — Research Plan

The system SHALL generate a research plan appropriate to the claim.

A research plan SHOULD specify:

- atomic claims requiring investigation;
- search objectives;
- source preferences;
- contradiction checks;
- primary-source requirements;
- temporal constraints;
- expected research depth.

## FR-014 — Supporting Search

The system SHALL be capable of generating searches intended to locate evidence supporting a claim.

## FR-015 — Contradiction Search

The system SHALL be capable of generating searches specifically intended to locate evidence contradicting a claim.

Contradiction search SHALL be treated as a first-class research objective rather than an optional afterthought.

## FR-016 — Primary-Source Search

Where appropriate, the system SHALL prioritize discovery of primary or closest-available sources.

## FR-017 — Domain-Aware Search

The research planner SHOULD route claims toward domain-appropriate sources.

Examples:

- scientific claims → scientific literature;
- financial claims → financial and regulatory sources;
- government claims → official government sources;
- historical claims → archival and scholarly sources.

## FR-018 — Adaptive Research

The research process SHALL be capable of generating additional research tasks after evaluating initial evidence.

Additional research SHOULD occur when:

- evidence conflicts;
- source quality is insufficient;
- important atomic claims remain unresolved;
- primary evidence is missing;
- temporal validity is uncertain;
- evidence coverage is inadequate.

---

# 5. Retrieval Requirements

## FR-019 — Multi-Source Retrieval

The system SHALL support retrieval from multiple independent search or information sources.

No single external search provider SHALL be a mandatory single point of failure.

## FR-020 — Hybrid Retrieval

The retrieval architecture SHOULD support combining lexical and semantic retrieval where beneficial.

Potential mechanisms include:

- BM25;
- dense embeddings;
- learned reranking.

The final implementation SHALL be determined through evaluation.

## FR-021 — Passage-Level Retrieval

The system SHALL support passage-level evidence retrieval rather than treating an entire document as a single evidence unit.

## FR-022 — Retrieval Metadata

Every retrieved document SHALL retain metadata sufficient for later evaluation.

At minimum:

- URL;
- canonical URL where available;
- title;
- source;
- publication time where available;
- retrieval time;
- retrieval method;
- query that retrieved it.

## FR-023 — Retrieval Deduplication

The system SHALL detect obvious duplicate URLs and substantially duplicated documents.

## FR-024 — Search Result Provenance

The system SHALL preserve which query and retrieval mechanism produced each document.

## FR-025 — Retrieval Failure Handling

The system SHALL distinguish between:

- no relevant result;
- provider failure;
- fetch failure;
- extraction failure;
- blocked content;
- malformed content.

These states SHALL NOT be silently collapsed into "no evidence."

---

# 6. Document Processing Requirements

## FR-026 — Document Acquisition

The system SHALL retrieve accessible source documents when required for verification.

## FR-027 — Content Extraction

The system SHALL extract the main textual content while minimizing navigation, advertisements, boilerplate, and unrelated page content.

## FR-028 — Extraction Status

Each document SHALL record extraction status.

Initial states:

- SUCCESS;
- PARTIAL;
- FAILED;
- BLOCKED;
- PAYWALLED;
- EMPTY;
- UNSUPPORTED.

## FR-029 — Content Integrity

The system SHOULD retain a content hash or equivalent fingerprint for duplicate detection and reproducibility.

## FR-030 — Document Freshness

The system SHALL preserve publication, modification, and retrieval timestamps when available.

---

# 7. Evidence Requirements

## FR-031 — Evidence Extraction

The system SHALL extract candidate passages that can materially affect an atomic claim.

## FR-032 — Evidence Classification

Each candidate evidence item SHALL be classified relative to an atomic claim according to the canonical taxonomy in [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md):

- SUPPORTS;
- PARTIALLY_SUPPORTS;
- CONTRADICTS;
- PARTIALLY_CONTRADICTS;
- QUALIFIES;
- CONTEXTUALIZES;
- NEUTRAL.

Rejected candidate passages SHALL record an explicit rejection reason (e.g. `IRRELEVANT`, `LOW_QUALITY`, `DUPLICATE`, `TEMPORALLY_INVALID`).

## FR-033 — Evidence Traceability

Every evidence item SHALL be traceable to:

```text
Claim
  ↓
Atomic Claim
  ↓
Evidence
  ↓
Passage
  ↓
Document
  ↓
Source
```

## FR-034 — Evidence Assessment

Evidence SHALL be evaluated using multiple dimensions rather than a single similarity score.

Initial dimensions:

- relevance;
- entailment;
- contradiction;
- specificity;
- source quality;
- source independence;
- temporal validity;
- provenance;
- consistency.

## FR-035 — Evidence Coverage

The system SHALL determine which atomic claims are adequately covered by evidence and which remain unresolved.

## FR-036 — Supporting and Contradicting Sets

The system SHALL maintain separate supporting and contradicting evidence sets for each atomic claim.

---

# 8. Source Requirements

## FR-037 — Source Identification

The system SHALL maintain a canonical representation of sources where possible.

## FR-038 — Source Classification

Sources SHOULD be classified into categories such as:

- GOVERNMENT;
- ACADEMIC;
- SCIENTIFIC_JOURNAL;
- PRIMARY_DOCUMENT;
- NEWS_ORGANIZATION;
- CORPORATE;
- NGO;
- EXPERT;
- SOCIAL_MEDIA;
- BLOG;
- FORUM;
- UNKNOWN.

Source category SHALL be treated as a feature, not an absolute truth label.

## FR-039 — Source Quality Assessment

The system SHALL maintain source-quality signals.

Potential signals include:

- authority;
- expertise;
- primary-source status;
- methodological transparency;
- publication quality;
- recency;
- domain relevance.

## FR-040 — Source Independence

The system SHALL attempt to determine whether multiple sources represent independent evidence.

## FR-041 — Syndication Detection

The system SHOULD identify duplicated, syndicated, or derivative reporting where technically feasible.

## FR-042 — Provenance Groups

Related documents SHOULD be associated with provenance groups representing a common underlying origin.

---

# 9. Temporal Verification Requirements

## FR-043 — Temporal Alignment

Evidence SHALL be evaluated against the temporal scope of the claim.

## FR-044 — Current-State Verification

Claims involving "currently", "today", or equivalent temporal language SHALL use appropriately fresh evidence.

## FR-045 — Historical Verification

Historical claims SHOULD prefer evidence appropriate to the historical period being investigated.

## FR-046 — Stale Evidence Detection

Evidence that may be outdated SHALL be identified and its relevance reduced or explicitly surfaced.

---

# 10. Verdict Requirements

## FR-047 — Atomic Verdict

Each atomic claim SHALL receive an internal verification state.

## FR-048 — Overall Verdict

The system SHALL derive an overall verdict from the state of the atomic claims and their evidence according to [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md).

Canonical internal verdicts:

- SUPPORTED;
- REFUTED;
- PARTIALLY_SUPPORTED;
- INSUFFICIENT_EVIDENCE;
- UNVERIFIABLE.

Public user-facing verdicts (mapped deterministically):

- LIKELY TRUE;
- LIKELY FALSE;
- PARTIALLY TRUE;
- UNVERIFIED;
- UNVERIFIABLE.

> Distorted/framing claims are classified under `PARTIALLY_SUPPORTED` with a `framing_concerns` flag in MVP. Standalone `MISLEADING` verdict classification is deferred to V2.

## FR-049 — No-Evidence Distinction

The system SHALL distinguish:

- evidence of contradiction;
- absence of supporting evidence;
- insufficient research;
- genuinely unavailable evidence.

## FR-050 — Contradiction Handling

When strong evidence conflicts, the system SHALL preserve the conflict rather than arbitrarily selecting one source.

## FR-051 — Verdict Traceability

Every verdict SHALL be explainable through the evidence and intermediate assessments that produced it.

---

# 11. Confidence and Uncertainty Requirements

## FR-052 — Confidence

The system SHALL provide a calibrated confidence representation once sufficient evaluation data exists.

## FR-053 — Uncertainty Decomposition

The system SHOULD identify important sources of uncertainty, such as:

- evidence scarcity;
- source disagreement;
- temporal uncertainty;
- entity ambiguity;
- claim ambiguity;
- weak source quality;
- lack of primary evidence.

## FR-054 — Calibration

Confidence SHALL be evaluated empirically.

Potential metrics:

- Expected Calibration Error;
- Brier score;
- reliability diagrams.

## FR-055 — No False Precision

The system SHALL NOT represent an uncalibrated model score as a literal probability of truth.

---

# 12. Research Controller Requirements

## FR-056 — Evidence Sufficiency

The system SHALL evaluate whether available evidence is sufficient to support a verdict.

## FR-057 — Research Continuation

The controller SHALL be able to request additional research when evidence is insufficient.

## FR-058 — Research Stopping

The controller SHALL be able to stop research when:

- evidence is sufficiently strong;
- additional research has low expected value;
- the verification budget is exhausted;
- the claim is determined to be unverifiable;
- or a sufficient stopping policy condition is reached.

## FR-059 — Research Budget

Each verification SHALL operate within a resource budget.

The budget MAY include:

- search calls;
- documents;
- passages;
- model inferences;
- LLM calls;
- tokens;
- latency;
- monetary cost;
- research depth.

## FR-060 — Cost-Aware Research

The controller SHOULD consider the expected information value of additional research relative to its cost.

---

# 13. Explanation Requirements

## FR-061 — Grounded Explanation

The system SHALL generate explanations grounded in the evidence used for the verdict.

## FR-062 — Evidence Citations

Explanations SHALL cite the relevant evidence and source.

## FR-063 — Contradiction Disclosure

Material contradictory evidence SHOULD be disclosed to the user.

## FR-064 — Uncertainty Disclosure

Important unresolved issues SHALL be surfaced rather than hidden.

## FR-065 — Concise and Detailed Views

The product SHOULD eventually support:

- concise verdict;
- detailed evidence analysis.

---

# 14. API and Product Requirements

## FR-066 — Programmatic Verification

The system SHALL expose a programmatic interface for claim verification.

## FR-067 — Structured Response

The verification response SHALL be machine-readable and contain, at minimum:

- request identifier;
- claim;
- verdict;
- confidence when calibrated;
- evidence;
- sources;
- unresolved issues;
- processing status.

## FR-068 — Health Monitoring

The system SHALL expose service health and dependency status.

## FR-069 — Asynchronous Verification

The product SHOULD support asynchronous processing for deep investigations that exceed interactive latency targets.

---

# 15. Quality Requirements

## QR-001 — Evidence Grounding

The final verdict must be grounded in retrieved evidence.

## QR-002 — Reproducibility

Given the same evidence snapshot, model versions, configuration, and policy, the system SHOULD produce reproducible results within defined tolerance.

## QR-003 — Robustness

The system SHOULD be robust to:

- paraphrased claims;
- noisy wording;
- conflicting sources;
- duplicate sources;
- outdated sources;
- ambiguous entities;
- adversarial content.

## QR-004 — Graceful Uncertainty

When evidence is insufficient, the system SHOULD prefer uncertainty over unsupported confidence.

## QR-005 — Explainability

A reviewer SHOULD be able to trace a verdict to its supporting and contradicting evidence.

---

# 16. Non-Functional Requirements

## NFR-001 — Latency

The system SHALL measure:

- p50 latency;
- p95 latency;
- p99 latency where appropriate.

Interactive and deep-research workloads SHOULD have separate latency targets.

Exact targets will be established through benchmarking.

## NFR-002 — Throughput

The system SHALL be designed so verification capacity can scale independently of user traffic.

## NFR-003 — Horizontal Scalability

Stateless verification components SHOULD be horizontally scalable where practical.

## NFR-004 — Fault Tolerance

Failure of an individual search provider, worker, model service, or scraper SHALL NOT unnecessarily terminate the entire verification process.

## NFR-005 — Graceful Degradation

When optional dependencies fail, the system SHOULD degrade in capability rather than fabricate certainty.

## NFR-006 — Cost Efficiency

The system SHALL track cost per verification.

Cost SHALL be considered alongside quality and latency.

## NFR-007 — Caching

The architecture SHOULD support caching of reusable:

- normalized claims;
- verification results;
- documents;
- passages;
- embeddings;
- source metadata.

Caching SHALL account for freshness and temporal sensitivity.

## NFR-008 — Batch Inference

Model-serving components SHOULD support batching where it improves throughput and cost efficiency.

## NFR-009 — Model Abstraction

Core services SHALL avoid unnecessary coupling to one model or provider.

## NFR-010 — Configuration

Models, thresholds, budgets, retrieval policies, and provider settings SHOULD be externally configurable.

---

# 17. Security Requirements

## SEC-001 — Untrusted Web Content

Retrieved web content SHALL be treated as untrusted data.

## SEC-002 — Prompt Injection Isolation

Instructions contained inside retrieved documents SHALL NOT automatically become instructions to the verification agent.

## SEC-003 — Secret Protection

API keys, credentials, and provider secrets SHALL NOT be embedded in source code or logged.

## SEC-004 — Input Abuse Protection

The system SHOULD protect against:

- request flooding;
- oversized inputs;
- abusive research requests;
- resource exhaustion.

## SEC-005 — Source Integrity

The system SHOULD preserve source URLs, retrieval timestamps, and content fingerprints to support auditability.

---

# 18. Observability Requirements

## OBS-001 — End-to-End Trace

Each verification SHALL have a trace connecting:

```text
request
→ claim
→ atomic claims
→ research plan
→ queries
→ search results
→ documents
→ evidence
→ assessments
→ verdict
```

## OBS-002 — Cost Telemetry

The system SHALL record resource usage such as:

- search calls;
- documents fetched;
- model inference counts;
- LLM calls;
- tokens;
- estimated monetary cost.

## OBS-003 — Latency Telemetry

Latency SHALL be measurable per pipeline stage.

## OBS-004 — Failure Telemetry

Failures SHALL be categorized by component and failure type.

## OBS-005 — Model Versioning

Model versions SHALL be included in relevant traces and evaluation records.

---

# 19. Evaluation Requirements

## EV-001 — Component-Level Evaluation

Each major subsystem SHALL have an independent evaluation set.

## EV-002 — End-to-End Evaluation

The complete system SHALL be evaluated on claims with trusted reference verdicts and evidence where available.

## EV-003 — Retrieval Evaluation

Retrieval SHOULD be evaluated using:

- Recall@K;
- MRR;
- nDCG;
- evidence coverage.

## EV-004 — Classification Evaluation

Claim and evidence classification SHOULD use:

- precision;
- recall;
- F1;
- Macro-F1;
- confusion matrices.

## EV-005 — Calibration Evaluation

Confidence SHOULD be evaluated using:

- ECE;
- Brier score;
- reliability curves.

## EV-006 — Cost Evaluation

Experiments SHALL measure:

- average cost per verification;
- cost by claim complexity;
- search calls per verification;
- model inference cost;
- cache savings.

## EV-007 — Latency Evaluation

Experiments SHALL report latency distributions rather than only averages.

## EV-008 — Ablation Evaluation

The system SHOULD support experiments removing or replacing major components to determine their marginal contribution.

## EV-009 — Robustness Evaluation

The benchmark SHOULD include:

- ambiguous claims;
- contradictory evidence;
- duplicated sources;
- outdated evidence;
- adversarial claims;
- difficult temporal claims;
- difficult numerical claims;
- compound claims.

---

# 20. Product and Scalability Constraints

## PSC-001 — Quality Before Arbitrary Cost Minimization

The system SHALL NOT sacrifice material verification quality solely to minimize infrastructure cost.

## PSC-002 — Cost-Aware Quality

The system SHOULD maximize verification quality per unit of resource.

## PSC-003 — Tiered Verification

The architecture SHOULD support multiple verification depths.

## PSC-004 — Reusable Work

Expensive work that can safely be reused SHOULD be cached.

## PSC-005 — Resource Budgets

Deep research SHALL have explicit resource limits.

## PSC-006 — Async Deep Research

Investigations that cannot meet interactive latency targets SHOULD be capable of asynchronous execution.

## PSC-007 — Provider Independence

External providers SHOULD be abstracted so they can be replaced, combined, or disabled.

---

# 21. Initial Quality Gates

Exact numerical targets will be determined after benchmark construction.

However, the project SHALL eventually define gates for:

```text
Claim Understanding
        ↓
Retrieval Quality
        ↓
Evidence Assessment
        ↓
Source/Provenance Quality
        ↓
Verdict Quality
        ↓
Calibration
        ↓
Latency
        ↓
Cost
        ↓
Scalability
```

A new architecture or model should be accepted based on measured improvement against these gates, not subjective impressions.

---

# 22. Requirement Traceability

Every major implementation component should map back to one or more requirements.

Example:

```text
Research Controller
    ├── FR-056 Evidence Sufficiency
    ├── FR-057 Research Continuation
    ├── FR-058 Research Stopping
    ├── FR-059 Research Budget
    └── FR-060 Cost-Aware Research
```

This prevents unnecessary architectural complexity.

---

# 23. Definition of Done

A verification capability should not be considered complete merely because it works on a few examples.

A subsystem is considered production-ready only when:

1. its behavior is specified;
2. its interfaces are defined;
3. failure modes are identified;
4. unit and integration tests exist;
5. benchmark evaluation exists where applicable;
6. observability exists;
7. cost and latency are measurable;
8. relevant security concerns are addressed;
9. model/provider dependencies are explicit;
10. documented limitations exist.

---

# 24. Engineering Principle

> **Every feature must solve a defined problem, every expensive component must justify its cost, and every quality claim must be backed by measurement.**

This requirements document is the contract from which the Tathvyn domain model and system architecture should be derived.
