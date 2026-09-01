# Tathvyn — Verdict Engine and Calibration

## 1. Purpose

The Verdict Engine is the decision layer of Tathvyn.

Its responsibility is to transform:

```text
Evidence Graph
+
Claim Structure
+
Evidence Quality
+
Provenance
+
Temporal Validity
+
Conflict State
+
Verification Policy
```

into:

```text
Verdict
+
Confidence
+
Evidence Sufficiency
+
Reasoning Trace
+
Citations
```

The engine must answer:

> **Given the evidence we actually have, what conclusion is justified—and how certain should we be?**

---

# 2. Core Principle

The Verdict Engine must never answer:

> "What is probably true according to the model?"

It should answer:

> **"What conclusion is justified by the available evidence under the current verification policy?"**

This distinction is fundamental.

---

# 3. Verdict Pipeline

```text
Evidence Graph
      ↓
Evidence Validation
      ↓
Claim Coverage Analysis
      ↓
Evidence Independence
      ↓
Support / Contradiction Aggregation
      ↓
Conflict Resolution
      ↓
Temporal Resolution
      ↓
Claim-Level Scoring
      ↓
Compound Claim Aggregation
      ↓
Evidence Sufficiency
      ↓
Uncertainty Estimation
      ↓
Calibration
      ↓
Abstention Check
      ↓
Final Verdict
      ↓
Explanation + Citations
```

---

# 4. Verdict Classes

Canonical internal and public taxonomies are defined in [00-canonical-enums.md](./00-canonical-enums.md).

Public user-facing verdicts:

```text
LIKELY TRUE
LIKELY FALSE
PARTIALLY TRUE
UNVERIFIED
UNVERIFIABLE
```

> **Framing & Distortion**: Claims with accurate components but distortive framing receive `PARTIALLY TRUE` with `framing_concerns: true` metadata in MVP. Standalone `MISLEADING` verdict is deferred to V2.

---

# 5. Internal Decision States

The internal decision engine evaluates:

```text
SUPPORTED
REFUTED
PARTIALLY_SUPPORTED
INSUFFICIENT_EVIDENCE
UNVERIFIABLE
```

Intermediate granular states:

```text
STRONGLY_SUPPORTED        → SUPPORTED
SUPPORTED                 → SUPPORTED
WEAKLY_SUPPORTED          → SUPPORTED (lower confidence)

STRONGLY_CONTRADICTED     → REFUTED
CONTRADICTED              → REFUTED
WEAKLY_CONTRADICTED       → REFUTED (lower confidence)

MIXED                     → PARTIALLY_SUPPORTED
INSUFFICIENT              → INSUFFICIENT_EVIDENCE
AMBIGUOUS                 → INSUFFICIENT_EVIDENCE
OUT_OF_SCOPE              → UNVERIFIABLE
```

Public labels are deterministically mapped from the canonical internal verdicts.

---

# 6. Why "LIKELY" Matters

Web evidence rarely establishes mathematical certainty.

Therefore:

```text
LIKELY TRUE
```

is preferable to:

```text
ABSOLUTELY TRUE
```

unless the product specifically defines stronger guarantees for certain evidence classes.

---

# 7. Evidence State

The Verdict Engine should construct an intermediate state:

```text
EvidenceState
├── support
├── contradiction
├── qualification
├── context
├── conflicts
├── provenance_clusters
├── coverage
├── temporal_validity
├── source_quality
└── uncertainty
```

---

# 8. Evidence Independence

Do not count:

```text
10 articles
```

as:

```text
10 independent confirmations
```

if they all derive from:

```text
1 original report.
```

Aggregation must happen at the provenance-cluster level.

---

# 9. Provenance-Adjusted Evidence

Conceptually:

```text
Evidence
 ↓
Provenance Cluster
 ↓
Independent Evidence Unit
 ↓
Aggregation
```

---

# 10. Evidence Unit

An evidence unit may represent:

```text
primary source
```

or:

```text
independent evidence cluster
```

rather than an individual URL.

---

# 11. Support Score

A support evidence unit can have:

```text
stance
relevance
source quality
temporal validity
entity alignment
provenance confidence
independence
```

---

# 12. Contradiction Score

Similarly:

```text
contradiction strength
relevance
source quality
temporal validity
entity alignment
independence
```

must be represented.

---

# 13. Qualification

