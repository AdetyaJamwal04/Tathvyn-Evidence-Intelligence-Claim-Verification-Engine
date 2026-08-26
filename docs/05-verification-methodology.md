# Tathvyn — Verification Methodology

## 1. Purpose

This document defines how Tathvyn transforms a natural-language claim into an evidence-grounded verification result.

The methodology is deliberately specified before selecting concrete models or infrastructure.

The central objective is:

> **Determine what the available evidence justifies about a claim, while explicitly accounting for evidence quality, contradiction, source dependence, temporal validity, uncertainty, and research cost.**

---

# 2. Fundamental Verification Principle

Tathvyn SHALL NOT treat verification as a direct classification problem:

```text
Claim → TRUE / FALSE
```

Instead:

```text
Claim
  ↓
Interpretation
  ↓
Atomic propositions
  ↓
Research objectives
  ↓
Evidence discovery
  ↓
Evidence assessment
  ↓
Evidence aggregation
  ↓
Evidence sufficiency
  ↓
Verdict
```

The verdict is a conclusion over an evidence state.

---

# 3. Verification Unit

The fundamental unit of verification is the **AtomicClaim**.

A compound claim may contain multiple atomic propositions:

```text
Claim
├── AtomicClaim A
├── AtomicClaim B
├── AtomicClaim C
└── AtomicClaim D
```

Each atomic claim is independently researched and assessed.

The parent claim is evaluated only after its material atomic claims have been assessed.

---

# 4. Verification Lifecycle

The complete methodology is:

```text
1. INGEST
     ↓
2. NORMALIZE
     ↓
3. CLASSIFY
     ↓
4. DECOMPOSE
     ↓
5. CONTEXTUALIZE
     ↓
6. PLAN RESEARCH
     ↓
7. RETRIEVE
     ↓
8. EXTRACT EVIDENCE
     ↓
9. ASSESS EVIDENCE
     ↓
10. ANALYZE SOURCES
     ↓
11. ANALYZE PROVENANCE
     ↓
12. CHECK TEMPORAL VALIDITY
     ↓
13. SEARCH FOR CONTRADICTIONS
     ↓
14. DETERMINE EVIDENCE SUFFICIENCY
     ↓
15. AGGREGATE ATOMIC VERDICTS
     ↓
16. CALIBRATE CONFIDENCE
     ↓
17. GENERATE EXPLANATION
```

The pipeline may iterate between steps rather than always executing linearly.

---

# 5. Stage 1 — Ingestion

The system receives:

```text
VerificationRequest
```

It preserves:

- original input;
- request metadata;
- request timestamp;
- language;
- client information where available.

The original input is immutable.

---

# 6. Stage 2 — Normalization

Normalization converts user phrasing into a proposition suitable for verification.

Example:

```text
Input:
"Is it true that India grew 8.2% last year?"

Normalized:
"India's GDP grew by 8.2% in 2025."
```

Normalization must not introduce unsupported information.

If "last year" cannot be resolved safely, the system must preserve the ambiguity rather than silently assuming a date.

---

# 7. Stage 3 — Claim Classification

The claim is classified along multiple dimensions.

Possible dimensions:

```text
Claim Type
Domain
Verifiability
Temporal Dependence
Complexity
Evidence Requirements
```

Example:

```text
Claim:
"India's GDP growth exceeded China's in 2025."

Type:
COMPARATIVE

Secondary:
NUMERICAL
TEMPORAL

Domain:
ECONOMICS

Temporal:
2025

Complexity:
MEDIUM
```

Classification influences research planning but does not determine the verdict.

---

# 8. Stage 4 — Atomic Decomposition

The system decomposes a compound claim into independent propositions.

Example:

> "The government banned cryptocurrency trading in India in 2024."

Possible atomic claims:

```text
A1: Cryptocurrency trading existed in the relevant context.
A2: A government authority issued a prohibition.
A3: The prohibition applied to cryptocurrency trading.
A4: The prohibition occurred in 2024.
A5: The prohibition had the claimed legal effect.
```

The decomposition should be semantically conservative.

The system should prefer:

> "I cannot safely decompose this proposition."

over inventing unsupported subclaims.

### Decomposition Edge Cases & Validation Rules:
1. **Already-Atomic Claims**: If the claim contains only a single indivisible proposition, the system produces a 1-element list with `is_atomic=True` and `decomposition_depth=0`.
2. **Maximum Depth**: Atomic claims are terminal and cannot be recursively decomposed (maximum depth = 1).
3. **Anti-Hallucination Gate**: Every generated atomic sub-claim must be logically entailed by or directly constituent of the parent claim. If a sub-claim introduces external factual entities absent from the parent, the decomposition is rejected and fallback to single-claim verification occurs.

