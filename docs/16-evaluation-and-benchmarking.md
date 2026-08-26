# Tathvyn — Evaluation and Benchmarking

## 1. Purpose

Evaluation is not a final testing phase of Tathvyn.

It is a core architectural subsystem.

The system makes a strong claim:

> **Tathvyn can determine the factual status of claims using retrieved evidence.**

That claim is meaningful only if it can be measured rigorously.

The evaluation architecture must therefore answer:

```text
Is the system accurate?
Is it calibrated?
Does retrieval find the right evidence?
Does evidence engineering interpret it correctly?
Does the system abstain when evidence is insufficient?
Does each architectural change actually improve verification?
How expensive is the improvement?
```

---

# 2. Evaluation Philosophy

The project should optimize for:

```text
Correctness
+
Calibration
+
Evidence quality
+
Robustness
+
Abstention quality
+
Latency
+
Cost
```

not merely:

```text
accuracy
```

A system that produces confident answers to unsupported claims is worse than a system that correctly says:

```text
UNVERIFIED
```

when evidence is insufficient.

---

# 3. Evaluation Stack

Evaluation should exist at multiple levels:

```text
Level 1 — Unit
Level 2 — Component
Level 3 — Retrieval
Level 4 — Evidence
Level 5 — Verdict
Level 6 — End-to-End
Level 7 — System / Product
```

---

# 4. Level 1 — Unit Evaluation

Test deterministic components independently.

Examples:

```text
URL normalization
date normalization
number parsing
unit conversion
claim hashing
source classification
query normalization
deduplication
```

These tests should be fast and deterministic.

---

# 5. Level 2 — Component Evaluation

Evaluate ML and intelligent subsystems independently.

Examples:

```text
Claim detection
Claim decomposition
Entity resolution
Temporal extraction
Query generation
Reranking
NLI
Provenance detection
Conflict detection
Source scoring
```

---

# 6. Level 3 — Retrieval Evaluation

Evaluate:

```text
Can the system retrieve the evidence?
```

before asking:

```text
Did the system classify the claim correctly?
```

This isolates retrieval failures.

---

# 7. Level 4 — Evidence Evaluation

Evaluate:

```text
Did the system correctly interpret retrieved information?
```

Metrics include:

```text
stance accuracy
entity alignment
temporal alignment
numerical extraction
provenance
conflict detection
```

---

# 8. Level 5 — Verdict Evaluation

Evaluate:

```text
Given the evidence,
did the system reach the correct verdict?
```

Include:

```text
accuracy
macro F1
precision
recall
calibration
abstention
```

---

# 9. Level 6 — End-to-End Evaluation

Measure:

```text
User Claim
 ↓
Claim Intelligence
 ↓
Retrieval
 ↓
Evidence
 ↓
Verdict
```

This is the most realistic benchmark.

---

# 10. Level 7 — Product Evaluation

Measure:

```text
latency
cost
throughput
availability
cache efficiency
user satisfaction
citation usefulness
```

A model can be accurate but unusable if:

```text
latency = 2 minutes
cost = $0.50/request
```

for a simple claim.

---

# 11. Benchmark Taxonomy

Benchmark datasets should be stratified by:

```text
domain
claim type
difficulty
temporal sensitivity
source availability
ambiguity
evidence conflict
claim complexity
```

---

# 12. Domain Distribution

Example domains:

```text
General
Science
Medicine
Technology
Finance
Law
Politics
History
Business
Climate
Sports
Culture
```

The exact distribution should reflect expected product usage.

---

# 13. Claim Type Distribution

Include:

```text
Simple factual
Numerical
Temporal
Comparative
Causal
Attribution
Historical
Compound
Negative
Conditional
```

---

# 14. Difficulty Distribution

Create:

```text
Easy
Medium
Hard
Expert
```

Difficulty should be determined from actual verification complexity rather than subjective labeling alone.

---

# 15. Temporal Distribution

Include:

```text
Historical
Stable facts
Recent events
Current facts
Rapidly changing facts
Future predictions
```

---

# 16. Evidence Availability

Examples:

```text
Strong evidence exists
Moderate evidence exists
Conflicting evidence exists
Weak evidence exists
No reliable evidence exists
```

The benchmark must include all categories.

---

# 17. Verdict Labels

Initial labels:

```text
SUPPORTED
REFUTED
MIXED / MISLEADING
UNVERIFIED
```

Internally, more granular labels may be useful.

---

# 18. Why "True / False" Is Insufficient

Consider:

> "A study proves that X causes Y."

Possible reality:

```text
Study exists
+
Study finds association
+
Causal interpretation is overstated
```

This is not simply:

```text
TRUE
```

or:

```text
FALSE
```

Hence:

```text
MISLEADING
```

is essential.

---

# 19. Gold Label Protocol

Every benchmark item should have:

```text
claim
gold verdict
gold atomic claims
gold evidence
gold contradictory evidence
source references
temporal requirements
rationale
```

---

# 20. Gold Evidence

Gold evidence should identify:

```text
source
document
passage
relationship
```

where possible.

---

# 21. Multiple Valid Evidence Sets

Do not assume there is exactly one correct source.

A claim may be supported by:

```text
Government report A
```

or:

```text
Primary dataset B
```

Both can be valid.

Evaluation should therefore support multiple acceptable evidence sets.

---

# 22. Evidence Annotation

Annotators should label:

```text
SUPPORTS
CONTRADICTS
QUALIFIES
CONTEXTUALIZES
NEUTRAL
```

and:

```text
entity alignment
temporal validity
source quality
```

where feasible.

---

# 23. Annotation Guidelines

Annotators need explicit rules for:

```text
negation
causality
numbers
dates
comparisons
qualifiers
source independence
```

Ambiguous cases should be escalated.

---

# 24. Annotation Agreement

Measure:

```text
Cohen's kappa
Fleiss' kappa
Krippendorff's alpha
```

depending on the annotation design.

Low agreement indicates:

```text
ambiguous task
weak guidelines
or intrinsically uncertain claims
```

---

# 25. Adjudication

Disagreements should be reviewed by:

```text
senior annotator
domain expert
```

where appropriate.

The final gold label should retain an audit trail.

---

# 26. Gold Label Confidence

A benchmark item can store:

```text
label_confidence
annotator_count
agreement_score
adjudication_status
```

This helps distinguish:

```text
hard problem
```

from:

```text
poor annotation.
```

---

# 27. Retrieval Metrics

Core metrics:

```text
Recall@K
Precision@K
MRR
MAP
nDCG
```

---

# 28. Evidence Recall

Define:

\[
EvidenceRecall@K =
\frac{\text{gold evidence retrieved in top K}}
{\text{gold evidence available}}
\]

This is a core Tathvyn metric.

---

# 29. Primary Source Recall

Measure:

\[
PrimaryRecall@K =
\frac{\text{claims with gold primary source retrieved}}
{\text{claims requiring primary source}}
\]

---

# 30. Contradiction Recall

Measure:

\[
ContradictionRecall@K =
\frac{\text{claims where material contradiction was retrieved}}
{\text{claims with known contradiction}}
\]

This directly tests confirmation bias.

---

# 31. Source Diversity

Measure:

```text
number of independent evidence clusters
```

rather than simply:

```text
number of URLs
```

---

# 32. Provenance-Adjusted Evidence Recall

If five articles all derive from one report:

```text
5 URLs ≠ 5 independent evidence units
```

The benchmark should evaluate whether the underlying evidence clusters were discovered.

---

# 33. Reranking Evaluation

Compare:

```text
Initial retrieval
vs
reranked retrieval
```

Metrics:

```text
nDCG@K
MRR
Evidence Recall@K
Contradiction Recall@K
```

---

# 34. Evidence Classification Metrics

For evidence relationship:

```text
SUPPORT
CONTRADICT
QUALIFY
CONTEXT
NEUTRAL
```

evaluate:

```text
macro F1
per-class F1
confusion matrix
```

---

# 35. NLI Evaluation

Measure:

```text
accuracy
macro F1
per-class F1
confidence calibration
```

But NLI performance should not be treated as equivalent to verification performance.

---

