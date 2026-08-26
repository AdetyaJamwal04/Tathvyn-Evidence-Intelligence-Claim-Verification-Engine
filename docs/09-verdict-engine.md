# Tathvyn — Verdict Engine

## 1. Purpose

This document defines the final decision layer of Tathvyn.

The Verdict Engine transforms the accumulated research state into a structured verification judgment.

Its responsibility is to answer:

> **Given the available evidence, its quality, independence, temporal validity, conflicts, and uncertainty, what conclusion is justified about the claim?**

The Verdict Engine is deliberately separated from:

- search;
- retrieval;
- evidence extraction;
- source discovery;
- research planning;
- explanation generation.

This separation makes the final decision logic independently testable.

---

# 2. Verdict Principle

The Verdict Engine must not operate as:

```text
LLM → TRUE/FALSE
```

It should operate as:

```text
Research State
      ↓
Evidence State
      ↓
Atomic Claim Assessments
      ↓
Evidence Sufficiency
      ↓
Materiality Analysis
      ↓
Verdict Decision
      ↓
Confidence Calibration
      ↓
Verification Result
```

---

# 3. Verdict Vocabulary

The canonical internal verdict taxonomy is defined in [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md):

```text
SUPPORTED
REFUTED
PARTIALLY_SUPPORTED
INSUFFICIENT_EVIDENCE
UNVERIFIABLE
```

The public API maps these deterministically into product-facing labels:

```text
Internal                  → Public
─────────────────────────────────────
SUPPORTED                 → LIKELY TRUE
REFUTED                   → LIKELY FALSE
PARTIALLY_SUPPORTED       → PARTIALLY TRUE
INSUFFICIENT_EVIDENCE     → UNVERIFIED
UNVERIFIABLE              → UNVERIFIABLE
```

> **Framing & Distortion**: Claims where literal facts are accurate but the overall presentation materially distorts reality are classified as `PARTIALLY_SUPPORTED` with a `framing_concerns: true` metadata flag. Standalone `MISLEADING` verdict classification is deferred to V2.

The internal taxonomy should remain richer than the UI taxonomy.

---

# 4. Verdict vs Confidence

These are separate concepts.

### Verdict

The qualitative conclusion.

### Confidence

How reliable the system estimates that conclusion to be under the current evidence state.

Example:

```text
Verdict:
SUPPORTED

Confidence:
0.86
```

The value `0.86` must not be interpreted as a calibrated probability until calibration has been empirically demonstrated.

---

# 5. Atomic Claim Verdict

Each atomic claim should first receive an independent assessment.

Possible states:

```text
SUPPORTED
REFUTED
CONFLICTED
INSUFFICIENT
UNVERIFIABLE
```

The parent claim should not be judged until material atomic claims have been assessed.

---

# 6. Atomic Verdict Inputs

The atomic verdict engine should consider:

```text
Supporting evidence
Contradicting evidence
Evidence strength
Source quality
Source independence
Provenance
Temporal validity
Claim coverage
Conflict state
Primary-source availability
Uncertainty
```

It should not directly depend on:

```text
search-result rank
embedding similarity
LLM confidence
raw NLI probability
source count
```

Those are intermediate signals.

---

# 7. Evidence Normalization

Before aggregation, evidence should be normalized.

For each evidence item:

```text
claim_relationship
relevance
entailment
contradiction
specificity
temporal_validity
source_quality
independence
provenance_confidence
coverage
```

All dimensions should have defined semantics.

---

# 8. Evidence State

The Verdict Engine consumes an evidence state conceptually represented as:

```text
EvidenceState
├── support_units
├── contradiction_units
├── context_units
├── provenance_clusters
├── unresolved_conflicts
├── coverage
├── temporal_state
├── source_quality_state
├── independence_state
└── uncertainty
```

This object should be deterministic and inspectable.

---

# 9. Independent Evidence Units

The engine should aggregate **independent evidence units**, not raw documents.

Example:

```text
Government Report
    ↓
News A
    ↓
Blog B
    ↓
Social Post C
```

may represent one underlying evidence unit.

Counting all four as independent would artificially inflate confidence.

---

# 10. Support Aggregation

Conceptually:

```text
Support Strength
=
Σ independent support contributions
```

But the actual contribution should account for:

```text
Evidence strength
×
Source utility
×
Independence
×
Temporal validity
×
Claim coverage
```

The exact aggregation function should be empirically evaluated.

---

# 11. Contradiction Aggregation

Contradicting evidence should be aggregated using the same conceptual framework.

A single strong primary contradiction may be more informative than many weak supporting pages.

Therefore:

```text
Evidence Count
```

must never be the primary decision mechanism.

---

# 12. Support-Contradiction Balance

A useful conceptual representation is:

```text
Support State
      │
      ├── strong support
      ├── moderate support
      └── weak support

Contradiction State
      │
      ├── strong contradiction
      ├── moderate contradiction
      └── weak contradiction
```

The engine then evaluates:

```text
support strength
vs
contradiction strength
```

under evidence-quality and independence constraints.

---

# 13. Hard Constraints Before Scoring

The engine should evaluate hard conditions before calculating any aggregate score.

Examples:

```text
No material evidence
    →
cannot be SUPPORTED

No meaningful contradiction
    →
cannot be REFUTED

Unresolved entity ambiguity
    →
confidence constrained

Severe temporal mismatch
    →
evidence cannot establish claim

Major unresolved contradiction
    →
strong verdict may be prohibited
```

This prevents weighted averages from hiding fundamental failures.

---

# 14. Evidence Sufficiency Gate

Before a strong verdict is allowed:

```text
Is there enough evidence?
```

The sufficiency gate should consider:

```text
Coverage
Support
Contradiction search
Source quality
Independence
Temporal validity
Conflict state
```

If the answer is no:

```text
INSUFFICIENT_EVIDENCE
```

may be more appropriate than forcing a directional verdict.

---

# 15. Coverage

A claim can only be considered strongly supported if the material proposition is sufficiently covered.

Example:

> "Company X acquired Company Y for $10B in 2025."

Evidence:

```text
Acquisition → supported
Price → unsupported
Year → supported
```

The whole claim should not automatically become SUPPORTED.

---

# 16. Materiality

Not all atomic claims contribute equally.

Each atomic claim should have:

```text
materiality
importance
```

Possible categories:

```text
CRITICAL
MATERIAL
CONTEXTUAL
```

A contextual error may not overturn the main claim.

A critical numerical error may.

---

# 17. Parent Claim Aggregation

Conceptually:

```text
Parent Claim
├── A1 → SUPPORTED
├── A2 → SUPPORTED
├── A3 → SUPPORTED
└── A4 → REFUTED
```

If A4 is critical:

```text
Parent:
REFUTED / MISLEADING
```

If A4 is minor:

```text
Parent:
PARTIALLY_SUPPORTED
```

Therefore parent verdict aggregation must be materiality-aware.

---

# 18. Parent Verdict Matrix

Conceptual matrix:

| Atomic Claim State | Materiality | Parent Impact |
|---|---|---|
| SUPPORTED | Critical | Supports parent |
| SUPPORTED | Material | Supports parent |
| SUPPORTED | Contextual | Minor support |
| REFUTED | Critical | Strong negative impact |
| REFUTED | Material | Negative impact |
| REFUTED | Contextual | May not overturn parent |
| INSUFFICIENT | Critical | Confidence ceiling |
| INSUFFICIENT | Material | Partial / uncertain |
| INSUFFICIENT | Contextual | Minor impact |
| UNVERIFIABLE | Critical | Parent may become UNVERIFIABLE |
| CONFLICTED | Critical | Confidence ceiling / possible MISLEADING |

This is a policy framework, not a fixed scoring table.

---

# 19. Supported

Use SUPPORTED when:

```text
Material atomic claims are sufficiently covered
+
supporting evidence is strong
+
evidence is sufficiently independent
+
temporal conditions are satisfied
+
no material unresolved contradiction exists
```

The standard should be stronger than:

```text
"we found something that sounds similar."
```

---

# 20. Refuted

Use REFUTED when:

```text
Material proposition is directly contradicted
+
contradicting evidence is sufficiently strong
+
source and temporal conditions are satisfied
+
the contradiction is not explained by scope/definition/time
```

---

# 21. Partially Supported

Use PARTIALLY_SUPPORTED when:

```text
Some material components are supported
+
others remain unsupported or contradicted
```

This is particularly useful for compound claims.