---

# 9. Stage 5 — Contextualization

Before searching, the system extracts:

- entities;
- temporal scope;
- geography;
- units;
- quantities;
- comparison targets;
- qualifiers;
- attribution;
- domain;
- required context.

This prevents a common failure:

> retrieving evidence about the wrong entity, time period, or measurement.

---

# 10. Stage 6 — Research Planning

Each atomic claim receives research objectives.

Minimum objectives for substantive factual claims:

```text
SUPPORT
CONTRADICT
PRIMARY_SOURCE
```

Additional objectives may include:

```text
CLARIFY_ENTITY
CLARIFY_TIME
RESOLVE_CONFLICT
FILL_CLAIM_GAP
```

The planner determines:

- search queries;
- preferred source types;
- expected depth;
- priority;
- budget;
- stopping conditions.

---

# 11. Search Diversity

Search should not consist of one query.

For an atomic claim:

```text
Atomic Claim
    │
    ├── Support query
    ├── Contradiction query
    ├── Primary-source query
    ├── Entity clarification query
    └── Temporal clarification query
```

Query diversity is important because different formulations expose different evidence.

---

# 12. Retrieval Strategy

Retrieval is conceptually divided into:

### Candidate generation

Find potentially relevant documents.

### Ranking

Prioritize documents most likely to contain useful evidence.

### Passage retrieval

Identify relevant portions of documents.

### Evidence assessment

Determine whether the passage actually bears on the claim.

This distinction prevents semantic similarity from being confused with evidence.

---

# 13. Evidence Definition

A passage becomes candidate evidence when it has a meaningful relationship to an atomic claim.

Candidate evidence is assessed using:

```text
Relevance
Entailment
Contradiction
Specificity
Temporal validity
Source quality
Independence
Provenance
```

---

# 14. Relevance

Relevance asks:

> **Is this evidence about the same proposition or an important component of it?**

High semantic similarity alone is insufficient.

Example:

Claim:

> "India's GDP grew by 8.2% in 2024."

Evidence:

> "India remains one of the world's fastest-growing major economies."

This is relevant context but does not directly establish the 8.2% figure.

---

# 15. Entailment

Entailment asks:

> **If the evidence is accepted as accurate, does it support the proposition expressed by the claim?**

Example:

Claim:

> "The rate increased from 12% to 18%."

Evidence:

> "The new rate is 18%, up from the previous 12%."

Strong entailment.

But:

> "The rate is 18%."

only supports part of the proposition.

This distinction is important for compound claims.

---

# 16. Contradiction

Contradiction asks:

> **Does the evidence assert information incompatible with the atomic claim under the same interpretation and temporal scope?**

Example:

Claim:

> "The rate was 18% in 2025."

Evidence:

> "The applicable rate remained 12% throughout 2025."

This is direct contradiction.

However:

```text
Different year
Different geography
Different product category
Different definition
```

must not automatically be treated as contradiction.

---

# 17. Context Evidence

Some evidence does not support or contradict the claim but is necessary for interpretation.

Examples:

- definitions;
- methodology;
- historical context;
- policy scope;
- population restrictions;
- measurement methodology.

Context evidence may materially affect the final verdict even when it does not directly entail the claim.

---

# 18. Evidence Quality Model

Evidence quality should remain multidimensional.

Conceptually:

```text
Evidence Quality
├── Relevance
├── Entailment
├── Specificity
├── Source Quality
├── Independence
├── Temporal Validity
├── Provenance
└── Consistency
```

No single score should replace these dimensions before empirical validation.

---

# 19. Source Quality

Source quality should be assessed using signals such as:

```text
Authority
Expertise
Primary-source status
Methodological transparency
Editorial standards
Domain relevance
Historical reliability
```

A government source may be highly authoritative for its own policy, while a scientific paper may be more appropriate for a scientific finding.

Therefore:

> **Source quality is claim-dependent.**

---

# 20. Source Independence

Multiple sources are not necessarily multiple pieces of evidence.

Example:

```text
Original government report
        ↓
Reuters article
        ↓
News website
        ↓
Blog
        ↓
Social media post
```

Five URLs exist.

But there may be only one underlying information origin.

Tathvyn should therefore estimate:

```text
Independent Evidence Units
```

rather than simply counting URLs.

---

# 21. Provenance Analysis

Evidence should be grouped according to information origin.

Potential relationships:

```text
ORIGINAL
SYNDICATED
QUOTED
REFERENCED
DERIVED
COPIED
UNKNOWN
```

Provenance confidence should be represented separately from factual confidence.

> **MVP Provenance Scope**: In MVP, provenance detection is implemented deterministically using (1) canonical URL domain clustering and (2) exact quotation & numerical overlap detection. Multi-document citation graph mining and neural derivation modeling are deferred to V2.

---

# 22. Temporal Validity

Evidence must be evaluated against claim time.

Conceptually:

```text
Claim temporal scope
        +
Evidence publication time
        +
Evidence validity interval
        ↓
Temporal relevance
```

Examples:

### Current claim

> "The company's CEO is X."

A source from five years ago may be weak evidence.

### Historical claim

> "X was CEO in 2020."

The same source may be highly relevant.

Temporal relevance is therefore contextual rather than simply "newer is better."

---

# 23. Evidence Independence and Corroboration

Corroboration should be modeled as:

```text
Corroboration Strength
=
Evidence Strength
×
Independence
×
Relevance
```

This is a conceptual relationship, not the final production formula.

The final aggregation function must be experimentally validated.

---

# 24. Evidence Conflict

Conflicting evidence should trigger investigation rather than arbitrary averaging.

Example:

```text
Source A → SUPPORTS
Source B → CONTRADICTS
```

The system should investigate:

1. Are they discussing the same proposition?
2. Are they using the same definition?
3. Are they referring to the same time?
4. Are they measuring the same population?
5. Is one source derived from the other?
6. Is one source primary?
7. Has the underlying fact changed?
8. Is there a methodological disagreement?

Only after these checks should the system classify the conflict.

---

# 25. Evidence Hierarchy

Evidence should generally be prioritized according to the relationship between source and fact.

A conceptual hierarchy:

```text
Direct primary evidence
        ↓
Authoritative secondary evidence
        ↓
Independent expert evidence
        ↓
Reputable reporting
        ↓
Tertiary sources
        ↓
Unverified user-generated content
```

This is not an absolute truth hierarchy.

For some claims, a reputable secondary source may be more informative than a nominally primary source.

---

# 26. Evidence Sufficiency

The key question is:

> **Do we have enough reliable, relevant, sufficiently independent evidence to make the requested determination?**

Evidence sufficiency should consider:

```text
Claim Coverage
Support Strength
Contradiction Coverage
Source Quality
Source Independence
Temporal Validity
Primary Evidence Availability
Evidence Consistency
```

---

# 27. Research Stopping

Research should stop when additional investigation has sufficiently low expected value.

Conceptually:

```text
Expected Value of Research
=
Expected reduction in uncertainty
×
Decision importance
−
Research cost
```

This is a conceptual objective rather than the final mathematical implementation.

Stopping conditions may include:

- strong primary evidence;
- overwhelming independent corroboration;
- strong direct contradiction;
- evidence conflict that cannot be resolved;
- claim determined to be unverifiable;
- budget exhaustion;
- diminishing expected information gain.

---

# 28. Verification Budget

Each investigation receives:

```text
Search Budget
Document Budget
Inference Budget
LLM Budget
Token Budget
Latency Budget
Monetary Budget
Depth Budget
```

The controller may allocate resources dynamically.

Example:

```text
Simple claim
    ↓
Low budget
    ↓
Primary source found
    ↓
STOP

Difficult claim
    ↓
Higher budget
    ↓
Contradictory evidence
    ↓
Resolve conflict
    ↓
Seek primary source
    ↓
Reassess
```

---

# 29. Atomic Claim Verdict

An atomic claim can reach:

```text
SUPPORTED
REFUTED
CONFLICTED
INSUFFICIENT
UNVERIFIABLE
```

These states should be determined from evidence rather than from raw model outputs.

---

# 30. Parent Claim Aggregation

A parent claim is derived from its atomic claims.

Example:

```text
Parent Claim
├── A1 → SUPPORTED
├── A2 → SUPPORTED
├── A3 → REFUTED
└── A4 → SUPPORTED
```

The parent claim may therefore be:

```text
PARTIALLY_SUPPORTED
```

rather than simply TRUE or FALSE.

---

# 31. Materiality

Atomic claims should not all contribute equally.

Example:

> "Company X acquired Company Y in 2025 for $10 billion."