# 36. Entity Alignment Evaluation

Metrics:

```text
precision
recall
F1
```

for:

```text
entity extraction
entity linking
entity alignment
```

---

# 37. Temporal Evaluation

Evaluate:

```text
span detection
normalization
relation classification
validity classification
```

---

# 38. Numerical Evaluation

Measure:

```text
value accuracy
unit accuracy
metric accuracy
period accuracy
operator accuracy
```

A numerical extraction is correct only when all material dimensions are correct.

---

# 39. Provenance Evaluation

Measure:

```text
provenance precision
provenance recall
cluster purity
source independence accuracy
```

---

# 40. Conflict Detection

Measure:

```text
conflict precision
conflict recall
conflict severity accuracy
```

False conflicts can unnecessarily reduce confidence.

Missed conflicts can create dangerous overconfidence.

---

# 41. Verdict Metrics

Core:

```text
Accuracy
Macro F1
Precision
Recall
```

Macro F1 is particularly important when classes are imbalanced.

---

# 42. Per-Class Verdict Metrics

Report separately:

```text
SUPPORTED
REFUTED
MIXED
UNVERIFIED
```

A system can have high aggregate accuracy while performing poorly on:

```text
UNVERIFIED
```

which is particularly important.

---

# 43. Confusion Matrix

Always inspect:

```text
actual
vs
predicted
```

especially:

```text
SUPPORTED → REFUTED
REFUTED → SUPPORTED
UNVERIFIED → SUPPORTED
UNVERIFIED → REFUTED
```

---

# 44. Cost-Sensitive Evaluation

Errors do not have equal consequences.

A false:

```text
SUPPORTED
```

for an unsupported medical claim may be more serious than:

```text
UNVERIFIED
```

for a harmless historical claim.

Therefore evaluate:

```text
weighted error cost
```

for high-risk domains.

---

# 45. Confidence Calibration

A system producing:

```text
confidence = 0.90
```

should be correct approximately:

```text
90%
```

of the time among similarly scored predictions.

---

# 46. Calibration Metrics

Use:

```text
Expected Calibration Error (ECE)
Brier Score
Reliability diagrams
Adaptive calibration error
```

---

# 47. Reliability Diagram

Evaluate whether:

```text
predicted confidence
```

matches:

```text
empirical accuracy
```

across confidence bins.

---

# 48. Overconfidence

A major failure mode:

```text
wrong verdict
+
high confidence
```

Track this separately.

---

# 49. Underconfidence

Another failure mode:

```text
correct verdict
+
unnecessarily low confidence
```

This can cause excessive abstention.

---

# 50. Abstention Evaluation

The system must be able to say:

```text
UNVERIFIED
```

or:

```text
INSUFFICIENT_EVIDENCE
```

when appropriate.

---

# 51. Selective Prediction

Define:

```text
coverage
```

as the percentage of claims on which the system gives a decisive verdict.

Then evaluate:

```text
risk at coverage
```

---

# 52. Risk-Coverage Curve

A strong system should achieve:

```text
high coverage
```

without a large increase in:

```text
error rate.
```

---

# 53. Abstention Threshold

The system can abstain when:

```text
confidence < threshold
```

or:

```text
evidence sufficiency < threshold
```

The threshold should be calibrated on validation data.

---

# 54. Evidence Sufficiency

Separate:

```text
confidence
```

from:

```text
evidence sufficiency
```

A model can be confident despite insufficient evidence.

---

# 55. Verdict Confidence Decomposition

Potential components:

```text
evidence strength
evidence independence
source quality
coverage
conflict level
temporal validity
model uncertainty
```

---

# 56. Confidence Should Not Equal Source Count

Bad:

```text
5 sources → high confidence
```

if:

```text
all 5 copied the same article.
```

Confidence should be provenance-aware.

---

# 57. End-to-End Accuracy

The primary benchmark:

```text
raw user claim
→
final verdict
```

This captures all upstream errors.

---

# 58. Evidence-Grounded Accuracy

Evaluate:

```text
verdict
+
supporting evidence
```

A correct label with irrelevant evidence should not receive full credit.

---

# 59. Citation Correctness

