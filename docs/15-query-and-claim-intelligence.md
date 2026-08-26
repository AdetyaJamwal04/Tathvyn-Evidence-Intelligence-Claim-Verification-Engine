# Tathvyn — Query and Claim Intelligence

## 1. Purpose

Claim and Query Intelligence is the front end of the Tathvyn verification pipeline.

Its job is to answer:

> **What exactly is being asserted, which parts are independently verifiable, and what information must be retrieved to verify them?**

A retrieval system cannot compensate for a malformed verification target.

If the system misunderstands:

```text
entity
time
metric
scope
relationship
negation
causality
```

then even perfect search can produce the wrong evidence.

---

# 2. Pipeline Position

```text
User Input
    ↓
Input Normalization
    ↓
Claim Detection
    ↓
Claim Classification
    ↓
Claim Segmentation
    ↓
Atomic Decomposition
    ↓
Entity Extraction
    ↓
Temporal Extraction
    ↓
Numerical Extraction
    ↓
Scope / Qualifier Extraction
    ↓
Verifiability Analysis
    ↓
Complexity Estimation
    ↓
Verification Plan
    ↓
Query Generation
    ↓
Retrieval
```

---

# 3. Core Principle

The system must distinguish:

```text
Text
```

from:

```text
Proposition
```

Example:

> "I think the economy is doing badly."

This contains an opinion.

Whereas:

> "India's GDP contracted by 2% in 2025."

contains a factual proposition.

---

# 4. Claim Taxonomy

Claims should support multi-label classification.

Potential labels:

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

These labels can overlap.

---

# 5. Factual Claim

A factual claim asserts something that can in principle be evaluated against evidence.

Example:

> "The company launched the product in June 2026."

---

# 6. Numerical Claim

Contains a measurable quantity.

Examples:

```text
GDP grew 8.2%.
The population is 1.4 billion.
The drug reduced risk by 30%.
```

Numerical claims require structured extraction.

---

# 7. Temporal Claim

Contains a time-dependent proposition.

Examples:

```text
X happened in 2024.
X is currently CEO.
X existed before Y.
```

Temporal validity must be explicitly represented.

---

# 8. Comparative Claim

Compares two or more entities.

Examples:

```text
A is larger than B.
A grew faster than B.
A is the largest company in the sector.
```

The comparison metric must be identified.

---

# 9. Causal Claim

Claims:

```text
A caused B
```

or equivalent language.

Examples:

```text
Smoking causes disease X.
Policy Y reduced inflation.
```

Causal claims require stricter evidence.

---

# 10. Attribution Claim

Claims that a person or organization said, wrote, announced, or did something.

Example:

> "The CEO said the company would expand into India."

Verification requires:

```text
identity
statement
source
time
context
```

---

# 11. Historical Claim

Claims about past events.

Example:

> "The treaty was signed in 1846."

Historical verification may require:

```text
primary records
archives
scholarly sources
contemporaneous accounts
```

---

# 12. Predictive Claim

Claims about future events.

Examples:

```text
Company X will launch product Y next year.
GDP will grow 7% in 2027.
```

These should not be evaluated using the same framework as established historical facts.

The system may classify them as:

```text
PREDICTION
```

rather than factual verification.

---

# 13. Opinion / Normative Claim

Examples:

```text
X is the best phone.
Policy Y is terrible.
This movie is boring.
```

These may not be objectively verifiable unless the claim contains embedded factual propositions.

---

# 14. Mixed Claims

Example:

> "The new policy is terrible because it increased unemployment by 4%."

This contains:

```text
Opinion:
policy is terrible

Factual:
unemployment increased 4%
```

The system should separate them.

---

# 15. Claim Detection

Input may contain:

```text
single claim
multiple claims
questions
opinions
instructions
narrative text
mixed content
```

The system must identify which spans actually contain verifiable propositions.

---

# 16. Claim Span

Represent:

```text
claim_id
source_text
start_offset
end_offset
normalized_text
```

This preserves traceability to the original user input.

---

# 17. Sentence Is Not Always a Claim

A single sentence can contain:

```text
multiple propositions
```

Example:

> "Company X acquired Company Y in 2025 for $10 billion."

