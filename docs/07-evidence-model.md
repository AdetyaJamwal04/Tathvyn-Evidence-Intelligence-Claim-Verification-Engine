# Tathvyn — Evidence Model

## 1. Purpose

This document defines how Tathvyn represents, evaluates, relates, and aggregates evidence.

Evidence is the central object of the verification system.

The core distinction is:

```text
Document ≠ Evidence
Source ≠ Evidence
Search Result ≠ Evidence
Embedding Similarity ≠ Evidence
LLM Opinion ≠ Evidence
```

Evidence is a **claim-relative, passage-level information object** whose relationship to an atomic claim can be explicitly assessed.

---

# 2. Evidence Principle

The system should answer:

> **What does this specific passage, from this specific source, at this specific point in time, actually establish about this atomic claim?**

rather than:

> "Is this webpage trustworthy?"

or:

> "Does this passage sound similar to the claim?"

---

# 3. Evidence Lifecycle

```text
Retrieved Document
        ↓
Document Extraction
        ↓
Passage Segmentation
        ↓
Candidate Passage Selection
        ↓
Evidence Candidate
        ↓
Claim-Relative Assessment
        ↓
Source Assessment
        ↓
Temporal Assessment
        ↓
Provenance Analysis
        ↓
Evidence Object
        ↓
Evidence Graph
        ↓
Evidence Aggregation
        ↓
Atomic Verdict
```

---

# 4. Evidence Candidate vs Evidence

The system should distinguish:

### Candidate Evidence

A passage that appears potentially relevant.

### Validated Evidence

A passage whose relationship to an atomic claim has been assessed sufficiently for use in verification.

This distinction prevents weak retrieval results from directly influencing the final verdict.

---

# 5. Evidence Object

Conceptual structure:

```text
Evidence
├── evidence_id
├── atomic_claim_id
├── document_id
├── passage_id
├── source_id
├── relationship
├── relevance
├── entailment
├── contradiction
├── specificity
├── temporal_validity
├── source_quality
├── independence
├── provenance
├── extraction_metadata
└── assessment_metadata
```

The object should remain traceable to its exact passage.

---

# 6. Evidence Relationship

The canonical relationship taxonomy is defined in [00-canonical-enums.md](./00-canonical-enums.md).

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

These relationships are always relative to a particular atomic claim.

The same passage may:

```text
support AtomicClaim A
```

while:

```text
contradict AtomicClaim B
```

Therefore evidence must not have a global "truth label."

---

# 7. Evidence Dimensions

Evidence should be assessed along independent dimensions:

```text
Relevance
Entailment
Contradiction
Specificity
Temporal Validity
Source Quality
Independence
Provenance Confidence
Claim Coverage
```

These dimensions should initially remain separate.

Prematurely collapsing them into one score makes debugging and scientific evaluation difficult.

---

# 8. Relevance

Relevance asks:

> **Does the evidence concern the same subject, predicate, context, and proposition as the atomic claim?**

Relevance should consider:

- entity overlap;
- semantic similarity;
- domain;
- geography;
- temporal scope;
- terminology;
- claim structure.

---

# 9. Semantic Similarity

Embeddings can estimate semantic similarity between:

```text
Atomic Claim
        ↕
Passage
```

However:

> **Semantic similarity is a retrieval signal, not a verification signal.**

Example:

Claim:

> "The company reduced prices by 20%."

Passage:

> "The company discussed a possible 20% price reduction."

High similarity does not imply that the reduction actually occurred.

---

# 10. Entailment

Entailment asks:

> **Assuming the passage is accurate, does it support the proposition expressed by the atomic claim?**

Potential states:

```text
ENTAILED
PARTIALLY_ENTAILED
NOT_ENTAILED
UNKNOWN
```

The evidence model should distinguish partial entailment from complete entailment.

---

# 11. Contradiction

Contradiction asks:

> **Does the passage assert a proposition incompatible with the atomic claim under the same relevant conditions?**

Potential states:

```text
CONTRADICTED
PARTIALLY_CONTRADICTED
NOT_CONTRADICTED
UNKNOWN
```

Contradiction must account for:

- time;
- geography;
- definitions;
- entities;
- qualifiers;
- measurement methodology.

---

# 12. Neutral Evidence