Evaluate:

```text
Does citation actually support the explanation?
```

Metrics can include:

```text
citation entailment
citation completeness
citation precision
```

---

# 60. Citation Completeness

Measure:

> What proportion of material factual statements in the explanation have supporting citations?

---

# 61. Explanation Faithfulness

The explanation must reflect the evidence used for the verdict.

A fluent explanation that invents reasoning is a failure.

---

# 62. Explanation Evaluation

Evaluate:

```text
factual consistency
citation grounding
coverage
conciseness
contradiction
```

Human evaluation may be necessary for some dimensions.

---

# 63. Adversarial Evaluation

Build adversarial datasets for:

```text
negation
numbers
dates
entity swaps
source spoofing
headline manipulation
quote truncation
copied articles
misleading statistics
```

---

# 64. Negation Test

Original:

```text
X acquired Y.
```

Mutation:

```text
X did not acquire Y.
```

The system should change its reasoning appropriately.

---

# 65. Numerical Mutation

Original:

```text
GDP grew 8.2%.
```

Mutation:

```text
GDP grew 18.2%.
```

Retrieval may find similar documents, but evidence engineering should detect the mismatch.

---

# 66. Temporal Mutation

Original:

```text
X was CEO in 2024.
```

Mutation:

```text
X is CEO in 2026.
```

The system must distinguish historical and current truth.

---

# 67. Entity Mutation

Original:

```text
Company A acquired Company B.
```

Mutation:

```text
Company A acquired Company C.
```

This tests entity alignment.

---

# 68. Unit Mutation

Original:

```text
10 million.
```

Mutation:

```text
10 billion.
```

The retrieval system may return identical topical evidence, so structured evidence evaluation must catch it.

---

# 69. Source Poisoning

Create claims supported by:

```text
low-quality fabricated pages
```

while high-quality sources contradict them.

The system should not blindly trust retrieval ranking.

---

# 70. Confirmation Bias Benchmark

For each claim, provide:

```text
supporting evidence
+
contradicting evidence
```

in controlled ranking positions.

Test whether the system can discover both.

---

# 71. Retrieval Position Bias

Place relevant evidence at:

```text
rank 1
rank 5
rank 20
rank 50
rank 100
```

Measure degradation.

---

# 72. Source Bias Test

Provide:

```text
many low-quality sources
+
few high-quality sources
```

The system should not equate volume with credibility.

---

# 73. Temporal Drift Benchmark

Maintain claims whose truth status changes.

Example:

```text
2024:
A is CEO.

2025:
B becomes CEO.

2026:
C becomes CEO.
```

Run the same semantic claim at different timestamps.

---

# 74. Benchmark Snapshots

Because the web changes, benchmarks need:

```text
snapshot date
source snapshots
gold evidence references
```

where legally and technically feasible.

---

# 75. Web Benchmark Challenge

Live-web evaluation is inherently unstable.

A benchmark should distinguish:

```text
static benchmark
```

from:

```text
live-web benchmark
```

---

# 76. Static Benchmark

Use:

```text
frozen documents
frozen metadata
frozen retrieval corpus
```

Advantages:

```text
reproducibility
controlled experiments
regression testing
```

---

# 77. Live Benchmark

Use:

```text
current web
```

for:

```text
freshness
provider evaluation
production-like behavior
```

But results can change over time.

---

# 78. Benchmark Versioning

Use:

```text
benchmark_v1
benchmark_v2
...
```

Every experiment must record:

```text
benchmark version
model versions
policy versions
retrieval configuration
```

---

# 79. Experiment Tracking

Every experiment should store:

```text
experiment_id
code_version
model_versions
policy_version
dataset_version
configuration
metrics
cost
latency
timestamp
```

---

# 80. Reproducibility

A result should be reproducible from:

```text
code commit
+
configuration
+
dataset version
+
model versions
+
retrieval snapshot
```

where practical.

---

# 81. Statistical Significance

When comparing systems, do not rely only on:

```text
accuracy +1.2%
```

Use appropriate statistical tests or confidence intervals.

For paired classification experiments, bootstrap or paired tests can be useful depending on the metric.