Qualification should not simply be treated as weak contradiction.

Example:

> "The treatment works, but only in patients with condition X."

This changes:

```text
scope
```

rather than necessarily reversing:

```text
truth value.
```

---

# 14. Evidence Contribution

A conceptual contribution function:

\[
C_i =
R_i
\times
S_i
\times
T_i
\times
E_i
\times
P_i
\times
I_i
\]

where:

```text
R = relevance
S = stance strength
T = temporal validity
E = entity alignment
P = provenance/source quality
I = independence
```

This is an initial conceptual model, not a final mathematical truth.

---

# 15. Why Multiplicative Scoring

If:

```text
relevance = high
```

but:

```text
entity alignment = poor
```

the evidence should not receive high influence.

A multiplicative structure naturally penalizes weak dimensions.

However, learned or probabilistic aggregation should eventually be evaluated against this baseline.

---

# 16. Avoiding Double Penalties

Care must be taken not to multiply correlated signals repeatedly.

For example:

```text
source quality
authority
primary status
editorial reputation
```

may be correlated.

Naively multiplying all of them can produce artificially extreme scores.

---

# 17. Score Calibration

Raw model outputs are not necessarily probabilities.

For example:

```text
NLI score = 0.93
```

does not automatically mean:

```text
93% probability the claim is true.
```

The Verdict Engine must separate:

```text
model score
```

from:

```text
calibrated probability.
```

---

# 18. Support Aggregation

A naive method:

\[
Support = \sum_i C_i
\]

is dangerous because evidence units may not be independent.

Use provenance-aware aggregation.

---

# 19. Independent Evidence Aggregation

Conceptually:

\[
Support =
\sum_{g \in Groups}
f(Group_g)
\]

where:

```text
Group_g
```

represents one provenance cluster.

---

# 20. Diminishing Returns

Additional evidence from the same provenance cluster should have diminishing influence.

Example:

```text
Source A → strong
Source B → derivative of A
Source C → derivative of A
```

should not produce:

```text
3 × confidence
```

---

# 21. Evidence Saturation

Confidence should approach a ceiling.

Conceptually:

\[
Confidence =
1-e^{-kE}
\]

where:

```text
E = effective independent evidence
```

This is illustrative.

The actual function should be calibrated empirically.

---

# 22. Contradiction Aggregation

Likewise:

\[
Contradiction =
\sum_{g}
f(ContradictoryEvidence_g)
\]

with provenance-aware independence.

---

# 23. Net Evidence

A conceptual baseline:

\[
NetEvidence =
Support - Contradiction
\]

But this should not directly become:

```text
confidence
```

because:

```text
coverage
quality
uncertainty
```

also matter.

---

# 24. Evidence Coverage

Coverage measures whether the retrieved evidence addresses all material components.

Example:

```text
Claim:
X acquired Y for $10B in 2025.

Evidence:
Acquisition confirmed.

Missing:
price
date
```

The evidence is insufficient for the complete claim.

---

# 25. Claim Coverage

For atomic claims:

\[
Coverage =
\frac{
\sum Materiality_i \cdot Verified_i
}{
\sum Materiality_i
}
\]

This is a conceptual metric.

---

# 26. Materiality

Not every atomic claim has equal importance.

Example:

```text
X acquired Y
```

may be more material than:

```text
announcement occurred on Tuesday.
```

Materiality can be estimated from:

```text
semantic importance
user emphasis
claim structure
domain policy
```

---

# 27. Compound Claim Verdict

A compound claim should not be reduced to:

```text
average atomic confidence
```

Instead:

```text
atomic verdicts
+
dependencies
+
materiality
```

should determine the final result.

---

# 28. Example Compound Claim

```text
X acquired Y
AND
the transaction was worth $10B
AND
it was the largest acquisition in the sector.
```

Suppose:

```text
A1 = supported
A2 = supported
A3 = unverified
```

Final:

```text
MIXED / MISLEADING
```

rather than:

```text
TRUE
```

---

# 29. Logical Operators

The system should recognize:

```text
AND
OR
IF
UNLESS
ONLY IF
BECAUSE
THEREFORE
```

These define dependencies between atomic claims.

---

# 30. AND Claims

For:

```text
A AND B
```

both must be supported for the compound proposition to be fully supported.

---

# 31. OR Claims

For:

```text
A OR B
```