A passage may be relevant without supporting or contradicting a claim.

Example:

Claim:

> "GDP grew by 8.2%."

Passage:

> "GDP growth is calculated using national accounts."

This is useful methodological context but does not establish the value.

Therefore:

```text
RELEVANT ≠ SUPPORTING
```

---

# 13. Specificity

Specificity asks:

> **How directly does the evidence address the exact proposition?**

Conceptually:

```text
High specificity:
"The official 2024 GDP growth rate was 8.2%."

Medium:
"India recorded strong GDP growth in 2024."

Low:
"India has experienced rapid economic growth."
```

Specificity is especially important for numerical and attribution claims.

---

# 14. Claim Coverage

A single passage may cover:

- the whole atomic claim;
- one component;
- several components;
- contextual requirements.

Coverage should be represented explicitly.

Example:

```text
Atomic Claim:
"X acquired Y for $10B in 2025."

Evidence A:
"X acquired Y."
→ acquisition component covered

Evidence B:
"The deal was valued at $10B."
→ monetary component covered

Evidence C:
"The acquisition closed in 2025."
→ temporal component covered
```

---

# 15. Temporal Validity

Evidence validity depends on time.

The assessment should consider:

```text
Claim temporal scope
Evidence publication time
Evidence observation time
Evidence validity interval
Retrieval time
```

A document published today may describe a historical event accurately.

A document published years ago may still be authoritative for that historical event.

Therefore:

> **Publication recency and factual temporal relevance are different concepts.**

---

# 16. Source Quality

Source quality should be claim-relative.

Potential dimensions:

```text
Authority
Expertise
Primary-source status
Methodological transparency
Editorial standards
Domain relevance
Historical reliability
```

Example:

A government source may be highly relevant for:

```text
official policy
```

while a peer-reviewed study may be stronger for:

```text
scientific causal claims
```

---

# 17. Source Quality Must Not Be Absolute

Avoid:

```text
Government = trustworthy
Blog = untrustworthy
```

Instead:

```text
Source
   +
Claim Type
   +
Domain
   +
Evidence Type
   +
Context
   ↓
Source Utility
```

A source can be highly authoritative for one type of information and weak for another.

---

# 18. Primary Evidence

Primary evidence is evidence closest to the underlying event, measurement, statement, or decision.

Examples:

```text
Official dataset
Government notification
Original research paper
Court judgment
Company filing
Original transcript
Archival document
```

Primary does not automatically mean correct.

It means:

> **closer to the underlying information origin.**

---

# 19. Secondary Evidence

Secondary evidence interprets, reports, or summarizes primary evidence.

Examples:

```text
News article
Research review
Analytical report
Expert commentary
Institutional summary
```

Secondary evidence can be highly valuable, especially when primary evidence is difficult to interpret.

---

# 20. Source Independence

Independence asks:

> **Does this evidence provide information materially independent of evidence already considered?**

Potential states:

```text
INDEPENDENT
DEPENDENT
LIKELY_DEPENDENT
UNKNOWN
```

Independence is a relationship, not a property of a source alone.

---

# 21. Provenance

Provenance tracks where information originated.

Example:

```text
Original Government Report
          │
          ├── News Article A
          │
          ├── News Article B
          │
          └── Blog C
```

A, B, and C may all represent one underlying evidence event.

Therefore:

```text
4 documents
≠
4 independent confirmations
```

---

# 22. Provenance Confidence

Provenance analysis itself can be uncertain.

Example:

```text
Likely same origin → 0.91
Possibly related → 0.62
Unknown → insufficient information
```

The provenance confidence should remain distinct from factual confidence.

---

# 23. Evidence Clustering

Evidence should be clusterable by information origin.

Potential clustering signals:

- shared citations;
- identical quotations;
- shared statistics;
- URL references;
- publication timestamps;
- textual similarity;
- named original source;
- identical methodology.

Conceptually:

```text
Evidence Cluster A
├── Source A
├── Source B
└── Source C

Evidence Cluster B
├── Source D
└── Source E
```

Cluster-level corroboration is more meaningful than raw document count.

> **MVP Clustering Implementation**: For MVP, evidence clustering utilizes deterministic URL-domain grouping and exact quotation/statistic substring matching. Neural cross-document coreference and citation graph mining are scheduled for V2.