---

# 82. Bootstrap Confidence Intervals

Report:

```text
metric
+
95% confidence interval
```

rather than only a point estimate.

---

# 83. Paired Evaluation

When possible, compare:

```text
System A
vs
System B
```

on exactly the same claims.

This reduces variance.

---

# 84. Ablation Framework

Every major subsystem should have an ablation.

Examples:

```text
No query expansion
No dense retrieval
No reranker
No provenance
No contradiction search
No temporal validation
No source scoring
No evidence graph
```

---

# 85. Ablation Matrix

Measure:

```text
Accuracy
Calibration
Evidence Recall
Latency
Cost
```

for each configuration.

---

# 86. Example Ablation

```text
Baseline
Hybrid Retrieval
+ Reranker
+ Source Quality
+ Provenance
+ Contradiction Search
+ Adaptive Retrieval
```

This reveals the marginal contribution of each layer.

---

# 87. Cost-Quality Frontier

For each architecture:

```text
quality
vs
cost
```

Plot the Pareto frontier.

The best system is not necessarily the most accurate one if the additional accuracy is prohibitively expensive.

---

# 88. Latency-Quality Frontier

Similarly evaluate:

```text
quality
vs
latency
```

This supports product-tier decisions.

---

# 89. Evaluation Tiers

Potential product modes:

### Fast

```text
low latency
low cost
moderate evidence depth
```

### Standard

```text
balanced
```

### Deep

```text
high evidence depth
high confidence
higher latency/cost
```

---

# 90. Regression Testing

Every change should run:

```text
unit tests
component tests
retrieval benchmark
verdict benchmark
critical adversarial suite
```

---

# 91. Golden Set

Maintain a small high-quality:

```text
golden evaluation set
```

for rapid regression detection.

It should contain:

```text
known difficult cases
high-impact failure cases
previous production failures
```

---

# 92. Production Failure Replay

Every important production failure should become:

```text
new regression test
```

This creates a continuously improving benchmark.

---

# 93. Error Taxonomy

Primary failure categories:

```text
CLAIM_ERROR
RETRIEVAL_ERROR
EVIDENCE_ERROR
SOURCE_ERROR
PROVENANCE_ERROR
TEMPORAL_ERROR
NUMERICAL_ERROR
NLI_ERROR
VERDICT_ERROR
CALIBRATION_ERROR
SYSTEM_ERROR
```

---

# 94. Error Attribution

A final incorrect verdict should be traced to the earliest meaningful failure.

Example:

```text
Wrong verdict
 ↓
Correct evidence aggregation?
 NO
 ↓
Wrong evidence?
 YES
 ↓
Retrieval failure?
 YES
```

The root cause is retrieval, not verdict logic.

---

# 95. Error Budget

Track error contribution:

```text
Claim Intelligence: 12%
Retrieval: 35%
Evidence Engineering: 28%
Verdict Engine: 15%
System failures: 10%
```

Illustrative only.

This helps prioritize engineering work.

---

# 96. Evaluation Dashboard

Track:

```text
Overall accuracy
Macro F1
Calibration
Evidence Recall
Contradiction Recall
Primary Source Recall
Abstention quality
Latency
Cost/request
```

and slice by:

```text
domain
claim type
difficulty
freshness
```

---

# 97. Evaluation Data Pipeline

```text
Benchmark Dataset
      ↓
Experiment Runner
      ↓
System
      ↓
Predictions
      ↓
Metric Engine
      ↓
Statistical Analysis
      ↓
Experiment Registry
      ↓
Dashboard / Report
```

---

# 98. Experiment Runner

The experiment runner should support:

```text
configuration
dataset selection
model selection
policy selection
retrieval mode
random seeds
parallel execution
```

---

# 99. Determinism

For reproducible experiments:

```text
seed random components
pin model versions
pin dependencies
record configuration
```

Live web search may remain nondeterministic and should be marked accordingly.

---

# 100. Model Evaluation

Every model replacement should answer:

```text
Does it improve the relevant metric?
Does it increase latency?
Does it increase memory?
Does it increase cost?
Does it create regressions?
```