---

# 22. Misleading & Framing Distortion (V2 Roadmap)

Framing distortion applies to cases where:

```text
The claim contains substantially true or supportable components
+
the framing, omission, qualification, or implication materially distorts interpretation.
```

Examples:

```text
Correct statistic
+
wrong comparison

Correct quote
+
missing context

Correct event
+
incorrect implication
```

In the **MVP taxonomy**, these cases are assigned `PARTIALLY_SUPPORTED` with a boolean metadata flag `framing_concerns: true`. A dedicated standalone `MISLEADING` verdict category will be reintroduced in V2 once calibration datasets for nuance and framing are validated.

---

# 23. Insufficient Evidence

Use INSUFFICIENT_EVIDENCE when:

```text
Relevant evidence was sought
+
available evidence is inadequate for a reliable directional judgment.
```

This differs from:

```text
No search was performed.
```

The research trace should show that the system attempted appropriate investigation.

---

# 24. Unverifiable

Use UNVERIFIABLE when the proposition cannot reasonably be evaluated using available evidence.

Examples:

```text
Private subjective experience
Unobservable proposition
Undefined criterion
Fundamentally inaccessible information
```

A system limitation should not automatically be labeled UNVERIFIABLE.

---

# 25. Conflict Handling

When:

```text
Support ≈ Contradiction
```

the engine should not automatically return:

```text
50/50
```

It should investigate:

```text
Temporal difference
Definition difference
Methodological difference
Population difference
Source dependence
Source quality
Primary evidence
```

If unresolved:

```text
CONFLICTED
```

at atomic level and potentially:

```text
INSUFFICIENT_EVIDENCE
```

or:

```text
MISLEADING
```

at parent level.

---

# 26. Strong Contradiction

Strong contradiction should be able to override numerous weak supporting documents.

Example:

```text
1 official primary source → contradiction
25 derivative blogs → support
```

The result should not be:

```text
25 vs 1
```

Instead:

```text
Independent evidence quality
+
provenance
+
claim relevance
```

should dominate.

---

# 27. Evidence Quality Floors

Some claim classes may require minimum evidence quality.

Examples:

```text
Legal claim
→ authoritative legal source preferred

Scientific causal claim
→ appropriate scientific evidence preferred

Financial numerical claim
→ primary filing/statistical source preferred
```

If the minimum evidence quality requirement is not met:

```text
confidence is constrained
```

rather than compensated by quantity.

---

# 28. Primary Source Requirement

Certain claim types may have a strong preference for primary evidence.

Examples:

```text
Official policy
→ government notification

Financial disclosure
→ regulatory filing

Quoted statement
→ original transcript/video

Scientific finding
→ original paper
```

Secondary reporting can still support the claim, but lack of primary evidence may reduce confidence.

---

# 29. Confidence Calibration

Raw scores must be calibrated against labeled verification outcomes.

Potential methods:

```text
Platt scaling
Isotonic regression
Beta calibration
Temperature scaling
```

The best method should be selected empirically.

---

# 30. Calibration Dataset

The calibration dataset must be separated from training data.

Recommended split:

```text
Training
Validation
Calibration
Test
```

Calibration data should reflect real deployment distributions where possible.

---

# 31. Confidence Metrics

Evaluate confidence using:

### Expected Calibration Error

Measures whether predicted confidence matches observed accuracy.

### Brier Score

Measures probabilistic prediction quality.

### Reliability Diagram

Visualizes:

```text
Predicted confidence
vs
Observed correctness
```

A system with 0.9 confidence should be correct approximately 90% of the time within an appropriately defined evaluation population.

---

# 32. Confidence Is Conditional

Confidence should be interpreted as:

> **Estimated reliability of the verdict under the evidence and policy conditions used to produce it.**

It is not:

```text
absolute probability that the claim is metaphysically true.
```

---

# 33. Confidence Factors

Potential internal factors:

```text
Evidence quality
Evidence independence
Evidence coverage
Conflict
Temporal uncertainty
Entity ambiguity
Source quality
Primary-source availability
Research depth
Model uncertainty
```

These factors should feed a calibrated confidence layer.

---

# 34. Confidence Ceilings

Confidence may be constrained by hard uncertainty.

Examples:

```text
Critical atomic claim unresolved
→ confidence ceiling

Strong unresolved source conflict
→ confidence ceiling

Entity ambiguity unresolved
→ confidence ceiling

Only weak derivative sources
→ confidence ceiling
```

The exact ceiling values should be empirically determined.

---

# 35. Confidence vs Verdict Threshold

These are separate.

Example:

```text
Evidence state
→ SUPPORTED

Calibrated confidence
→ 0.71
```

The system may still report:

```text
SUPPORTED — moderate confidence
```

rather than converting everything below an arbitrary threshold into:

```text
INSUFFICIENT
```

The product policy should determine presentation.

---

# 36. Decision Thresholds

Thresholds should be evaluated using benchmark data.

Potential initial conceptual boundaries:

```text
Strong support
→ high-quality support with no material contradiction

Strong refutation
→ high-quality contradiction with no material unresolved issue

Mixed
→ meaningful support and contradiction

Insufficient
→ inadequate evidence
```

Exact numerical thresholds should not be finalized before evaluation.

---

# 37. Score-Based Baseline

A simple baseline may use:

```text
Support Score
−
Contradiction Score
```

with evidence-quality and independence modifiers.

Example:

\[
S =
\sum_i w_i^+ e_i^+
-
\sum_j w_j^- e_j^-
\]

where:

- \(e_i^+\) = support evidence strength;
- \(e_j^-\) = contradiction evidence strength;
- \(w\) = validated evidence modifiers.

This is a baseline, not the final architecture.

---

# 38. Bayesian Interpretation

A probabilistic formulation could eventually model:

\[
P(H \mid E_1, E_2, ..., E_n)
\]

where:

- \(H\) = claim hypothesis;
- \(E_i\) = evidence unit.

However, naive Bayesian multiplication assumes independence.

Because web evidence is often correlated, provenance and source dependence must be modeled.

Therefore a simplistic Bayesian implementation would be unsafe.

---

# 39. Correlated Evidence

Consider:

```text
Original report
 ↓
Article A
 ↓
Article B
 ↓
Article C
```

Evidence A, B, and C are correlated.

Treating them as independent likelihood updates can dramatically overstate confidence.

The aggregation layer must account for dependency.

---

# 40. Evidence Graph Aggregation

A future probabilistic engine could operate over:

```text
Evidence Graph
       ↓
Dependency structure
       ↓
Independent evidence clusters
       ↓
Claim posterior
```

This is a possible research direction rather than an initial implementation requirement.

---

# 41. Deterministic Checks Before Probabilistic Aggregation

Where possible:

```text
Check dates
Check units
Check numbers
Check entities
Check definitions
Check provenance
```

before invoking probabilistic aggregation.

This reduces avoidable uncertainty.

---

# 42. Numerical Verdict Engine

For numerical claims, the verdict engine should support structured comparison.

Example:

```text
Claim:
8.2%

Evidence:
8.2%
```

Strong match only if:

```text
Metric = same
Unit = same
Period = same
Population = same
Geography = same
Methodology = compatible
```

Otherwise the evidence may only partially support the claim.

---

# 43. Comparative Verdict Engine

For:

> "A is larger than B."

the system should normalize:

```text
Metric
Unit
Time
Population
Measurement methodology
```

Then compare:

\[
A > B
\]

using deterministic computation when the underlying values are available.

---

# 44. Causal Verdict Engine

Causal claims should have stricter evidence requirements.

Potential levels:

```text
ASSOCIATION
TEMPORAL ASSOCIATION
PLAUSIBLE MECHANISM
STRONG CAUSAL EVIDENCE
ESTABLISHED CAUSAL RELATION
```

The engine must not promote:

```text
correlation
```

to:

```text
causation
```

without adequate evidence.

---

# 45. Attribution Verdict Engine

For quote claims:

```text
Person X said Y.
```

the engine should assess:

```text
identity
statement
source authenticity
context
timestamp
originality
```

A secondary article quoting the statement may be useful but should be distinguished from the original source.

---

# 46. Historical Verdict Engine

Historical claims may require:

```text
Primary documents
Contemporaneous records
Scholarly sources
Archival evidence
```

The engine should account for:

```text
source survival
historical bias
translation
interpretation
scholarly disagreement
```

A lack of surviving primary evidence should not automatically imply falsity.

---