---

# 24. Independent Evidence Units

A future aggregation system should reason over:

```text
Independent Evidence Units
```

rather than URLs.

An evidence unit may be:

- an original dataset;
- an independent study;
- an independent official statement;
- an independent reporting investigation.

---

# 25. Evidence Strength

Evidence strength should represent how materially an evidence item bears on an atomic claim.

Conceptually:

```text
Evidence Strength
=
Claim Relevance
×
Entailment / Contradiction
×
Specificity
×
Temporal Validity
```

Source quality and independence should be considered separately during aggregation.

This conceptual separation prevents one source score from dominating the entire system.

---

# 26. Support and Contradiction Are Symmetric

The evidence model should represent:

```text
Support Evidence
```

and:

```text
Contradiction Evidence
```

using the same conceptual framework.

This avoids confirmation-oriented verification.

---

# 27. Contradiction Search Must Be Active

The system should not wait for contradictions to appear accidentally.

For material claims:

```text
Search Support
       +
Search Contradiction
       +
Search Primary Source
```

All three should contribute to the evidence state.

---

# 28. Conflict Taxonomy

Not every disagreement is a factual contradiction.

Possible conflict types:

```text
TRUE_CONTRADICTION
TEMPORAL_DIFFERENCE
DEFINITION_DIFFERENCE
POPULATION_DIFFERENCE
GEOGRAPHIC_DIFFERENCE
METHODOLOGICAL_DIFFERENCE
SCOPE_DIFFERENCE
SOURCE_DEPENDENCE
UNRESOLVED
```

This classification is critical.

---

# 29. Example — Apparent Contradiction

Claim:

> "Unemployment was 5%."

Source A:

> "Unemployment was 5% in January."

Source B:

> "Unemployment was 7% in December."

These are not necessarily contradictory.

Temporal normalization resolves the apparent conflict.

---

# 30. Example — Methodological Conflict

Source A:

> "Inflation was 6%."

Source B:

> "Core inflation was 4%."

These are not necessarily contradictory.

The metrics differ.

The evidence model should identify:

```text
METRIC_MISMATCH
```

rather than declaring one source false.

---

# 31. Evidence Assessment Pipeline

Conceptually:

```text
Candidate Passage
      ↓
Language / Quality Check
      ↓
Claim Relevance
      ↓
Entity Alignment
      ↓
Temporal Alignment
      ↓
Entailment / Contradiction
      ↓
Specificity
      ↓
Source Assessment
      ↓
Provenance Analysis
      ↓
Evidence Classification
```

---

# 32. Evidence Assessment Model

The assessment layer may use multiple methods:

### Deterministic

- exact numbers;
- dates;
- entity matching;
- URL relationships;
- duplicate hashes.

### ML

- semantic similarity;
- NLI;
- reranking;
- entity linking.

### LLM

- difficult entailment;
- nuanced contradiction;
- methodological interpretation;
- ambiguous context.

The system should use the cheapest reliable method first.

---

# 33. Cascaded Assessment

A cost-aware assessment pipeline may look like:

```text
Cheap Filters
    ↓
Embedding Similarity
    ↓
Cross-Encoder
    ↓
NLI
    ↓
LLM Reasoning
```

Not every evidence candidate needs to reach the final stage.

---

# 34. Evidence Assessment Budget

Each evidence candidate may have a processing budget.

For example:

```text
Tier 0:
Deterministic checks

Tier 1:
Embedding / lightweight model

Tier 2:
Cross-encoder / NLI

Tier 3:
LLM analysis
```

Escalation should occur only when uncertainty or importance justifies it.

---

# 35. Numerical Evidence

Numerical evidence requires structured comparison.

The system should extract:

```text
Value
Unit
Metric
Population
Geography
Time
Methodology
```

Then compare compatible quantities.

Example:

```text
Claim:
GDP growth = 8.2%

Evidence:
GDP growth = 8.2%
Period = calendar 2024
Metric = real GDP
```

This is stronger than semantic similarity alone.

---

# 36. Numerical Conflict

Suppose:

```text
Source A → 8.2%
Source B → 7.9%
```

The system should investigate:

- preliminary vs revised estimate;
- fiscal vs calendar year;
- nominal vs real;
- different base years;
- different methodologies;
- different publication dates.

Only after normalization should the values be considered contradictory.

---

# 37. Attribution Evidence

For claims such as:

> "Person X said Y."

Evidence should establish:

```text
Person identity
Statement content
Time
Location/context
Originality
```

A quote copied across 50 sites should not count as 50 independent confirmations.

---

# 38. Causal Evidence

For causal claims:

> "X caused Y."

Evidence assessment should distinguish:

```text
X associated with Y
X preceded Y
X plausibly affects Y
X causally affects Y
```

A correlation study should not automatically entail a causal claim.

---

# 39. Scientific Evidence

Scientific evidence should consider:

```text
Study design
Sample size
Methodology
Peer review
Replication
Evidence hierarchy
Publication date
Consensus
Limitations
```

The system should avoid using publication prestige as a substitute for scientific assessment.

---

# 40. Evidence Aggregation

Aggregation should happen in stages.

```text
Passage Level
      ↓
Evidence Level
      ↓
Provenance Cluster
      ↓
Independent Evidence Unit
      ↓
Atomic Claim
      ↓
Parent Claim
```

This hierarchy reduces double counting.

---

# 41. Passage-Level Aggregation

Multiple passages from the same document should not automatically count as independent evidence.

For example:

```text
Document A
├── Passage 1
├── Passage 2
└── Passage 3
```

These are generally one source of evidence.

---

# 42. Document-Level Aggregation

Multiple documents from the same provenance group should not automatically provide independent corroboration.

Example:

```text
Original Report
├── News A
├── News B
└── Blog C
```

The underlying information may still be one evidence unit.

---

# 43. Evidence Cluster Aggregation

An evidence cluster may contribute stronger support when:

```text
multiple independent sources
+
high relevance
+
high entailment
+
strong source quality
+
temporal consistency
```

The cluster should not simply sum source scores.

---

# 44. Contradiction Aggregation

The same principles apply to contradiction evidence.

A single strong primary contradiction may outweigh many weak derivative supporting pages.

Therefore:

> **Evidence aggregation should be quality- and independence-aware, not count-based.**

---

# 45. Evidence Sufficiency Model

Evidence sufficiency should be multidimensional.

Conceptually:

```text
Evidence Sufficiency
├── Claim Coverage
├── Support Strength
├── Contradiction Coverage
├── Source Quality
├── Independence
├── Temporal Validity
├── Primary Evidence
└── Conflict Resolution
```

A high score in one dimension should not automatically compensate for a catastrophic failure in another.

---

# 46. Hard Constraints

Some conditions may be treated as hard constraints.

Examples:

```text
No evidence
    →
cannot claim strong support

Severe temporal mismatch
    →
cannot establish current state

Unresolved entity ambiguity
    →
confidence ceiling

Only derivative evidence
    →
corroboration ceiling

Major unresolved contradiction
    →
confidence ceiling
```

This is preferable to allowing weighted averages to hide fundamental deficiencies.

---

# 47. Confidence Ceilings

Certain uncertainty conditions should cap final confidence.

Examples:

```text
Entity unresolved
→ maximum confidence limited

Primary source unavailable
→ confidence may be limited for certain claim types

Strong unresolved conflict
→ confidence limited

Evidence coverage incomplete
→ confidence limited
```

Exact numerical ceilings should be learned or validated rather than arbitrarily chosen.

---

# 48. Evidence Graph

The evidence graph should represent:

```text
Claim
  │
  ▼
Atomic Claim
  │
  ├───────────────┐
  ▼               ▼
Evidence A      Evidence B
  │               │
  ▼               ▼
Document A      Document B
  │               │
  ▼               ▼
Source A        Source B
  │
  └──── Provenance ────┐
                       ▼
                Evidence Cluster
```

The graph supports:

- traceability;
- provenance;
- conflict detection;
- source independence;
- explanation.

---

# 49. Evidence Graph Operations

The system should eventually support:

```text
find_supporting_evidence(claim)
find_contradicting_evidence(claim)
find_primary_sources(claim)
find_provenance_cluster(evidence)
find_independent_evidence(claim)
find_conflicts(claim)
find_uncovered_components(claim)
```