Potential atomic propositions:

```text
X acquired Y
Acquisition occurred in 2025
Transaction value was $10B
```

---

# 18. Claim Segmentation

Segmentation should detect:

```text
conjunctions
clauses
relative clauses
conditionals
comparatives
causal relationships
enumerations
```

---

# 19. Atomic Claim Principle

An atomic claim should represent a proposition that can be independently assessed with evidence.

It should be:

```text
specific
testable
semantically complete
non-overlapping where possible
```

---

# 20. Atomic Claim Example

Original:

> "Company X acquired Company Y in 2025 for $10B, making it the largest acquisition in the sector."

Atomic claims:

```text
A1:
Company X acquired Company Y.

A2:
The acquisition occurred in 2025.

A3:
The transaction value was $10B.

A4:
The acquisition was the largest in the sector.
```

---

# 21. Decomposition Constraints

The decomposition system must ensure:

### Coverage

All material propositions are represented.

### Faithfulness

No information is invented.

### Independence

Atomic claims can be assessed separately where possible.

### Reconstruction

The atomic claims collectively preserve the original meaning.

---

# 22. Reconstruction Test

Given:

```text
Original Claim
```

and:

```text
Atomic Claims
```

ask:

> Can the original proposition be reconstructed from the atomic representation without adding or losing material information?

If not:

```text
decomposition_failed
```

---

# 23. Over-Decomposition

Avoid splitting a proposition unnecessarily.

Bad:

```text
X
acquired
Y
in
2025
```

Better:

```text
X acquired Y in 2025.
```

The atomic unit should preserve semantic structure.

---

# 24. Under-Decomposition

Avoid keeping materially independent claims together.

Bad:

```text
X acquired Y in 2025 for $10B and the deal was the largest ever.
```

if each component requires different evidence.

---

# 24b. Decomposition Edge Cases and Depth Policy

### 1. Already-Atomic Claims
If the claim classifier or parser determines that the input represents a single indivisible proposition, the system generates a 1-element atomic claim list with `is_atomic=True` and `decomposition_depth=0`. No further decomposition is attempted.

### 2. Maximum Decomposition Depth
Decomposition depth is capped at 1. Atomic claims are terminal nodes and cannot be recursively decomposed into sub-atomic claims.

### 3. Anti-Hallucination & Entity Preservation Check
Before accepting generated atomic claims:
- Check that all named entities in atomic claims exist in or are direct coreferences of entities in the parent claim.
- Check that no new numerical values, dates, or causal relationships absent from the parent claim were injected.
- If validation fails, reject the decomposition and fall back to single-claim verification.

---

# 25. Claim Dependency Graph

Atomic claims may depend on each other.

Example:

```text
A1:
X acquired Y.

A2:
The transaction occurred in 2025.

A3:
The transaction value was $10B.

A4:
This was the largest acquisition.
```

A4 may depend on:

```text
A1 + A3 + sector definition
```

Represent these dependencies explicitly.

---

# 26. Claim Graph

```text
             Parent Claim
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
       A1        A2        A3
        │                   │
        └─────────┬─────────┘
                  ▼
                 A4
```

---

# 27. Entity Extraction

Extract entities from each atomic claim.

Potential entity types:

```text
PERSON
ORGANIZATION
PRODUCT
LOCATION
EVENT
LAW
POLICY
COUNTRY
DATE
METRIC
```

---

# 28. Entity Canonicalization

Normalize:

```text
Apple
Apple Inc.
Apple Computer Inc.
```

when they refer to the same entity.

Do not merge aliases without sufficient evidence.

---

# 29. Entity Ambiguity

Example:

```text
Washington
```

may refer to:

```text
Washington State
Washington, D.C.
George Washington
```

The system should preserve:

```text
candidate entities
+
confidence
```

until resolved.

---

# 30. Entity Resolution Pipeline

```text
Mention
 ↓
NER
 ↓
Candidate generation
 ↓
Context matching
 ↓
Knowledge base
 ↓
Temporal validation
 ↓
Resolved / ambiguous
```

---

# 31. Entity Attributes

For each resolved entity:

```text
entity_id
canonical_name
aliases
type
country
industry
valid_time
confidence
```

---

# 32. Temporal Extraction

Extract all temporal expressions.

Examples:

```text
2025
June 2026
last year
currently
before the election
after the merger
during the pandemic
```

---

# 33. Temporal Normalization

Convert relative expressions into explicit ranges where possible.

Example:

```text
"last year"
```

becomes:

```text
reference_date = request_time
range = previous calendar year
```

The exact semantic interpretation must be recorded.

---

# 34. Temporal Scope

Represent:

```text
point
interval
before
after
during
since
until
recurring
current
unknown
```

---

# 35. Current-State Claims

Words like:

```text
currently
today
now
is
remains
still
```

create freshness requirements.

The verification policy should mark them as:

```text
FRESHNESS_SENSITIVE
```

---

# 36. Temporal Ambiguity

Example:

> "X was the largest company."

Largest when?

The system should identify:

```text
missing temporal scope
```

and either:

```text
infer cautiously
```

or:

```text
mark ambiguity
```

---

# 37. Numerical Extraction

Extract:

```text
value
unit
metric
period
qualifier
comparison
```

Example:

> "GDP grew by 8.2% year-over-year in Q4."

Structured:

```text
metric = GDP
value = 8.2
unit = percent
period = Q4
comparison = year-over-year
```

---

# 38. Unit Normalization

Normalize:

```text
$10 billion
10B USD
USD 10bn
```

into:

```text
10,000,000,000 USD
```

while preserving original representation.

---

# 39. Percentage vs Percentage Point

The system must distinguish:

```text
8% increase
```

from:

```text
8 percentage-point increase
```

These are mathematically different.

---

# 40. Numerical Qualifiers

Capture:

```text
approximately
more than
less than
at least
up to
nearly
around
estimated
```

Example:

> "More than 10 million people."

must not become:

```text
exactly 10,000,000
```

---

# 41. Comparative Operators

Extract:

```text
>
<
≥
≤
=
≈
largest
smallest
more
less
faster
slower
```

---

# 42. Scope Extraction

Claims may include scope:

```text
country
region
population
industry
age group
product category
time period
```

Example:

> "India's urban population..."

The geography is part of the proposition.

---

# 43. Qualifier Extraction

Capture:

```text
only
mostly
generally
typically
under certain conditions
according to
estimated
reported
allegedly
```

Qualifiers can materially change truth conditions.

---

# 44. Negation Detection

Explicitly represent:

```text
not
never
no
without
didn't
cannot
```

Negation errors are high-impact.

---

# 45. Conditional Claims

Example:

> "If inflation remains high, interest rates will increase."

This is not equivalent to:

> "Interest rates will increase."

Represent:

```text
condition
conclusion
```

separately.

---

# 46. Modal Language

Capture:

```text
may
might
could
likely
probably
certainly
must
will
```

These change the epistemic strength of the claim.

---

# 47. Attribution Markers

Detect:

```text
according to
reported by
said
claimed
alleged
estimated
researchers found
officials stated
```

These can alter what exactly needs to be verified.

---

# 48. Source-Relative Claims

Example:

> "According to NASA, X happened."

The claim has two components:

```text
NASA stated X.
X itself is true.
```

The system should not automatically conflate them.

---

# 49. Claim Verifiability

Classify claims into:

```text
DIRECTLY_VERIFIABLE
INDIRECTLY_VERIFIABLE
PARTIALLY_VERIFIABLE
CURRENTLY_UNVERIFIABLE
NON_FACTUAL
```

---

# 50. Directly Verifiable

Examples:

```text
date
number
event
official statement
document existence
```

---

# 51. Indirectly Verifiable

Examples:

```text
causal claims
historical interpretation
complex comparative claims
```

These require multiple evidence types.

---

# 52. Partially Verifiable

Example:

> "This is the best smartphone."

The objective component:

```text
price
battery
performance
```

may be measurable.

"Best" itself depends on criteria.

---

# 53. Non-Factual

Examples:

```text
I love this phone.
This movie is boring.
Policy X is morally wrong.
```

The system should not fabricate a factual verdict.

---

# 54. Claim Complexity