support for either may be sufficient depending on semantics.

---

# 32. Conditional Claims

For:

```text
A → B
```

the system must not simply verify:

```text
B
```

without considering:

```text
A
```

and the causal/conditional relationship.

---

# 33. Causal Claims

Causal claims require a dedicated policy.

Evidence should distinguish:

```text
correlation
association
mechanistic evidence
experimental evidence
quasi-experimental evidence
causal inference
```

---

# 34. Causal Evidence Strength

Potential hierarchy:

```text
Randomized controlled evidence
↓
Strong quasi-experimental evidence
↓
Longitudinal observational evidence
↓
Cross-sectional association
↓
Anecdotal evidence
```

This hierarchy is domain-dependent.

---

# 35. Causal Overclaim Detection

Example:

Evidence:

> "X is associated with Y."

Claim:

> "X causes Y."

The Verdict Engine should detect:

```text
evidence does not establish claimed causal strength
```

and likely produce:

```text
MIXED / MISLEADING
```

or:

```text
UNVERIFIED
```

depending on context.

---

# 36. Temporal Resolution

Conflicting evidence may be explained by time.

Example:

```text
2024:
A was CEO.

2026:
B is CEO.
```

The system should not treat these as contradiction.

---

# 37. Temporal Priority

For current-state claims:

```text
recent valid evidence
```

should generally receive greater weight.

For historical claims:

```text
contemporaneous evidence
```

may be more authoritative.

---

# 38. Source Quality Policy

Source weighting must be claim-dependent.

Example:

```text
Official government source
```

may be highly authoritative for:

```text
official policy
```

but should not automatically dominate:

```text
independent scientific assessment of that policy.
```

---

# 39. Source Quality Vector

Use:

```text
authority
expertise
primary_status
methodology
transparency
specificity
```

rather than one opaque score.

---

# 40. Evidence Quality Vector

The Verdict Engine can consume:

```text
relevance
stance
entity
temporal
source
provenance
independence
```

---

# 41. Conflict Resolution

When evidence conflicts, ask:

```text
Are they actually discussing the same proposition?
```

Check:

```text
entity
time
definition
scope
metric
population
methodology
```

before declaring contradiction.

---

# 42. Conflict Hierarchy

Potential resolution order:

```text
Entity mismatch
↓
Temporal mismatch
↓
Definition mismatch
↓
Scope mismatch
↓
Measurement mismatch
↓
True contradiction
```

---

# 43. True Contradiction

A contradiction should require sufficiently aligned:

```text
entity
time
scope
definition
```

and incompatible propositions.

---

# 44. Conflict Severity

```text
MINOR
MODERATE
MATERIAL
CRITICAL
```

Material conflicts should reduce confidence substantially.

---

# 45. Uncertainty

Uncertainty can arise from:

```text
insufficient evidence
conflicting evidence
ambiguous claim
ambiguous entity
temporal uncertainty
model uncertainty
source uncertainty
```

These should be distinguishable.

---

# 46. Uncertainty Vector

Represent:

```text
evidence_uncertainty
semantic_uncertainty
temporal_uncertainty
source_uncertainty
model_uncertainty
```

---

# 47. Evidence Sufficiency

Define a separate score:

```text
evidence_sufficiency ∈ [0,1]
```

It measures:

> Is there enough appropriate evidence to make a decision?

This is different from:

```text
probability that the claim is true.
```

---

# 48. Example

A system may have:

```text
truth probability = 0.90
```

but:

```text
evidence sufficiency = 0.45
```

because only one weak source was found.

The system should probably abstain.

---

# 49. Abstention

The Verdict Engine must have a first-class abstention path.

```text
Insufficient evidence
       ↓
UNVERIFIED
```

Abstention is a feature, not a failure.

---

# 50. Abstention Conditions

Potential conditions:

```text
low evidence sufficiency
high conflict
high ambiguity
insufficient primary evidence
low source quality
low calibration confidence
coverage below threshold
```

---

# 51. Decision Region

Conceptually:

```text
                High Support
                     │
                     ▼
               LIKELY TRUE
                     ▲
                     │
      ───────────────┼───────────────
                     │
          UNVERIFIED │
                     │
      ───────────────┼───────────────
                     │
                     ▼
               LIKELY FALSE
                High Contradiction
```

Mixed evidence may occupy the center.

---