These operations can later support adaptive research.

---

# 50. Evidence Lifecycle

Evidence may transition through:

```text
CANDIDATE
    ↓
ASSESSED
    ↓
VALIDATED
    ↓
AGGREGATED
    ↓
USED_IN_VERDICT
```

Evidence should not be silently discarded without recording why when auditability is required.

Possible rejection reasons:

```text
IRRELEVANT
LOW_QUALITY
DUPLICATE
DERIVATIVE
TEMPORALLY_INVALID
ENTITY_MISMATCH
INSUFFICIENT_CONTEXT
EXTRACTION_ERROR
CONTRADICTORY_BUT_UNRESOLVED
```

---

# 51. Evidence Freshness

Evidence freshness should not be one universal scalar.

The system should retain:

```text
publication_time
modification_time
observation_time
retrieval_time
validity_interval
```

Freshness policies can then be claim-dependent.

---

# 52. Evidence Decay

For some current-state claims, older evidence should lose relevance.

For historical claims, evidence does not necessarily decay.

Therefore:

```text
Temporal Relevance
=
f(claim temporal semantics, evidence temporal semantics)
```

not simply:

```text
f(age)
```

---

# 53. Evidence Contradiction vs Source Disagreement

Two sources disagreeing does not automatically mean one contradicts the claim.

Example:

Claim:

> "Inflation was 6%."

Source A:

> "Headline CPI inflation was 6%."

Source B:

> "Core inflation was 4%."

The sources disagree numerically but may not contradict the claim.

The evidence model must first determine whether they describe the same proposition.

---

# 54. Evidence and Definitions

Definitions are part of verification.

Example:

> "Unemployment is 5%."

Potential interpretations:

```text
ILO definition
National definition
Seasonally adjusted
Unadjusted
Youth unemployment
Overall unemployment
```

Definition mismatch must be surfaced.

---

# 55. Evidence and Context

Context can materially change a verdict.

Example:

> "Drug X reduces mortality by 50%."

Context may reveal:

```text
Relative risk reduction
vs
Absolute risk reduction
```

The evidence may support the literal statistic while the original framing is misleading.

This is one reason Tathvyn needs a distinction between:

```text
SUPPORTED
```

and:

```text
MISLEADING
```

---

# 56. Evidence Quality vs Evidence Quantity

The system should prefer:

```text
2 independent, high-quality sources
```

over:

```text
50 duplicated low-quality pages
```

This should be reflected structurally through provenance and independence.

---

# 57. Evidence Aggregation Baselines

Before implementing a sophisticated aggregator, establish baselines.

### Baseline A

Majority vote over source relationships.

### Baseline B

Weighted evidence score.

### Baseline C

Provenance-aware weighted aggregation.

### Baseline D

Learned evidence aggregation.

### Baseline E

Adaptive evidence reasoning.

Each stage must be evaluated independently.

---

# 58. No Arbitrary Weights

Avoid starting with:

```text
Entailment = 40%
Source = 30%
Similarity = 20%
Recency = 10%
```

Instead:

1. define measurable features;
2. construct labeled evidence data;
3. establish simple baselines;
4. evaluate aggregation models;
5. perform ablations;
6. calibrate;
7. stress-test.

---

# 59. Evidence Evaluation Dataset

A useful dataset should eventually annotate:

```text
Claim
Atomic Claim
Passage
Evidence Relationship
Source Type
Source Quality
Provenance
Temporal Validity
Independence
Claim Coverage
```

Labels should distinguish:

```text
Support
Partial Support
Contradiction
Partial Contradiction
Context
Irrelevant
Insufficient
```

---

# 60. Evidence-Level Metrics

Potential metrics:

### Relationship classification

- Precision
- Recall
- F1
- Macro-F1

### Evidence retrieval

- Recall@K
- Precision@K

### Attribution

- evidence citation precision;
- evidence citation recall.

### Provenance

- cluster precision;
- cluster recall;
- pairwise F1.

### Calibration

- ECE;
- Brier score.

---

# 61. Grounded Explanation

The explanation layer should only use evidence that exists in the evidence graph.

A grounded explanation should answer:

```text
What is the verdict?
Why?
Which evidence supports it?
Which evidence contradicts it?
What uncertainty remains?
```