If:

```text
A1: Company X acquired Company Y → SUPPORTED
A2: Acquisition occurred in 2025 → SUPPORTED
A3: Price was $10 billion → REFUTED
```

The price error may materially change the meaning of the claim.

Materiality must therefore be considered when aggregating atomic results.

---

# 32. Misleading & Distorted Claims (V2 Roadmap)

A claim exhibits framing distortion when:

- its literal components contain some truth;
- important context is omitted;
- the framing creates a materially incorrect interpretation;
- or a true statement is used to imply a false conclusion.

In the **canonical MVP taxonomy** (defined in [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md)), such claims receive the verdict `PARTIALLY_SUPPORTED` accompanied by a metadata flag `framing_concerns: true`. 

A standalone `MISLEADING` top-level verdict is deferred to V2, where dedicated framing models and calibrated threshold data become available.

---

# 33. Insufficient Evidence vs Refuted

This distinction is mandatory.

### REFUTED

There is sufficiently strong evidence against the proposition.

### INSUFFICIENT_EVIDENCE

The available evidence does not justify a reliable conclusion.

Example:

```text
No credible sources found
```

does not imply:

```text
Claim is false
```

---

# 34. Unverifiable

A claim is UNVERIFIABLE when the proposition cannot reasonably be evaluated using available evidence.

Examples may include:

- inherently private experiences;
- inaccessible information;
- undefined subjective criteria;
- claims depending on unavailable future observations.

Unverifiable is different from insufficient research.

---

# 35. Confidence Model

Confidence should ultimately represent:

> **The empirically calibrated reliability of the final verification judgment under the current evidence state.**

It should not directly expose:

- cosine similarity;
- NLI probability;
- classifier softmax;
- LLM confidence;
- source score.

Those are intermediate signals.

---

# 36. Confidence Decomposition

The system should maintain internal uncertainty signals such as:

```text
Evidence uncertainty
Source uncertainty
Temporal uncertainty
Entity uncertainty
Claim ambiguity
Retrieval uncertainty
Model uncertainty
Conflict uncertainty
```

A future calibration layer can map these signals to final confidence.

---

# 37. LLM Role

LLMs may assist with:

### Appropriate uses

- claim interpretation;
- compound-claim decomposition;
- research-query generation;
- evidence summarization;
- contradiction explanation;
- ambiguity analysis;
- research planning.

### Restricted uses

LLMs should not independently determine factual truth without evidence.

The system should not accept:

```text
LLM says TRUE
```

as verification.

---

# 38. Specialized Model Role

Specialized models may be used where they provide measurable value.

Potential roles:

```text
Embedding model
→ semantic retrieval

Reranker
→ passage/document ranking

NLI model
→ entailment/contradiction assessment

NER/entity linker
→ entity understanding

Classifier
→ claim/domain classification
```

Each model should have an independently evaluated role.

---

# 39. Deterministic Logic

Deterministic rules should be preferred where the problem is deterministic.

Examples:

- date comparison;
- numeric consistency;
- unit conversion;
- duplicate URL detection;
- hash comparison;
- budget enforcement;
- schema validation.

Do not use an LLM to solve deterministic problems unnecessarily.

---

# 40. Numerical Claims

Numerical claims require special treatment.

The system should distinguish:

```text
Value
Unit
Population
Geography
Time
Methodology
Definition
```

Example:

> "Inflation was 6%."

requires understanding:

- which inflation measure;
- which country;
- which month/year;
- headline vs core;
- annual vs monthly;
- source methodology.

Numerical verification should not rely solely on semantic similarity.

---

# 41. Comparative Claims

Comparative claims require normalization.

Example:

> "India grew faster than China."

The system must establish:

```text
Metric
Time period
Population/entity
Measurement methodology
Comparison direction
```

Both sides must be evaluated under compatible definitions.

---

# 42. Causal Claims

Causal claims require stronger evidence than simple correlation.

Example:

> "X caused Y."

Evidence showing:

```text
X occurred
Y occurred
```

is not sufficient by itself.

The methodology must eventually distinguish:

```text
Correlation
Association
Temporal precedence
Mechanistic evidence
Causal inference
Experimental evidence
```

The required evidence standard should depend on the claim type.

---

# 43. Attribution Claims

Attribution claims require verifying that the person or organization actually made the statement.

The system should prefer:

- original speech;
- official transcript;
- primary recording;
- verified publication;
- authoritative archival source.

A quote appearing on many websites does not establish that the person said it.