# 47. Scientific Verdict Engine

Scientific claims require domain-aware policy.

Potential evidence states:

```text
Strongly established
Supported
Preliminary
Contested
Unsupported
Refuted
```

The product may map these into the canonical verdict taxonomy.

Scientific consensus should be represented as evidence rather than blindly treated as truth.

---

# 48. High-Stakes Verdict Policy

For high-stakes claims, the engine may require:

```text
Higher evidence sufficiency
Primary-source preference
Additional contradiction search
Stricter confidence calibration
Human review
```

The final product should clearly distinguish:

```text
general information
```

from:

```text
professional decision support.
```

---

# 49. Verdict Explanation Contract

The Verdict Engine should produce a structured decision object.

Conceptually:

```text
VerdictDecision
├── verdict
├── confidence
├── evidence_sufficiency
├── support_summary
├── contradiction_summary
├── unresolved_issues
├── materiality_analysis
├── uncertainty_profile
├── supporting_evidence_ids
├── contradicting_evidence_ids
├── stop_reason
├── policy_version
└── model_versions
```

The prose explanation should be generated later.

---

# 50. Explainability

The system must be able to answer:

```text
Why did you classify the claim this way?
```

with:

```text
Atomic claim assessments
+
evidence
+
source quality
+
conflicts
+
materiality
+
uncertainty
```

The explanation must not expose arbitrary internal model reasoning as if it were factual evidence.

---

# 51. Decision Trace

A verdict should have a compact machine-readable trace.

Example:

```text
Claim
 ↓
A1 supported
 ↓
A2 supported
 ↓
A3 contradicted
 ↓
A3 critical
 ↓
Parent claim materially affected
 ↓
MISLEADING
```

This is more useful for debugging than a free-form reasoning transcript.

---

# 52. Verdict Failure Modes

Initial taxonomy:

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
MISLEADING_MISCLASSIFICATION
INSUFFICIENT_EVIDENCE_ERROR
UNVERIFIABLE_ERROR
```

---

# 53. Verdict Evaluation

The Verdict Engine should be evaluated independently.

Metrics:

```text
Accuracy
Macro-F1
Per-class precision/recall
Confusion matrix
Calibration
Selective accuracy
Abstention quality
```

For a verification system, abstention quality is especially important.

---

# 54. Selective Prediction

The system should be allowed to say:

```text
I do not have enough evidence.
```

This is a feature, not necessarily a failure.

A useful evaluation is:

```text
Coverage
vs
Accuracy
```

As the system becomes more selective, accuracy should improve without catastrophic coverage loss.

---

# 55. Risk-Coverage Tradeoff

Conceptually:

\[
Risk(c)
\]

should decrease as the system becomes more selective at coverage \(c\).

This provides a way to evaluate whether the system knows when it should abstain.

---

# 56. False Positive vs False Negative

The relative cost of errors depends on product context.

For example:

```text
False "TRUE"
```

may be more damaging than:

```text
UNVERIFIED
```

for misinformation detection.

Therefore the system should optimize an application-specific loss function.

---

# 57. Cost-Sensitive Verdicts

Potential loss formulation:

\[
L =
\lambda_{FP} FP
+
\lambda_{FN} FN
+
\lambda_A Abstention
\]

where the coefficients reflect product priorities.

These should be selected using product requirements and evaluation data.

---

# 58. Verdict Versioning

Every verdict should record:

```text
verdict_engine_version
aggregation_policy_version
calibration_version
research_policy_version
model_versions
```

This enables reproducibility.

---

# 59. Reproducibility

Given the same:

```text
claim
evidence snapshot
model versions
policy versions
```

the Verdict Engine should produce the same result, subject to explicitly documented nondeterminism.

This makes it possible to regression-test the system.

---

# 60. Online vs Offline Verdicting

The system should support:

### Online

Real-time verification request.

### Offline

Recompute historical verdicts after:

- model upgrades;
- policy changes;
- source updates;
- benchmark improvements.

This allows controlled evolution.

---

# 61. Verdict Cache

A cached verdict may be reused only when:

```text
claim equivalence
+
evidence freshness
+
policy compatibility
+
model compatibility
```

are satisfied.

Otherwise the system should re-verify.

---

# 62. Verdict API Contract

Conceptually:

```python
decide(
    claim,
    atomic_claims,
    evidence_state,
    policy
) -> VerdictDecision
```

The function should be deterministic given its inputs and configured versions.

---

# 63. Core Verdict Invariants

### INV-V-001

A strong directional verdict requires sufficient evidence.

### INV-V-002

Evidence count alone cannot determine a verdict.

### INV-V-003

Dependent sources cannot be treated as independent corroboration.

### INV-V-004

Material atomic claims must influence parent verdicts.

### INV-V-005

Critical unresolved conflicts must constrain confidence.

### INV-V-006

Insufficient evidence must remain distinct from refutation.

### INV-V-007

Unverifiable must remain distinct from system failure.

### INV-V-008

Raw model scores must not be presented as calibrated truth probabilities.

### INV-V-009

Every verdict must be traceable to evidence.

### INV-V-010

Every verdict must be reproducible from versioned inputs and policies.

---

# 64. Conceptual Decision Algorithm

```text
decide(claim, evidence_state):

    validate_evidence_state()

    atomic_results = []

    for atomic_claim in claim.atomic_claims:

        evidence = get_evidence(atomic_claim)

        normalized = normalize_evidence(evidence)

        if critical_data_invalid(normalized):
            result = INSUFFICIENT
        else:
            result = evaluate_atomic_claim(
                normalized
            )

        atomic_results.append(result)

    materiality = evaluate_materiality(
        claim,
        atomic_results
    )

    parent_verdict = aggregate_atomic_results(
        atomic_results,
        materiality
    )

    sufficiency = assess_final_sufficiency(
        evidence_state,
        atomic_results
    )

    if not sufficiency.allows(parent_verdict):
        parent_verdict = apply_abstention_policy(
            parent_verdict
        )

    confidence = calibrate_confidence(
        parent_verdict,
        evidence_state
    )

    return VerdictDecision(...)