The explanation generator should not invent facts absent from the graph.

---

# 62. Evidence Citation Contract

Each factual assertion in the final explanation should be traceable to one or more evidence objects.

Conceptually:

```text
Explanation Sentence
       ↓
Evidence IDs
       ↓
Passage
       ↓
Document
       ↓
Source
```

This creates a verifiable explanation chain.

---

# 63. Evidence Auditability

A reviewer should be able to inspect:

```text
Why was this passage selected?
Why was it considered supporting evidence?
What source published it?
Is it derived from another source?
Was it temporally valid?
What other evidence contradicted it?
```

This is essential for a research-grade system.

---

# 64. Evidence Failure Taxonomy

Initial failure classes:

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

This taxonomy should drive future model and policy improvements.

---

# 65. Evidence Model Invariants

### INV-E-001

Evidence must be linked to an atomic claim.

### INV-E-002

Evidence must point to a specific document and passage.

### INV-E-003

Semantic similarity alone cannot establish evidence.

### INV-E-004

Source quality must remain distinct from claim-evidence relationship.

### INV-E-005

Independent evidence must not be inferred from URL count.

### INV-E-006

Derivative sources must not automatically provide independent corroboration.

### INV-E-007

Temporal mismatch must constrain evidence validity.

### INV-E-008

Definition mismatch must be distinguished from contradiction.

### INV-E-009

A lack of evidence must not become contradiction.

### INV-E-010

Evidence conflicts must remain auditable.

### INV-E-011

Raw model scores must not be exposed as truth probabilities.

### INV-E-012

Every final evidence-backed assertion must be traceable to a source passage.

---

# 66. Conceptual Evidence Aggregation Algorithm

```text
aggregate_evidence(atomic_claim):

    candidates = get_candidate_evidence(atomic_claim)

    candidates = remove_irrelevant(candidates)

    candidates = assess_entailment_and_contradiction(candidates)

    candidates = assess_temporal_validity(candidates)

    candidates = assess_source_quality(candidates)

    candidates = cluster_by_provenance(candidates)

    evidence_units = construct_independent_units(candidates)

    support = aggregate_support(evidence_units)

    contradiction = aggregate_contradiction(evidence_units)

    conflicts = identify_unresolved_conflicts(
        support,
        contradiction
    )

    sufficiency = assess_sufficiency(
        support,
        contradiction,
        conflicts,
        coverage,
        temporal_validity
    )

    return EvidenceState(...)
```

This is a conceptual algorithm, not an implementation specification.

---

# 67. Quality-Cost Principle

Evidence assessment should use the cheapest reliable method capable of resolving the current uncertainty.

```text
Deterministic
    ↓ if insufficient
Embedding / lightweight model
    ↓ if insufficient
Cross-encoder / NLI
    ↓ if insufficient
LLM reasoning
    ↓ if insufficient
Additional research
```

This creates a natural path toward product-scale cost optimization.

---

# 68. Why This Evidence Model Matters

A naive fact checker might do:

```text
Search
  ↓
Top 5 pages
  ↓
LLM
  ↓
TRUE/FALSE
```

Tathvyn instead aims for:

```text
Claim
 ↓
Atomic Claim
 ↓
Objective-specific retrieval
 ↓
Passage evidence
 ↓
Entailment / contradiction
 ↓
Source quality
 ↓
Temporal validity
 ↓
Provenance
 ↓
Independence
 ↓
Conflict analysis
 ↓
Evidence sufficiency
 ↓
Verdict
```

This is the central architectural distinction of Tathvyn.

---

# 69. Final Evidence Principle

> **Evidence is not whatever text the system retrieves. Evidence is a claim-relative, traceable, temporally contextualized, provenance-aware information object whose relationship to the claim has been explicitly assessed.**

The evidence layer should therefore be treated as a first-class scientific and engineering subsystem.

---

# 70. Next Step

The next document should be:

**`08-research-agent.md`**

It will define the adaptive research controller:

- research state;
- planning;
- task selection;
- iterative search;
- contradiction hunting;
- primary-source escalation;
- evidence sufficiency;
- stopping policies;
- budgets;
- model/tool routing;
- failure recovery;
- and how the system evolves from a pipeline into an actual research agent.