---

# 101. Model Promotion Gate

A candidate model should pass:

```text
quality threshold
+
calibration threshold
+
latency threshold
+
memory threshold
```

before production.

---

# 102. Retrieval Provider Evaluation

Each provider should be evaluated on:

```text
evidence recall
source diversity
freshness
latency
failure rate
cost
```

by claim class.

---

# 103. Provider Routing Evaluation

Compare:

```text
static provider
vs
rule-based routing
vs
learned routing
```

---

# 104. Cache Evaluation

Measure:

```text
exact cache hit rate
semantic cache hit rate
false reuse rate
latency saved
cost saved
```

The most important metric is:

```text
false reuse rate
```

---

# 105. Semantic Cache Safety

A semantic cache is acceptable only if:

```text
reuse quality
```

remains above a defined threshold.

A cache hit that returns stale or semantically incorrect evidence is a correctness failure.

---

# 106. Human Evaluation

Some aspects require expert or user judgment:

```text
explanation quality
citation usefulness
claim decomposition quality
ambiguity handling
```

---

# 107. Human Evaluation Protocol

Use blinded comparison where possible:

```text
System A
vs
System B
```

with randomized order.

Evaluate:

```text
correctness
clarity
evidence sufficiency
citation usefulness
trustworthiness
```

---

# 108. Expert Evaluation

For high-stakes domains, use qualified evaluators.

Examples:

```text
medical
legal
financial
scientific
```

The exact evaluator requirements depend on the domain.

---

# 109. Trust Is Not Accuracy

User trust should not be used as a proxy for factual correctness.

A persuasive but wrong explanation is dangerous.

Therefore:

```text
objective correctness
```

must remain the primary metric.

---

# 110. Human Factors

Evaluate whether users understand:

```text
confidence
uncertainty
mixed evidence
unverified status
```

The UI should not visually imply certainty beyond what the evidence supports.

---

# 111. Product-Level Success Metrics

Potential metrics:

```text
verification completion rate
repeat usage
citation click-through
user correction rate
user-reported error rate
latency satisfaction
```

These are secondary to factual correctness.

---

# 112. Cost Metrics

Track:

```text
search cost
LLM cost
embedding compute
reranking compute
storage cost
bandwidth
database cost
```

---

# 113. Cost per Correct Verification

A useful product metric:

\[
CostPerCorrectVerification =
\frac{TotalCost}
{CorrectVerifications}
\]

This connects engineering economics to quality.

---

# 114. Marginal Cost of Accuracy

Measure:

\[
\Delta Cost / \Delta Accuracy
\]

for architectural changes.

Example:

```text
+1% accuracy
+
$0.0008/request
```

may be worthwhile.

Whereas:

```text
+0.1% accuracy
+
$0.02/request
```

may not be.

---

# 115. Cost-Aware Research Policy

The research controller should eventually optimize:

\[
Utility =
ExpectedAccuracyGain
-
\lambda Cost
-
\mu Latency
\]

where:

```text
λ
```

and:

```text
μ
```

reflect product priorities.

---

# 116. Multi-Objective Optimization

The product is optimizing:

```text
Accuracy
Calibration
Latency
Cost
Coverage
```

This is a Pareto optimization problem rather than a single-metric optimization problem.

---

# 117. Benchmark Governance

Benchmark datasets should be protected from accidental training contamination where possible.

Track:

```text
dataset provenance
creation date
label source
model exposure
```

---

# 118. Leakage Prevention

Avoid evaluating on examples that were:

```text
used to tune thresholds
used to train models
used repeatedly during prompt engineering
```

Maintain:

```text
train
validation
test
challenge
```

separation.

---

# 119. Challenge Set

Maintain a hidden or rarely exposed:

```text
challenge set
```

containing difficult examples.

Use it to detect overfitting to the public benchmark.

---

# 120. Benchmark Contamination

LLM-assisted components may have seen benchmark claims during training.

Where possible:

```text
prefer newly constructed or private challenge sets
```

for meaningful evaluation.

---

# 121. Evaluation Matrix

The minimum evaluation matrix should include:

| Dimension | Examples |
|---|---|
| Domain | science, finance, law, history |
| Claim type | numerical, causal, temporal |
| Difficulty | easy → expert |
| Evidence | support, contradiction, mixed |
| Freshness | historical → real-time |
| Source | primary → social |
| Ambiguity | low → high |
| Complexity | atomic → compound |

---

# 122. Minimum Acceptance Gates

Before calling the system production-ready, define explicit gates for:

```text
Verdict accuracy
Macro F1
Calibration
Evidence Recall
Contradiction Recall
Citation correctness
Abstention quality
Latency
Cost
```

The actual thresholds should be determined empirically and by product risk.

---

# 123. Research Log

Every major experiment should produce:

```text
Hypothesis
Configuration
Dataset
Metrics
Results
Statistical uncertainty
Interpretation
Decision
```

---

# 124. Example Experiment

### Hypothesis

Hybrid retrieval improves evidence recall over dense-only retrieval.

### Baseline

```text
Dense retrieval
```

### Treatment

```text
BM25 + dense + RRF
```

### Metrics

```text
Evidence Recall@10
Contradiction Recall@10
nDCG@10
latency
cost
```

### Decision

Promote only if the quality improvement justifies the cost.

---

# 125. Evaluation Architecture

```text
                  Benchmark Registry
                         │
                         ▼
                 Experiment Runner
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
        Static Corpus            Live Web
             │                       │
             └───────────┬───────────┘
                         ▼
                       Tathvyn
                         │
                         ▼
                     Predictions
                         │
                         ▼
                   Metric Engine
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
          Retrieval    Evidence   Verdict
           Metrics     Metrics    Metrics
              │          │          │
              └──────────┼──────────┘
                         ▼
                Statistical Analysis
                         │
                         ▼
                 Experiment Registry
                         │
                         ▼
                    Dashboard
```

---

# 126. Evaluation Invariants

### INV-EV-001

Every major architectural change must be measurable.

### INV-EV-002

Retrieval must be evaluated independently of verdict accuracy.

### INV-EV-003

Evidence quality must be evaluated independently of retrieval.

### INV-EV-004

Confidence must be calibrated.

### INV-EV-005

Abstention must be evaluated as a first-class behavior.

### INV-EV-006

Contradiction retrieval must be explicitly benchmarked.

### INV-EV-007

Primary-source retrieval must be explicitly benchmarked.

### INV-EV-008

Production failures must become regression tests.

### INV-EV-009

Experiments must record code, model, policy, and dataset versions.

### INV-EV-010

Quality improvements must be evaluated against cost and latency.

---

# 127. Research Questions

The evaluation program should answer:

1. What is the true error contribution of each subsystem?
2. How much does retrieval quality determine final verdict quality?
3. Does provenance-aware reasoning improve calibration?
4. How much does contradiction search reduce false positives?
5. What is the optimal abstention policy?
6. Which confidence features are most predictive?
7. How much accuracy can be gained per unit cost?
8. How does performance degrade under temporal drift?
9. How robust is the system to adversarial claim mutations?
10. How well does the system generalize across domains?
11. How much does live-web variability affect benchmark results?
12. Which architectural components are actually worth their complexity?

---

# 128. Final Principle

> **If we cannot measure an improvement, we should not assume we engineered one.**

Tathvyn should be developed as an empirical system:

```text
Hypothesis
   ↓
Architecture
   ↓
Experiment
   ↓
Measurement
   ↓
Error Analysis
   ↓
Revision
   ↓
Regression Test
```

The benchmark is not a report card at the end.

It is the feedback loop that drives the entire engineering process.

---

# 129. Next Step

The next document should be:

**`17-verdict-engine-and-calibration.md`**

It will define the actual decision layer:

- evidence aggregation;
- support/contradiction balancing;
- provenance-aware weighting;
- claim-level scoring;
- compound-claim aggregation;
- conflict resolution;
- uncertainty;
- calibration;
- abstention;
- verdict thresholds;
- confidence intervals;
- explanation generation boundaries;
- and how Tathvyn converts an evidence graph into a **defensible final decision without pretending to know more than the evidence supports**.