# 52. Decision Thresholds

Do not hard-code arbitrary thresholds permanently.

Instead:

```text
train / tune
 ↓
validation
 ↓
calibration
 ↓
test
```

Thresholds should be selected against desired risk.

---

# 53. Calibration Dataset

Use a validation set separate from:

```text
training
```

and:

```text
final test.
```

---

# 54. Calibration Methods

Potential methods:

```text
Platt scaling
Isotonic regression
Temperature scaling
Beta calibration
```

Selection should be empirical.

---

# 55. Multiclass Calibration

For:

```text
TRUE
FALSE
MIXED
UNVERIFIED
```

calibration should be evaluated across the full class distribution.

---

# 56. Calibration Metric

Use:

```text
ECE
Brier score
log loss
reliability diagrams
```

---

# 57. Confidence Output

The public API should expose:

```json
{
  "verdict": "LIKELY TRUE",
  "confidence": 0.91,
  "evidence_sufficiency": 0.88
}
```

but these numbers must have defined semantics.

---

# 58. Confidence Semantics

Recommended interpretation:

```text
confidence
=
calibrated probability associated with the chosen decision,
under the benchmark distribution and current policy.
```

It should not mean:

```text
absolute probability of truth in the universe.
```

---

# 59. Confidence Intervals

For aggregate evaluation, report:

```text
confidence intervals
```

around system metrics.

Per-request confidence should remain distinct from benchmark uncertainty.

---

# 60. Model Tiebreaker

An LLM can be used as a tiebreaker only when:

```text
structured evidence is ambiguous
```

It should not override strong evidence arbitrarily.

---

# 61. Tiebreaker Boundary

The LLM should receive:

```text
claim
atomic claims
evidence graph
source metadata
conflicts
policy
```

not:

```text
raw unrestricted web access
```

unless explicitly designed as another research action.

---

# 62. Tiebreaker Output

Require structured output:

```text
decision
reason
evidence_ids
uncertainties
confidence
```

The model must cite the evidence objects it used.

---

# 63. Tiebreaker Validation

The system should verify:

```text
Does the LLM cite existing evidence?
Does the reasoning match evidence stance?
Does it invent evidence?
Does it violate temporal scope?
```

---

# 64. No LLM Override Rule

A low-quality LLM response should not override:

```text
strong primary evidence
```

without a policy-defined reason.

---

# 65. Verdict Score

A baseline internal score can combine:

```text
support
-
contradiction
+
quality
+
coverage
-
conflict
```

but the score should not be exposed as if it were a probability.

---

# 66. Learned Verdict Model

Eventually, a supervised model may learn:

```text
Evidence features
+
Claim features
+
Source features
+
Conflict features
```

to predict:

```text
gold verdict
```

Potential models:

```text
logistic regression
gradient boosting
small neural network
```

A simpler interpretable model should be the baseline.

---

# 67. Why Start Simple

A simple model provides:

```text
interpretability
debuggability
calibration baseline
low inference cost
```

Before replacing it with a more complex learned aggregator.

---

# 68. Feature Set

Potential features:

```text
support_strength
contradiction_strength
independent_support_count
independent_contradiction_count
coverage
source_quality
primary_source_presence
temporal_validity
conflict_severity
claim_complexity
claim_risk
evidence_sufficiency
```

---

# 69. Monotonicity

Some relationships should ideally be monotonic.

For example:

```text
all else equal,
stronger independent support
```

should not reduce:

```text
support confidence.
```

This can be encouraged using suitable model constraints.

---

# 70. Counterfactual Testing

Test the verdict engine by modifying one feature.

Example:

```text
add strong independent evidence
```

Expected:

```text
confidence should not decrease
```

unless the new evidence introduces conflict.

---

# 71. Verdict Stability

Small irrelevant changes to evidence ordering should not materially change the verdict.

Test:

```text
shuffle evidence order
```

and compare outputs.

---

# 72. Evidence Order Invariance

A robust aggregator should be approximately:

```text
permutation invariant
```

with respect to evidence ordering.

---

# 73. Source Count Sensitivity

Test:

```text
1 primary source
vs
10 derivative articles
```

The verdict should not become dramatically more confident merely because the number of URLs increased.

---

# 74. Contradiction Sensitivity

Introduce:

```text
one strong contradictory primary source
```

and measure whether confidence appropriately changes.

