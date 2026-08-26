# Tathvyn — Problem Definition

## 1. Problem Statement

Given a natural-language factual claim, Tathvyn must determine the state of available evidence surrounding that claim.

The system must not simply classify:

```text
claim → true / false
```

Instead, it must construct an evidence-backed assessment:

```text
claim
  ↓
claim interpretation
  ↓
evidence discovery
  ↓
evidence assessment
  ↓
source/provenance analysis
  ↓
reasoning
  ↓
verification state
```

The conclusion describes what the available evidence justifies, not absolute reality.

## 2. Formal Problem Model

Let:

- \(C\) = normalized claim;
- \(A = \{a_1, a_2, ..., a_n\}\) = atomic claims;
- \(E = \{e_1, e_2, ..., e_m\}\) = retrieved evidence;
- \(P\) = provenance and source information;
- \(T\) = temporal constraints and validity;
- \(I\) = source independence;
- \(U\) = uncertainty.

Conceptually:

\[
V = f(C, A, E, P, T, I, U)
\]

The result should emerge from multiple independently evaluable stages rather than one model prediction.

## 3. Definition of a Claim

A claim is a declarative proposition asserting one or more facts about entities, events, relationships, quantities, states, or occurrences that can potentially be evaluated against evidence.

Examples:

- "The Earth has a solid inner core."
- "India's GDP grew by 8.2% in 2024."
- "Company X acquired Company Y in 2023."
- "Smoking increases the risk of lung cancer."

## 4. Claim Categories

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

A claim may eventually have multiple dimensions rather than one mutually exclusive class.

## 5. Verifiability

Claims should be assessed as:

- VERIFIABLE
- PARTIALLY_VERIFIABLE
- TIME_DEPENDENT
- CONTEXT_DEPENDENT
- UNVERIFIABLE

This classification can prevent wasted computation on claims that cannot reasonably be verified.

## 6. Atomic Claim Decomposition

Compound claims may contain multiple independently verifiable propositions.

Example:

> "The Indian government increased the GST rate on electric vehicles from 12% to 18% in 2025."

Potential atomic propositions:

1. The relevant GST rate was 12%.
2. The rate became 18%.
3. The change occurred in 2025.
4. The change applied to electric vehicles.
5. The change was implemented through the relevant government policy mechanism.

Each atomic claim receives its own evidence and verification state.

## 7. Verification Objectives

Tathvyn must:

1. understand the claim;
2. decompose compound claims;
3. identify entities and temporal constraints;
4. determine verifiability;
5. plan research;
6. retrieve supporting evidence;
7. retrieve contradicting evidence;
8. seek primary evidence;
9. extract relevant passages;
10. assess evidence relationships;
11. evaluate source quality;
12. detect source dependence and duplication;
13. validate temporal relevance;
14. aggregate evidence;
15. determine evidence sufficiency;
16. produce an uncertainty-aware verdict.

## 8. Evidence Search Objectives

Research should include:

### Supporting search

What evidence suggests the claim is correct?

### Contradicting search

What evidence suggests the claim is incorrect?

### Primary-source search

What is the closest available source to the underlying fact, event, measurement, or statement?

## 9. Verification States

Internal atomic-claim states:

```text
UNRESEARCHED
    ↓
RESEARCHING
    ↓
EVIDENCE_FOUND
    ↓
EVIDENCE_ASSESSED
    ↓
SUPPORTED
REFUTED
CONFLICTED
INSUFFICIENT
UNVERIFIABLE
```

A lack of evidence must not automatically be interpreted as evidence of falsity.

## 10. Overall Verdict Taxonomy