Complexity estimation can use:

```text
atomic claim count
entity count
temporal expressions
numerical expressions
causal markers
comparatives
ambiguity
domain specificity
required source types
```

---

# 55. Complexity Score

Conceptually:

\[
Complexity =
f(
atomicity,
ambiguity,
entities,
time,
numbers,
causality,
domain
)
\]

The initial implementation can be rule-based.

---

# 56. Difficulty Classes

```text
TRIVIAL
SIMPLE
MODERATE
COMPLEX
HIGHLY_COMPLEX
```

These classes influence research budget.

---

# 57. Claim Risk

Complexity is not the same as risk.

Risk may depend on:

```text
potential harm
domain
user context
consequence
uncertainty
```

A simple medical claim can be high-risk.

---

# 58. High-Stakes Detection

Potential categories:

```text
MEDICAL
LEGAL
FINANCIAL
SAFETY
PUBLIC HEALTH
PERSONAL REPUTATION
```

High-stakes claims should trigger stricter evidence policies.

---

# 59. Domain Classification

Classify claims into domains such as:

```text
Science
Medicine
Finance
Politics
Law
Technology
History
Sports
Business
Climate
General
```

Multi-label classification may be appropriate.

---

# 60. Domain-Specific Verification Policy

Domain classification influences:

```text
source requirements
retrieval strategy
research depth
confidence thresholds
primary-source preference
```

---

# 61. Claim Normalization

Normalize:

```text
whitespace
punctuation
aliases
dates
units
numbers
```

without destroying original wording.

Maintain:

```text
raw_text
normalized_text
```

---

# 62. Claim Fingerprinting

Generate:

```text
exact hash
normalized hash
semantic embedding
```

These support:

```text
deduplication
cache lookup
semantic reuse
analytics
```

---

# 63. Claim Equivalence

Two claims may be semantically equivalent.

Example:

```text
"India's GDP grew 8.2%."

"India recorded 8.2% GDP growth."
```

But:

```text
"India's GDP growth was 8.2 percentage points."
```

is not equivalent.

Equivalence must be conservative.

---

# 64. Claim Contradiction

Claims can be structurally compared.

Example:

```text
X acquired Y.
```

vs:

```text
X did not acquire Y.
```

The system can detect a direct contradiction without web search.

---

# 65. Claim Mutation Testing

Generate controlled mutations:

```text
entity swap
date swap
number swap
unit swap
negation
geography swap
```

Example:

```text
8.2%
→
9.2%
```

This creates adversarial evaluation data.

---

# 66. Query Generation

Query generation should be based on structured claim representation.

Input:

```text
entity
predicate
object
time
metric
scope
objective
```

Output:

```text
search queries
```

---

# 67. Query Intent Types

Queries should have explicit intent:

```text
DIRECT
SUPPORT
CONTRADICTION
PRIMARY_SOURCE
CONTEXT
ENTITY
TEMPORAL
NUMERICAL
PROVENANCE
```

---

# 68. Query Templates

Example:

```text
{entity} {predicate} {object} {time}
```

and:

```text
{entity} official {object} {time}
```

and:

```text
{entity} did not {predicate} {object}
```

---

# 69. Query Diversity

Multiple queries should vary:

```text
wording
source type
specificity
time
objective
```

Avoid generating ten paraphrases that retrieve the same documents.

---

# 70. Query Quality

Evaluate a query based on:

```text
retrieval recall
unique evidence yield
source diversity
latency
cost
```

The best query is not necessarily the most linguistically natural one.

---

# 71. Query Selection

Given candidate queries:

\[
q^* =
\arg\max_q
\frac{ExpectedEvidenceGain(q)}
{ExpectedCost(q)}
\]

This becomes a central research-agent decision.

---

# 72. Query Redundancy

Two queries are redundant if they retrieve nearly identical candidate sets.

Use:

```text
query embedding similarity
+
result overlap
```

to reduce redundancy.

---

# 73. Query Expansion With LLM

LLM query generation should be used for:

```text
complex language
rare terminology
implicit relationships
cross-domain reasoning
```

but validated before execution.

---

# 74. LLM Query Validation