---

# 75. Temporal Sensitivity

Replace:

```text
old evidence
```

with:

```text
current authoritative evidence
```

and verify that current-state verdicts update appropriately.

---

# 76. Coverage Sensitivity

Remove evidence for one material atomic claim.

Expected:

```text
confidence decreases
```

and possibly:

```text
MIXED / UNVERIFIED
```

depending on materiality.

---

# 77. Verdict Explanation

The explanation should be generated only after:

```text
verdict finalized
```

and should be grounded in:

```text
selected evidence
```

---

# 78. Explanation Structure

Recommended:

```text
Verdict
↓
Short conclusion
↓
Key supporting evidence
↓
Key contradictory evidence
↓
Important qualification
↓
Why confidence is limited
↓
Citations
```

---

# 79. Explanation Must Reflect Uncertainty

Bad:

> "This is definitely true."

when:

```text
confidence = 0.72
```

Better:

> "The available evidence supports the claim, although the evidence is limited by..."

---

# 80. Evidence Selection for Explanation

Do not expose every internal evidence item.

Select:

```text
most decisive support
most decisive contradiction
most important qualification
```

while preserving citations.

---

# 81. Verdict Audit Trace

Store:

```text
verdict_id
evidence_snapshot_id
policy_version
model_versions
aggregation_version
calibration_version
decision_features
thresholds
```

---

# 82. Reproducibility

Given the same:

```text
evidence snapshot
+
policy version
+
model versions
```

the Verdict Engine should produce the same result, subject to explicitly documented nondeterminism.

---

# 83. Verdict Versioning

Example:

```text
verdict_engine_v1
verdict_engine_v2
```

Historical results remain attached to their original engine version.

---

# 84. Verdict Lifecycle

```text
EVIDENCE_READY
      ↓
AGGREGATING
      ↓
CONFLICT_ANALYSIS
      ↓
CALIBRATING
      ↓
DECIDING
      ↓
EXPLANATION
      ↓
FINAL
```

---

# 85. Verdict Failure States

```text
INSUFFICIENT_EVIDENCE
CONFLICT_UNRESOLVED
CLAIM_AMBIGUOUS
POLICY_UNSUPPORTED
MODEL_FAILURE
SYSTEM_FAILURE
```

These should not all map to:

```text
UNVERIFIED
```

internally.

---

# 86. Public vs Internal Status

Public:

```text
UNVERIFIED
```

Internal:

```text
UNVERIFIED_DUE_TO_CONFLICT
UNVERIFIED_DUE_TO_LOW_COVERAGE
UNVERIFIED_DUE_TO_AMBIGUITY
```

This improves diagnostics.

---

# 87. Verdict API

Conceptually:

```python
evaluate(
    claim_analysis,
    evidence_state,
    policy
) -> VerdictResult
```

Output:

```text
VerdictResult
├── verdict
├── confidence
├── evidence_sufficiency
├── key_evidence
├── conflicts
├── explanation
└── trace
```

---

# 88. Verdict Pseudocode

```text
evaluate(claim, evidence, policy):

    validate_evidence(evidence)

    coverage = calculate_coverage(
        claim,
        evidence
    )

    clusters = build_independent_units(
        evidence
    )

    support = aggregate_support(
        clusters
    )

    contradiction = aggregate_contradiction(
        clusters
    )

    conflicts = resolve_conflicts(
        evidence
    )

    uncertainty = estimate_uncertainty(
        coverage,
        conflicts,
        evidence
    )

    raw_decision = decide(
        support,
        contradiction,
        coverage,
        uncertainty
    )

    calibrated = calibrate(
        raw_decision
    )

    final = apply_abstention_policy(
        calibrated
    )

    return final
```

---

# 89. Verdict Evaluation

Evaluate:

```text
accuracy
macro F1
calibration
Brier score
ECE
abstention quality
evidence grounding
```

---

# 90. Calibration Evaluation

Compare:

```text
raw score
```

vs:

```text
calibrated score
```

on a held-out set.

---

# 91. Threshold Optimization

Choose thresholds based on:

```text
risk tolerance
coverage target
calibration
domain
```

not arbitrary values.

---

# 92. Domain-Specific Calibration

Calibration may differ across:

```text
medicine
finance
history
technology
politics
```

If enough data exists, maintain domain-specific calibration models.