---

# 44. Historical Claims

Historical verification should prioritize:

- primary documents;
- archival sources;
- scholarly research;
- contemporaneous records;
- reputable historical institutions.

The system must avoid treating current summaries as equivalent to primary historical evidence.

---

# 45. Scientific Claims

Scientific claims require domain-aware evidence evaluation.

Potential evidence sources:

```text
Peer-reviewed literature
Systematic reviews
Meta-analyses
Official scientific institutions
Primary studies
```

The system should distinguish:

```text
Established finding
Emerging evidence
Preliminary finding
Contested finding
Unsupported claim
```

Scientific publication alone does not guarantee correctness.

---

# 46. Source Scoring Principle

Source scores should answer:

> **How useful is this source for evaluating this particular claim?**

They should not answer:

> **Is everything published by this source true?**

This prevents source reputation from becoming an unconditional truth shortcut.

---

# 47. Evidence Aggregation

The final aggregation layer should combine evidence without double-counting.

A conceptual model:

```text
Atomic Claim
    │
    ├── Evidence A
    │     ├── strength
    │     ├── quality
    │     ├── independence
    │     └── temporal validity
    │
    ├── Evidence B
    │     └── same provenance as A
    │
    └── Evidence C
          └── independent
```

Evidence B should contribute less additional corroboration than Evidence C if both derive from A.

---

# 48. No Fixed Weighting Before Evaluation

We should NOT begin with arbitrary weights such as:

```text
source credibility = 40%
NLI = 30%
semantic similarity = 20%
recency = 10%
```

This is easy to implement but difficult to justify.

Instead:

1. define features;
2. create benchmark data;
3. establish baselines;
4. train or derive aggregation methods;
5. calibrate;
6. perform ablations;
7. measure generalization.

---

# 49. Baseline Methodology

Before sophisticated aggregation, establish simple baselines.

### Baseline A

Single-source retrieval + LLM judgment.

### Baseline B

Top-K retrieval + NLI.

### Baseline C

Weighted evidence aggregation.

### Baseline D

Adaptive multi-stage verification.

The project's advanced methodology must demonstrate improvement over simpler alternatives.

---

# 50. Evaluation Dimensions

The methodology should be evaluated on:

```text
End-to-end verdict accuracy
Evidence recall
Evidence precision
Source attribution accuracy
Contradiction detection
Calibration
Robustness
Latency
Cost
```

A method that improves accuracy by 1% while increasing cost by 20× may not be a product improvement.

---

# 51. Research Quality vs Verdict Quality

These are distinct.

A system may retrieve excellent evidence but aggregate it incorrectly.

Conversely, a system may produce the correct verdict for the wrong reasons.

Therefore evaluation must ask:

```text
Did we retrieve the right evidence?
        ↓
Did we correctly interpret it?
        ↓
Did we correctly aggregate it?
        ↓
Did we reach the correct verdict?
```

---

# 52. Evidence Grounding

A verdict should be considered well-grounded only when:

1. relevant evidence exists;
2. evidence materially supports the reasoning;
3. citations point to the actual evidence;
4. the explanation does not introduce unsupported claims.

Grounding should be evaluated separately from factual accuracy.

---

# 53. Failure Taxonomy

Every incorrect verification should eventually be classified into a failure type.

Initial taxonomy:

```text
CLAIM_UNDERSTANDING_FAILURE
DECOMPOSITION_FAILURE
ENTITY_RESOLUTION_FAILURE
TEMPORAL_FAILURE
QUERY_GENERATION_FAILURE
RETRIEVAL_FAILURE
DOCUMENT_EXTRACTION_FAILURE
EVIDENCE_SELECTION_FAILURE
ENTAILMENT_FAILURE
CONTRADICTION_FAILURE
SOURCE_ASSESSMENT_FAILURE
PROVENANCE_FAILURE
AGGREGATION_FAILURE
CALIBRATION_FAILURE
EXPLANATION_FAILURE
SYSTEM_FAILURE
```

This taxonomy is critical for iterative improvement.

---

# 54. Golden Verification Trace

For research and debugging, each benchmark case should ideally contain:

```text
Input Claim
    ↓
Expected Atomic Claims
    ↓
Expected Research Objectives
    ↓
Relevant Evidence
    ↓
Supporting Evidence
    ↓
Contradicting Evidence
    ↓
Expected Verdict
    ↓
Expected Uncertainty
```

This becomes the foundation for component-level evaluation.

---