The canonical taxonomies are formally defined in [00-canonical-enums.md](file:///c:/Projects/Tathvyn/Tathvyn_docs/00-canonical-enums.md).

| Verdict | Meaning |
|---|---|
| SUPPORTED | Strong, independent evidence substantiates the material claim |
| REFUTED | Strong evidence directly contradicts the material claim |
| PARTIALLY_SUPPORTED | Some material components are supported while others are unsupported, contradicted, or distorted |
| INSUFFICIENT_EVIDENCE | Relevant evidence was sought but is inadequate for a reliable conclusion |
| UNVERIFIABLE | The proposition cannot reasonably be evaluated using available external evidence |

> **Note on Distorted / Misleading Claims**: Cases where literal facts are accurate but framing, omission, or context distorts the meaning are classified under `PARTIALLY_SUPPORTED` with a `framing_concerns` metadata flag in MVP. Standalone `MISLEADING` verdict classification is deferred to V2.

## 11. Evidence Requirements

Evidence should eventually be assessed for:

- relevance;
- entailment;
- contradiction;
- source quality;
- source independence;
- temporal validity;
- specificity;
- provenance;
- consistency;
- claim coverage.

No single dimension should be treated as a universal proxy for truth.

## 12. Accuracy Requirements

Accuracy must be decomposed into:

### Claim understanding

Correct interpretation and decomposition.

### Retrieval

Ability to find evidence required for a correct assessment.

### Evidence assessment

Correct identification of support, contradiction, context, and insufficiency.

### Source analysis

Correct assessment of source characteristics and independence.

### Verdict

Correct final classification.

### Calibration

Confidence should correspond to empirical reliability.

### Robustness

Performance should remain acceptable under ambiguity, contradiction, duplication, outdated evidence, and adversarial inputs.

## 13. Product Constraints

Tathvyn must simultaneously optimize:

- verification quality;
- evidence quality;
- latency;
- retrieval cost;
- inference cost;
- storage cost;
- scalability;
- reliability.

Cost optimization means **maximizing quality per unit of resources**, not simply minimizing expenditure.

## 14. Verification Budget

Every request should eventually receive limits such as:

```text
max_search_calls
max_documents
max_passages
max_model_inferences
max_llm_calls
max_tokens
max_latency
max_cost
research_depth_limit
```

The research controller can allocate more resources to difficult claims and fewer to straightforward claims.

## 15. Adaptive Research Hypothesis

A core system hypothesis is:

> **A hierarchical verification system that allocates computation according to claim complexity and evidence uncertainty can achieve a better quality-cost tradeoff than a fixed-depth RAG/LLM pipeline.**

This must be experimentally evaluated rather than assumed.

## 16. Non-Functional Requirements

### Performance

Measure:

- p50 latency;
- p95 latency;
- throughput;
- queue latency.

### Reliability

Handle:

- search-provider failures;
- model failures;
- scraping failures;
- partial evidence;
- malformed inputs.

### Observability

Every verification should have an auditable trace:

```text
request
 → claim analysis
 → research plan
 → queries
 → search results
 → documents
 → evidence
 → assessments
 → reasoning
 → verdict
```

### Reproducibility

A result should be reproducible when the same claim, evidence snapshot, model versions, and configuration are used.

## 17. Security Requirements

Retrieved content is untrusted data.

The system must eventually defend against:

- prompt injection;
- malicious webpages;
- SEO manipulation;
- poisoned retrieval;
- fabricated citations;
- source impersonation;
- manipulated metadata;
- duplicate misinformation;
- content laundering.

## 18. Core System Invariant

> **No final verdict may depend solely on a language model's internal knowledge or judgment.**

LLMs may assist with claim interpretation, research planning, evidence synthesis, and uncertainty analysis. They should not be treated as the evidence itself.

## 19. Evaluation Contract

| Subsystem | Example metrics |
|---|---|
| Claim classification | Macro-F1 |
| Atomic decomposition | Precision / Recall |
| Entity recognition | Entity F1 |
| Retrieval | Recall@K, MRR, nDCG |
| Evidence assessment | Macro-F1 |
| Source classification | Macro-F1 |
| Duplicate detection | Precision / Recall |
| Verdict | Macro-F1, confusion matrix |
| Confidence | ECE, Brier score |
| Grounding | Evidence precision / recall |
| System | p50 / p95 latency |
| Economics | Cost / verification |
| Scaling | Throughput |

## 20. Design Boundaries

The problem definition does not prescribe:

- a specific LLM;
- a specific embedding model;
- a specific NLI model;
- a vector database;
- LangGraph;
- a search provider;
- a cloud provider;
- or a deployment topology.

Those decisions must be derived from requirements and validated experimentally.

## 21. Engineering Principle

> **Do not add complexity until a measurable failure mode justifies it.**

Every architectural component should exist because it solves a defined verification, quality, cost, reliability, or scalability problem.