Otherwise use a global calibrated model with domain features.

---

# 93. Risk-Aware Verdict Policy

For high-risk domains:

```text
higher evidence sufficiency
+
stronger source requirements
+
lower tolerance for unsupported decisive verdicts
```

may be appropriate.

---

# 94. Abstention Optimization

The objective is not:

```text
maximize decisive predictions.
```

It is:

```text
maximize useful correct predictions
while controlling harmful errors.
```

---

# 95. Selective Risk

Measure:

\[
Risk(c) =
P(error \mid confidence \ge c)
\]

for confidence threshold:

```text
c
```

---

# 96. Coverage-Risk Tradeoff

Report:

```text
coverage
vs
error
```

across thresholds.

This allows product teams to choose an operating point.

---

# 97. Calibration Drift

Calibration can degrade when:

```text
web changes
source distribution changes
model changes
claim distribution changes
```

Monitor calibration continuously.

---

# 98. Verdict Monitoring

Track:

```text
confidence distribution
verdict distribution
abstention rate
contradiction rate
evidence sufficiency
calibration drift
```

---

# 99. Production Drift

Detect changes in:

```text
claim types
domains
source types
search provider
evidence quality
```

These may change system behavior even without a code deployment.

---

# 100. Verdict Engine Architecture

```text
                     Evidence Graph
                           │
                           ▼
                  Evidence Validator
                           │
                           ▼
                  Coverage Analyzer
                           │
                           ▼
                Provenance Aggregator
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                 Support     Contradiction
                    │             │
                    └──────┬──────┘
                           ▼
                    Conflict Engine
                           │
                           ▼
                   Claim Aggregator
                           │
                           ▼
                  Uncertainty Model
                           │
                           ▼
                    Calibration
                           │
                           ▼
                  Abstention Policy
                           │
                           ▼
                     Verdict
                           │
                           ▼
               Explanation Generator
```

---

# 101. Verdict Invariants

### INV-VE-001

A verdict must be based only on evidence available in the evidence snapshot.

### INV-VE-002

Dependent sources must not be treated as independent confirmations.

### INV-VE-003

Evidence sufficiency and truth confidence must remain separate.

### INV-VE-004

NLI scores must not be treated as calibrated truth probabilities without calibration.

### INV-VE-005

Compound claims must respect atomic claim dependencies.

### INV-VE-006

Material contradictions must reduce confidence.

### INV-VE-007

Unsupported certainty must result in abstention where required.

### INV-VE-008

Historical verdicts must remain reproducible.

### INV-VE-009

Explanations must be grounded in selected evidence.

### INV-VE-010

Verdict behavior should be robust to irrelevant evidence ordering.

---

# 102. Research Questions

The Verdict Engine should empirically determine:

1. Which aggregation function best predicts gold verdicts?
2. How much does provenance-aware aggregation improve calibration?
3. How should support and contradiction interact?
4. What is the optimal abstention policy?
5. How should compound claims be aggregated?
6. Which uncertainty features are most predictive?
7. How much does source quality improve calibration?
8. Can a simple learned aggregator outperform hand-designed scoring?
9. How stable is the verdict under evidence perturbations?
10. How should calibration adapt to different domains?
11. What evidence sufficiency threshold minimizes harmful false positives?
12. How much does the LLM tiebreaker actually improve accuracy relative to its cost?

---

# 103. Final Principle

> **The Verdict Engine should be conservative about what it concludes and precise about why it concludes it.**

The complete decision path should remain:

```text
Claim
 ↓
Atomic Claims
 ↓
Retrieved Information
 ↓
Validated Evidence
 ↓
Independent Evidence Units
 ↓
Support / Contradiction
 ↓
Coverage / Conflict
 ↓
Uncertainty
 ↓
Calibration
 ↓
Abstention
 ↓
Verdict
```

The goal is not to make Tathvyn sound certain.

The goal is to make its certainty **earned by evidence**.

---

# 104. Next Step

The next document should be:

**`18-research-orchestrator.md`**

It will define the control plane that coordinates the entire system:

- research state machine;
- task scheduling;
- adaptive query selection;
- evidence sufficiency checks;
- stopping conditions;
- budget allocation;
- parallelism;
- retries;
- failure recovery;
- model routing;
- cache reuse;
- and the transition from a fixed pipeline into a genuine **agentic verification system**.