# 55. Methodology Invariants

### INV-M-001

Evidence must be traceable to a source passage.

### INV-M-002

Semantic similarity alone cannot establish support.

### INV-M-003

Absence of evidence cannot automatically establish contradiction.

### INV-M-004

Multiple derivative sources cannot automatically be treated as independent corroboration.

### INV-M-005

Temporal mismatch must be considered before comparing evidence with a claim.

### INV-M-006

LLM-generated reasoning cannot substitute for external evidence.

### INV-M-007

Conflicting high-quality evidence must remain visible to the aggregation layer.

### INV-M-008

Raw model scores must not automatically be exposed as truth probabilities.

### INV-M-009

Deterministic computations should not be delegated to probabilistic models without justification.

### INV-M-010

Every verdict must be traceable to the evidence state that produced it.

---

# 56. High-Level Verification Algorithm

Conceptually:

```text
verify(claim):

    request = ingest(claim)

    normalized = normalize(request)

    classification = classify(normalized)

    if not verifiable(classification):
        return UNVERIFIABLE

    atomic_claims = decompose(normalized)

    context = contextualize(atomic_claims)

    plan = create_research_plan(context)

    while research_budget_available(plan):

        tasks = select_next_tasks(plan)

        evidence = execute_research(tasks)

        evidence = assess_evidence(evidence)

        evidence = analyze_sources(evidence)

        evidence = analyze_provenance(evidence)

        evidence = evaluate_temporal_validity(evidence)

        update_evidence_state(evidence)

        if evidence_sufficient():
            break

        if expected_value_of_research_is_low():
            break

    atomic_verdicts = determine_atomic_verdicts()

    overall_verdict = aggregate_atomic_verdicts(
        atomic_verdicts,
        materiality
    )

    confidence = calibrate(
        evidence_state,
        uncertainty
    )

    explanation = generate_grounded_explanation(
        overall_verdict,
        evidence_state
    )

    return VerificationResult(...)
```

This is a conceptual algorithm, not an implementation commitment.

---

# 57. Quality-Cost Objective

The product objective can be represented conceptually as:

\[
\max \; Q
\]

subject to:

\[
C \le C_{max}
\]

\[
L \le L_{max}
\]

where:

- \(Q\) = verification quality;
- \(C\) = verification cost;
- \(L\) = latency.

A more realistic product optimization may eventually use a utility function:

\[
U = lpha Q - eta C - \gamma L
\]

with coefficients determined by product requirements and empirical business constraints.

The exact formulation should be validated experimentally.

---

# 58. Verification Depth

A future implementation should support multiple research depths.

```text
DEPTH 0 — Heuristic
    ↓
DEPTH 1 — Basic Retrieval
    ↓
DEPTH 2 — Evidence Assessment
    ↓
DEPTH 3 — Contradiction + Primary Search
    ↓
DEPTH 4 — Adaptive Deep Research
```

The system should not automatically run the deepest pipeline for every claim.

---

# 59. Research Escalation

Escalation should occur when signals indicate that deeper research has value.

Potential triggers:

```text
Low evidence coverage
High source disagreement
Low source quality
High claim complexity
Temporal ambiguity
Entity ambiguity
High-stakes domain
High contradiction probability
Low confidence
```

Escalation policy should eventually be learned or optimized from evaluation data.

---

# 60. High-Stakes Domains

The methodology should eventually support domain-specific verification policies.

Examples:

```text
Medical
Legal
Financial
Scientific
Political
Historical
General
```

High-stakes domains may require:

- stricter source requirements;
- stronger evidence thresholds;
- more primary evidence;
- additional disclaimers;
- human review pathways.

The initial implementation should avoid claiming that a generic verifier is sufficient for professional decision-making.

---

# 61. Final Methodological Principle

> **Verification is an evidence acquisition, assessment, and reasoning process under uncertainty and resource constraints.**

The goal is not maximum confidence.

The goal is:

> **the strongest defensible conclusion supported by the available evidence within the permitted research budget.**

---

# 62. Next Step

The next document should be:

**`06-retrieval-strategy.md`**

It will define the retrieval subsystem in depth:

- search architecture;
- query generation;
- query diversity;
- lexical retrieval;
- dense retrieval;
- reranking;
- source discovery;
- primary-source prioritization;
- duplicate detection;
- provenance discovery;
- caching;
- retrieval evaluation;
- search-provider abstraction;
- and cost-aware retrieval.

Only after this should we lock the concrete retrieval stack.