Check:

```text
Does query preserve entities?
Does it preserve dates?
Does it preserve negation?
Does it introduce unsupported assumptions?
```

---

# 75. Query Injection Safety

Never allow a retrieved document to modify query-generation instructions.

Only trusted system state can control query generation.

---

# 76. Claim Intelligence Output

The subsystem should produce:

```text
ClaimAnalysis
├── normalized_claim
├── claim_type
├── domain
├── atomic_claims
├── entities
├── temporal_scope
├── numerical_facts
├── qualifiers
├── verifiability
├── complexity
├── risk
└── verification_policy
```

---

# 77. Verification Plan

The Claim Intelligence layer should produce a preliminary plan:

```text
atomic claims
required evidence
source preferences
freshness
query intents
research budget
```

---

# 78. Example Verification Plan

Claim:

> "Company X acquired Company Y for $10B in 2025, making it the largest acquisition in the industry."

Plan:

```text
A1:
X acquired Y
→ primary corporate / regulatory source

A2:
Transaction occurred in 2025
→ official announcement

A3:
Value = $10B
→ filing / transaction report

A4:
Largest in industry
→ comparative industry dataset
→ historical transaction comparison
```

A4 requires a substantially deeper retrieval strategy.

---

# 79. Claim Intelligence Failure Modes

Initial taxonomy:

```text
CLAIM_MISSED
WRONG_CLAIM_SPAN
UNDER_DECOMPOSITION
OVER_DECOMPOSITION
ENTITY_ERROR
ENTITY_AMBIGUITY
TEMPORAL_ERROR
NUMERICAL_ERROR
UNIT_ERROR
NEGATION_ERROR
QUALIFIER_LOSS
DOMAIN_ERROR
VERIFIABILITY_ERROR
QUERY_DRIFT
QUERY_REDUNDANCY
```

---

# 80. Evaluation Dataset

Build a labeled claim-intelligence dataset containing:

```text
raw text
claim spans
atomic claims
claim types
entities
dates
numbers
qualifiers
domain
verifiability
gold query intents
```

---

# 81. Claim Detection Metrics

Evaluate:

```text
span precision
span recall
span F1
```

---

# 82. Claim Classification Metrics

Use:

```text
macro F1
micro F1
per-class F1
confusion matrix
```

Multi-label metrics should be used where appropriate.

---

# 83. Decomposition Metrics

Evaluate:

```text
coverage
faithfulness
atomicity
redundancy
reconstruction accuracy
```

A decomposition can have high recall while still being semantically poor.

---

# 84. Entity Metrics

Evaluate:

```text
NER F1
entity linking accuracy
ambiguity detection accuracy
```

---

# 85. Temporal Metrics

Evaluate:

```text
temporal span F1
normalization accuracy
relation classification
```

---

# 86. Numerical Metrics

Evaluate:

```text
value extraction accuracy
unit accuracy
metric accuracy
period accuracy
operator accuracy
```

---

# 87. Query Metrics

Evaluate:

```text
Recall@K
unique evidence yield
primary-source recall
contradiction recall
query redundancy
cost/query
```

---

# 88. End-to-End Metrics

Ultimately measure:

```text
Claim Intelligence
       ↓
Retrieval
       ↓
Evidence
       ↓
Verdict
```

The final metric is:

```text
verification quality
```

---

# 89. Claim Intelligence Ablations

Compare:

```text
Rules only
Rules + NER
Rules + local models
Rules + LLM
Full hybrid
```

Measure:

```text
quality
latency
cost
```

---

# 90. Model Routing

Claim Intelligence should determine when expensive reasoning is justified.

Example:

```text
Simple factual claim
→ deterministic pipeline

Moderate claim
→ local ML

Complex compound claim
→ LLM-assisted decomposition

Ambiguous claim
→ deeper entity / temporal resolution
```

---

# 91. Claim Intelligence Caching

Cache:

```text
claim analysis
entity resolution
temporal normalization
query plans
```

using versioned keys.

---

# 92. Cache Key

Conceptually:

```text
normalized_claim_hash
+
claim_model_version
+
policy_version
```

---

# 93. Claim Reuse