```

---

# 65. Initial Implementation Strategy

The first implementation should be deliberately simple.

### Version 0

```text
Rule-based evidence aggregation
+
explicit hard constraints
+
simple validated scoring baseline
```

### Version 1

```text
Learned evidence aggregation
+
calibration
```

### Version 2

```text
Provenance-aware probabilistic aggregation
+
dependency modeling
```

### Version 3

```text
Adaptive learned decision policy
```

Each upgrade should be justified by benchmark results.

---

# 66. What We Should Not Build First

Avoid beginning with:

```text
Complex Bayesian network
Multi-agent judge
LLM-only verdict
Large learned ensemble
Custom neural architecture
```

before establishing:

```text
Reliable evidence representation
Reliable benchmark
Strong retrieval
Strong evidence assessment
Simple baseline
```

Otherwise it becomes difficult to identify where quality actually comes from.

---

# 67. Product-Scale Objective

The Verdict Engine should optimize:

```text
Accuracy
+
Calibration
+
Abstention quality
+
Latency
+
Cost
+
Explainability
```

A slightly less accurate system that is:

```text
10× cheaper
+
5× faster
+
better calibrated
```

may be the superior production system.

The tradeoff must be measured rather than assumed.

---

# 68. Final Verdict Principle

> **The correct verdict is not the most confident conclusion the system can produce. It is the strongest conclusion justified by the evidence state after accounting for uncertainty, source dependence, temporal validity, materiality, and research limitations.**

A mature Tathvyn system should therefore be comfortable saying:

```text
SUPPORTED
```

when evidence is strong,

```text
REFUTED
```

when contradiction is strong,

```text
PARTIALLY_SUPPORTED
```

when only part of the claim survives,

```text
MISLEADING
```

when framing materially distorts the truth,

```text
INSUFFICIENT_EVIDENCE
```

when evidence is inadequate,

and:

```text
UNVERIFIABLE
```

when the proposition cannot reasonably be evaluated.

---

# 69. Next Step

The next document should be:

**`10-model-architecture.md`**

It will translate the methodology into a concrete ML architecture:

- claim understanding;
- claim decomposition;
- embeddings;
- retrieval models;
- rerankers;
- NLI;
- entity resolution;
- temporal reasoning;
- source scoring;
- model routing;
- local vs API models;
- model serving;
- batching;
- quantization;
- CPU/GPU strategy;
- and evaluation-driven model selection.