If the same claim is repeatedly verified:

```text
reuse claim analysis
```

but not necessarily:

```text
reuse final verdict
```

because evidence may have changed.

---

# 94. Semantic Reuse

Paraphrased claims may reuse:

```text
entity resolution
domain classification
query strategy
```

only when equivalence is confidently established.

---

# 95. Human Review Trigger

Claim Intelligence should be able to request review when:

```text
ambiguity is unresolved
high-stakes claim
complex legal language
highly ambiguous entity
insufficient semantic interpretation
```

---

# 96. Claim Intelligence API

Conceptually:

```python
analyze_claim(
    text,
    context,
    policy
) -> ClaimAnalysis
```

And:

```python
plan_verification(
    claim_analysis,
    budget
) -> VerificationPlan
```

---

# 97. Claim Intelligence Pseudocode

```text
analyze_claim(text):

    normalized = normalize(text)

    spans = detect_claims(
        normalized
    )

    analyses = []

    for span in spans:

        classification = classify(span)

        atomic = decompose(span)

        validate_reconstruction(
            span,
            atomic
        )

        entities = extract_entities(
            atomic
        )

        temporal = extract_temporal(
            atomic
        )

        numerical = extract_numbers(
            atomic
        )

        qualifiers = extract_qualifiers(
            atomic
        )

        domain = classify_domain(
            atomic
        )

        verifiability = assess_verifiability(
            atomic
        )

        complexity = estimate_complexity(
            atomic
        )

        risk = estimate_risk(
            atomic,
            domain
        )

        analyses.append(...)

    return ClaimAnalysis(...)
```

---

# 98. Verification Planning Pseudocode

```text
plan_verification(claim_analysis):

    for atomic_claim in claim_analysis.atomic_claims:

        objectives = determine_objectives(
            atomic_claim
        )

        source_requirements = determine_sources(
            atomic_claim
        )

        query_intents = determine_queries(
            atomic_claim
        )

        budget = allocate_budget(
            complexity,
            risk
        )

    return VerificationPlan(...)
```

---

# 99. Claim Intelligence Invariants

### INV-CI-001

The system must preserve the original claim text.

### INV-CI-002

Every atomic claim must trace back to its parent claim.

### INV-CI-003

Decomposition must not invent information.

### INV-CI-004

Entity ambiguity must remain explicit until resolved.

### INV-CI-005

Temporal scope must not be silently inferred when materially ambiguous.

### INV-CI-006

Numbers and units must be represented separately.

### INV-CI-007

Negation and qualifiers must survive normalization.

### INV-CI-008

Opinion must not be converted into factual verification.

### INV-CI-009

Query generation must preserve claim semantics.

### INV-CI-010

Expensive reasoning should be used selectively.

---

# 100. Research Questions

The system should empirically determine:

1. How much does explicit claim decomposition improve retrieval?
2. How much do entity-resolution errors affect final verdicts?
3. Which temporal normalization strategies work best?
4. How much does structured numerical extraction improve accuracy?
5. How often does LLM decomposition outperform deterministic decomposition?
6. What is the optimal complexity classifier?
7. How much query diversity is actually useful?
8. Can query selection be learned from retrieval outcomes?
9. How much semantic claim caching is safe?
10. Which claim types should receive deeper research by default?

---

# 101. Final Principle

> **Before Tathvyn asks whether something is true, it must first establish what exactly is being asserted.**

The Claim Intelligence layer should transform:

```text
Natural Language
        ↓
Structured Proposition
        ↓
Atomic Claims
        ↓
Verification Objectives
        ↓
Research Plan
```

Only then should the system begin evidence acquisition.

---

# 102. Next Step

The next document should be:

**`16-evaluation-and-benchmarking.md`**

This is where the project becomes genuinely research-grade.

It will define:

- benchmark construction;
- gold-label methodology;
- retrieval benchmarks;
- evidence benchmarks;
- verdict benchmarks;
- calibration;
- abstention;
- adversarial testing;
- ablation studies;
- human evaluation;
- statistical significance;
- regression testing;
- error taxonomy;
- and the metrics required to prove that Tathvyn is actually improving rather than merely becoming more complex.
