# Tathvyn — Model Architecture

## 1. Purpose

This document translates the Tathvyn methodology into a concrete machine-learning architecture.

The objective is not to maximize model size.

The objective is to maximize:

```text
Verification Quality
        ×
Reliability
        ×
Scalability
```

under explicit constraints on:

```text
Cost
Latency
Memory
Throughput
Operational Complexity
```

The model architecture must therefore be:

- modular;
- replaceable;
- benchmark-driven;
- cost-aware;
- observable;
- versioned.

---

# 2. Model Architecture Principle

Tathvyn should not depend on one "fact-checking model."

Instead:

```text
Claim Understanding
        ↓
Retrieval
        ↓
Reranking
        ↓
Evidence Assessment
        ↓
Source / Provenance Analysis
        ↓
Evidence Aggregation
        ↓
Verdict
```

Different models solve different problems.

---

# 3. Model Responsibilities

| Component | Primary Responsibility |
|---|---|
| Claim Classifier | Identify claim characteristics |
| Claim Decomposer | Convert compound claims into atomic claims |
| Entity Resolver | Resolve entities and ambiguity |
| Query Generator | Generate research queries |
| Embedding Model | Semantic candidate retrieval |
| Reranker | Fine-grained relevance ranking |
| NLI Model | Entailment / contradiction |
| Numerical Parser | Structured numerical comparison |
| Temporal Resolver | Temporal normalization |
| Source Scorer | Source utility estimation |
| Aggregator | Evidence-level decision |
| LLM | Complex reasoning / planning / explanation |

The system should avoid asking one model to perform all of these functions.

---

# 4. Model Selection Philosophy

A model should be selected because it performs a measurable role well.

Selection criteria:

```text
Task Accuracy
Calibration
Latency
Memory
Throughput
Cost
Robustness
License
Language Coverage
Hardware Requirements
Operational Complexity
```

Model popularity is not a selection criterion.

---

# 5. Local vs API Decision

Each model should be classified as:

```text
LOCAL
API
HYBRID
```

## Local candidates

Prefer local inference when:

- the task is high-volume;
- the model is small;
- latency matters;
- privacy matters;
- inference is predictable;
- quality is sufficient.

Examples:

```text
Embeddings
Reranking
NLI
NER
Numerical parsing
Entity linking
```

## API candidates

API models may be appropriate when:

- reasoning complexity is high;
- task frequency is lower;
- model capability is difficult to reproduce locally;
- latency/cost remains acceptable.

Examples:

```text
Complex claim decomposition
Difficult conflict analysis
Research planning
Explanation generation
```

---

# 6. The LLM Must Not Be the Truth Oracle

A critical architecture rule:

```text
LLM
   ↓
Reasoning / planning
```

not:

```text
LLM
   ↓
Ground truth
```

The LLM should reason over retrieved evidence.

It should not replace the evidence layer.

---

# 7. Proposed Initial Model Stack

The initial architecture can use:

```text
Claim Understanding
→ lightweight transformer / LLM

Embeddings
→ sentence-transformer class model

Reranking
→ cross-encoder

NLI
→ DeBERTa-class NLI model

NER
→ spaCy / transformer NER

Entity Linking
→ hybrid deterministic + model-based

Query Generation
→ deterministic templates + optional LLM

Reasoning
→ external LLM initially

Aggregation
→ deterministic baseline
```

Exact models should be benchmarked before final selection.

---

# 8. Model Registry

All models should be accessed through a registry.

Conceptually:

```text
ModelRegistry
├── embedding_model
├── reranker
├── nli_model
├── ner_model
├── entity_linker
├── claim_classifier
└── reasoning_model
```

The registry should manage:

- loading;
- unloading;
- versioning;
- device placement;
- batching;
- health;
- metrics.

---

# 9. Model Lifecycle

Models should transition through:

```text
REGISTERED
    ↓
DOWNLOADING
    ↓
LOADED
    ↓
WARM
    ↓
SERVING
    ↓
UNLOADING
    ↓
FAILED
```

Model failures must be isolated from the rest of the system.

---

# 10. Claim Understanding

The claim understanding subsystem converts raw text into structured semantics.

Outputs:

```text
claim_type
domain
entities
temporal_scope
quantities
units
qualifiers
attribution
verifiability
complexity
```

The system should combine:

```text
deterministic NLP
+
specialized models
+
LLM only when necessary
```

---

# 11. Claim Classification

Initial classification dimensions:

```text
FACTUAL
NUMERICAL
TEMPORAL
COMPARATIVE
CAUSAL
ATTRIBUTION
HISTORICAL
PREDICTIVE
OPINION
COMPOUND
```

A multi-label classifier may be more appropriate than a mutually exclusive classifier.

Example:

```text
"India's GDP grew faster than China's in 2025."

Labels:
NUMERICAL
COMPARATIVE
TEMPORAL
```

---

# 12. Claim Complexity Estimation

Complexity should be estimated before allocating expensive resources.

Signals:

```text
Atomic claim count
Entity count
Temporal ambiguity
Numerical content
Causal language
Comparative structure
Domain specificity
Evidence scarcity
```

This can initially be rule-based.

A learned model can be introduced later.

---

# 13. Claim Decomposition

Compound claims require decomposition.

Possible implementation:

```text
Stage 1:
Rule-based sentence segmentation

Stage 2:
Dependency / semantic analysis

Stage 3:
LLM-assisted decomposition

Stage 4:
Schema validation
```

The LLM should produce structured output validated against the domain model.

---

# 14. Decomposition Validation

Generated atomic claims must be checked for:

```text
Coverage
Faithfulness
Non-duplication
Independence
No invented information
```

A decomposition evaluator can compare:

```text
Original claim
vs
reconstructed claim
```

If the atomic claims cannot reconstruct the original proposition, decomposition is suspect.

---

# 15. Embedding Model

Embeddings are primarily used for:

```text
Candidate retrieval
Semantic matching
Deduplication
Claim similarity
Cache matching
```

They should not directly determine the verdict.

---

# 16. Embedding Requirements

Evaluate:

```text
Semantic retrieval recall
Numerical robustness
Entity sensitivity
Negation handling
Multilingual performance
Latency
Memory
```

Generic embedding benchmarks are insufficient.

Tathvyn needs verification-specific evaluation.

---

# 17. Embedding Model Candidates

Potential initial candidates include:

```text
all-MiniLM-L6-v2
BGE-family models
E5-family models
Modern multilingual embedding models
```

The exact choice should depend on benchmark performance and deployment constraints.

A small model may be preferred if its retrieval quality is sufficiently close to larger alternatives.

---

# 18. Embedding Architecture

Conceptually:

```text
Claim
  ↓
Embedding
  ↓
Vector Index
  ↓
Candidate Passages
```

But retrieval should eventually combine:

```text
Dense retrieval
+
Lexical retrieval
```

---

# 19. Reranker

The reranker performs fine-grained comparison:

```text
Query / Atomic Claim
        +
Candidate Passage
        ↓
Relevance Score
```

A cross-encoder is a strong baseline because it jointly processes both inputs.

---

# 20. Reranker Role

The reranker should optimize:

```text
Evidence utility
```

rather than:

```text
semantic similarity alone
```

Potential inputs:

```text
claim
passage
research objective
source metadata
temporal metadata
```

---

# 21. Reranker Candidates

Potential families:

```text
BGE rerankers
Cross-encoder MS MARCO models
Modern multilingual rerankers
Task-specific learned rankers
```

The choice should be benchmark-driven.

---

# 22. NLI Model

NLI is used to estimate:

```text
ENTAILMENT
CONTRADICTION
NEUTRAL
```

between:

```text
Atomic Claim
        +
Evidence Passage
```

A DeBERTa-class NLI model is a reasonable initial baseline.

---

# 23. NLI Limitations

NLI models can fail on:

```text
Numerical reasoning
Temporal reasoning
Entity ambiguity
Long documents
Domain-specific terminology
Causal claims
Negation
Conditional statements
```

Therefore NLI must be treated as one evidence signal.

---

# 24. NLI Cascade

A cost-aware cascade:

```text
Candidate passage
      ↓
Reranker
      ↓
NLI
      ↓
If uncertain
      ↓
LLM adjudication
```

This avoids expensive reasoning for obvious cases.

---

# 25. NLI Calibration

Raw NLI probabilities should not be treated as:

```text
probability the claim is true
```

They represent model confidence in an NLI label.

NLI calibration should be evaluated independently.

---

# 26. Entity Resolution

Entity resolution should combine:

```text
NER
+
candidate generation
+
knowledge base lookup
+
contextual similarity
+
LLM only for ambiguity
```

Example:

```text
"Washington"
```

may refer to:

```text
George Washington
Washington State
Washington, D.C.
```

The system must preserve ambiguity until resolved.

---

# 27. Entity Resolution Architecture

```text
Mention
  ↓
NER
  ↓
Candidate Entities
  ↓
Contextual Matching
  ↓
Knowledge Base
  ↓
Confidence
  ↓
Resolved / Ambiguous
```

Entity resolution errors can corrupt the entire research process.

---

# 28. Temporal Reasoning

Temporal reasoning should not depend solely on an LLM.

Use deterministic operations for:

```text
Date comparison
Date ranges
Relative date resolution
Publication time
Observation time
```

Models may be used for:

```text
"before the election"
"after the merger"
"currently"
"at the time"
```

---

# 29. Numerical Reasoning

Numerical claims should use structured extraction.

Potential pipeline:

```text
Text
 ↓
Number extraction
 ↓
Unit normalization
 ↓
Metric extraction
 ↓
Time extraction
 ↓
Entity/geography extraction
 ↓
Deterministic comparison
```

Use a calculator or numerical engine for arithmetic rather than an LLM.

---

# 30. Source Scoring Model

Source utility can initially use explicit features:

```text
source_type
domain
primary_status
domain_expertise
authority
methodological_transparency
historical_reliability
claim_domain
```

A learned source model can be introduced after sufficient labeled data exists.

---

# 31. Source Score Is Contextual

The model should estimate:

```text
P(source is useful for this claim)
```

rather than:

```text
P(source is always truthful)
```

This distinction should be reflected in training data and feature design.

---

# 32. Provenance Model

Provenance detection can combine:

```text
Citation graph
URL references
Quotation overlap
Text similarity
Publication metadata
Explicit attribution
```

Potential future implementation:

```text
document graph
+
clustering model
```

---

# 33. Provenance Before Aggregation

Provenance should be resolved before evidence aggregation.

Otherwise:

```text
20 derivative articles
```

may incorrectly become:

```text
20 independent confirmations
```

---

# 34. Model Routing

A central controller should route requests by difficulty.

Conceptually:

```text
Simple
 ↓
Deterministic

Moderate
 ↓
Local ML

Complex
 ↓
Local ML + reasoning model

Very difficult
 ↓
Adaptive research + reasoning model
```

This is the core cost optimization mechanism.

---

# 35. Complexity-Based Routing

Potential routing features:

```text
claim_complexity
evidence_conflict
entity_ambiguity
temporal_ambiguity
source_scarcity
claim_domain
high_stakes_flag
```

---

# 36. Confidence-Based Routing

The system can escalate when:

```text
model confidence is low
```

but only after determining the uncertainty source.

Example:

```text
Low NLI confidence
→ use stronger NLI / LLM

Low retrieval confidence
→ search again

Entity ambiguity
→ entity resolver

Source conflict
→ conflict research
```

---

# 37. LLM Escalation

The LLM should be invoked when:

```text
decomposition is ambiguous
complex semantics are present
evidence conflict requires interpretation
causal reasoning is difficult
source context is difficult to normalize
explanation requires synthesis
```

It should not be invoked merely because it is available.

---

# 38. Model Cascade

A potential architecture:

```text
                Input
                  ↓
        Deterministic processing
                  ↓
             Small models
                  ↓
           Medium models
                  ↓
         Expensive reasoning
                  ↓
            Human review
```

Each escalation should be justified by uncertainty and expected value.

---

# 39. Model Batching

High-volume inference should use batching.

Examples:

```text
Embedding:
batch 32–256

NLI:
batch dynamically

Reranking:
batch candidates
```

Batch size should be tuned against:

```text
throughput
memory
latency
```

---

# 40. Dynamic Batching

For production inference:

```text
Requests arrive
     ↓
Micro-batch window
     ↓
Batch inference
     ↓
Distribute results
```

This can substantially improve hardware utilization.

Latency budgets must constrain batch waiting time.

---

# 41. CPU vs GPU

### CPU

Useful for:

```text
small NER
lightweight classifiers
basic embeddings
low-volume workloads
```

### GPU

Useful for:

```text
large embedding batches
reranking
NLI
larger reasoning models
high throughput
```

The production architecture should support both.

---

# 42. Quantization

Potential optimization:

```text
FP32
 ↓
FP16 / BF16
 ↓
INT8
 ↓
INT4
```

Quantization should be evaluated for:

```text
accuracy degradation
latency
memory
throughput
```

Do not assume lower precision is harmless for NLI or reranking.

---

# 43. Model Serving

Potential serving approaches:

```text
In-process inference
ONNX Runtime
Torch compile
vLLM
Triton
Dedicated model server
```

The choice depends on:

```text
model type
traffic
hardware
batching
latency requirements
```

Do not introduce distributed model serving prematurely.

---

# 44. Model Warmup

Models should support:

```text
lazy loading
warmup
preloading
unloading
```

For latency-sensitive production paths:

```text
warm model
→ predictable latency
```

For low traffic:

```text
lazy loading
→ lower memory cost
```

---

# 45. Model Memory Strategy

Multiple models can compete for memory.

Potential strategy:

```text
Always resident:
embedding model

Resident under load:
reranker
NLI

On demand:
large reasoning model
```

This should be managed by the Model Registry.

---

# 46. Inference Isolation

One failing model should not crash the verification service.

Use:

```text
timeouts
circuit breakers
process isolation where appropriate
resource limits
fallback models
```

---

# 47. Model Fallbacks

Examples:

```text
Primary embedding model
        ↓ failure
Fallback embedding model

NLI model
        ↓ unavailable
heuristic / LLM adjudication

Reasoning API
        ↓ unavailable
deterministic query generation
```

Fallback quality should be measured.

---

# 48. API Model Economics

For API-based reasoning:

```text
Input tokens
+
Output tokens
+
Requests
+
Retries
```

must be tracked.

The system should maintain:

```text
cost per verification
cost per successful verdict
cost per evidence item
```

---

# 49. Model Cost Routing

A useful conceptual rule:

\[
Select\ model =
\arg\max_m
\frac{ExpectedQuality_m}{Cost_m}
\]

subject to:

```text
latency constraint
accuracy constraint
availability constraint
```

The actual routing policy should be learned from production telemetry.

---

# 50. Model Registry Metadata

Each registered model should include:

```text
model_id
version
task
provider
license
parameter_count
memory_requirement
hardware_requirement
latency_profile
throughput_profile
accuracy_profile
calibration_profile
```

---

# 51. Model Versioning

Every inference must be attributable to:

```text
model_id
model_version
configuration
device
precision
inference_engine
```

This is necessary for reproducibility.

---

# 52. Model Evaluation

Each model should have:

```text
offline benchmark
stress test
latency benchmark
memory benchmark
calibration test
adversarial test
domain-specific test
```

Generic benchmark scores are insufficient.

---

# 53. Model Selection Benchmark

For each candidate model:

```text
Quality
Latency
Memory
Throughput
Cost
Robustness
```

should be measured.

Example:

| Model | Accuracy | Latency | Memory | Throughput |
|---|---:|---:|---:|---:|
| Small | A | A | A | A |
| Medium | B | B | B | B |
| Large | C | C | C | C |

The decision should be based on the product's operating point.

---

# 54. Pareto Frontier

Model selection should identify the Pareto frontier:

```text
No model is strictly better in:

quality
+
cost
+
latency
+
memory
```

A slightly smaller model may be optimal if quality loss is negligible.

---

# 55. Model Drift

Performance may degrade when:

```text
web vocabulary changes
new domains appear
source distributions change
new misinformation patterns emerge
language usage changes
```

The system should monitor model performance over time.

---

# 56. Model Monitoring

Production monitoring should include:

```text
Input distribution
Prediction distribution
Confidence distribution
Escalation rate
Fallback rate
Latency
Cost
Error rate
User correction rate
```

Offline evaluation should periodically validate actual quality.

---

# 57. Human Feedback

User feedback may provide signals such as:

```text
correct
incorrect
missing evidence
bad source
misleading verdict
```

These signals should not automatically become ground truth.

They require quality control and labeling policy.

---

# 58. Evaluation-Driven Architecture

The architecture should follow:

```text
Hypothesis
 ↓
Implement
 ↓
Benchmark
 ↓
Compare
 ↓
Ablate
 ↓
Deploy
 ↓
Monitor
 ↓
Improve
```

not:

```text
Choose popular model
 ↓
Deploy
 ↓
Assume quality
```

---

# 59. Model Failure Taxonomy

Initial taxonomy:

```text
CLAIM_CLASSIFICATION_ERROR
DECOMPOSITION_ERROR
ENTITY_LINKING_ERROR
TEMPORAL_REASONING_ERROR
RETRIEVAL_EMBEDDING_ERROR
RERANKING_ERROR
NLI_ERROR
NUMERICAL_REASONING_ERROR
SOURCE_SCORING_ERROR
PROVENANCE_ERROR
MODEL_ROUTING_ERROR
CALIBRATION_ERROR
MODEL_TIMEOUT
MODEL_OOM
MODEL_DRIFT
```

---

# 60. Adversarial Evaluation

Models should be tested against:

```text
Negation
Double negation
Sarcasm
Ambiguous entities
Temporal shifts
Numerical perturbations
Unit changes
Contradictory wording
Misleading headlines
Cherry-picked statistics
Quoted misinformation
```

---

# 61. Numerical Adversarial Tests

Given:

```text
Claim:
GDP grew 8.2%.
```

Test:

```text
GDP grew 8.3%.
GDP fell 8.2%.
GDP grew 8.2 percentage points.
GDP grew 8.2% quarterly.
GDP grew 8.2% in 2023.
GDP grew 8.2% in another country.
```

The model architecture should distinguish these cases.

---

# 62. Negation Tests

Example:

```text
Claim:
"Company X did not ban product Y."

Evidence:
"Company X banned product Y."
```

NLI and retrieval systems should correctly identify contradiction.

Negation should be explicitly included in benchmark data.

---

# 63. Temporal Adversarial Tests

Example:

```text
Claim:
"Person X is CEO in 2026."

Evidence:
"Person X was CEO in 2020."
```

Semantic similarity may be extremely high.

The system must still recognize temporal mismatch.

---

# 64. Source Adversarial Tests

Example:

```text
50 websites
```

all copy:

```text
one incorrect original article
```

The system should not interpret this as strong corroboration.

---

# 65. LLM Prompt Injection Defense

Any retrieved document may contain malicious text.

Model architecture must enforce:

```text
Retrieved Content
      ↓
UNTRUSTED DATA
```

The reasoning model must receive explicit structural separation between:

```text
System instructions
Research state
Evidence content
```

Evidence content must never be allowed to override system policy.

---

# 66. Model Security

Protect against:

```text
Prompt injection
Model extraction
Adversarial examples
Malicious documents
Resource exhaustion
Oversized inputs
Tool poisoning
Data exfiltration
```

Model inputs should be bounded and sanitized.

---

# 67. Model Observability

Every inference should expose metrics such as:

```text
model_id
version
input_size
batch_size
latency
device
memory
confidence
fallback
error
```

Do not log sensitive user content unnecessarily.

---

# 68. Model Trace

A verification trace should show:

```text
Claim
 ↓
Claim model
 ↓
Embedding model
 ↓
Reranker
 ↓
NLI
 ↓
Reasoning model
 ↓
Aggregator
```

with model versions attached to every step.

---

# 69. Initial Model Architecture

A practical first version:

```text
                ┌────────────────────┐
                │ Claim Understanding│
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ Query Generation   │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ Hybrid Retrieval   │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ Cross-Encoder      │
                │ Reranker           │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ NLI / Evidence     │
                │ Assessment         │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ Evidence Graph     │
                └─────────┬──────────┘
                          ↓
                ┌────────────────────┐
                │ Verdict Engine     │
                └────────────────────┘
```

Optional reasoning model:

```text
                ┌────────────────────┐
                │ Reasoning LLM       │
                │                    │
                │ decomposition      │
                │ conflict analysis   │
                │ explanation         │
                └────────────────────┘
```

---

# 70. Initial Model Deployment Strategy

For the first serious prototype:

```text
Local:
- embeddings
- reranker
- NLI
- NER
- numerical processing

API:
- complex reasoning
- difficult decomposition
- optional explanation
```

This balances:

```text
cost
+
quality
+
engineering simplicity
```

---

# 71. Production Evolution

### Stage 1

Single service:

```text
Flask/FastAPI
+
local models
+
external search
+
reasoning API
```

### Stage 2

Separate inference workers:

```text
API
 ↓
Inference queue
 ↓
Model workers
```

### Stage 3

Dedicated services:

```text
Embedding service
Reranker service
NLI service
Research service
```

### Stage 4

Autoscaled inference infrastructure.

Do not jump directly to Stage 4.

---

# 72. Throughput Strategy

At high volume:

```text
Requests
 ↓
Queue
 ↓
Batching
 ↓
Inference workers
 ↓
Results
```

Different workloads may have separate queues:

```text
embedding_queue
rerank_queue
nli_queue
llm_queue
```

---

# 73. Latency Budget

A request latency budget can be decomposed:

```text
Claim understanding
+
Search
+
Document retrieval
+
Extraction
+
Embedding
+
Reranking
+
NLI
+
Research iterations
+
Verdict
+
Explanation
```

The system should measure each component independently.

---

# 74. Cost Budget

Cost should be decomposed:

```text
Search API
+
Network
+
CPU
+
GPU
+
Storage
+
LLM
```

This enables accurate cost-per-verification analysis.

---

# 75. Quality-Cost Routing

The system should eventually support profiles:

```text
FAST
BALANCED
DEEP
```

### FAST

Low research depth, minimal expensive models.

### BALANCED

Moderate research and model escalation.

### DEEP

Maximum evidence investigation within a larger budget.

The same underlying architecture can serve all three.

---

# 76. Model Architecture Invariants

### INV-MA-001

No single model should be treated as the factual authority.

### INV-MA-002

Embedding similarity cannot establish truth.

### INV-MA-003

NLI output cannot directly become final verdict probability.

### INV-MA-004

LLMs operate over evidence rather than replacing evidence.

### INV-MA-005

Model versions must be recorded.

### INV-MA-006

Model selection must be benchmark-driven.

### INV-MA-007

Expensive models should be invoked selectively.

### INV-MA-008

Model failure must not become an epistemic conclusion.

### INV-MA-009

Retrieved content is untrusted model input.

### INV-MA-010

Every model component must have a clearly defined responsibility.

---

# 77. Research Questions

Several architectural questions should remain empirical:

1. How much does NLI improve over reranking alone?
2. Which embedding model gives the best evidence recall per millisecond?
3. Does a cross-encoder materially improve verdict quality?
4. When does LLM adjudication outperform NLI?
5. How much does provenance-aware aggregation improve calibration?
6. How much quality is lost through quantization?
7. What is the optimal model escalation threshold?
8. What is the best quality-cost operating point?
9. How much latency can batching remove?
10. Can a smaller local model replace some API reasoning?

These questions should become experiments rather than assumptions.

---

# 78. Architecture Selection Rule

The final model architecture should be selected using:

```text
Benchmark Evidence
+
Cost Analysis
+
Latency Analysis
+
Reliability Analysis
+
Operational Complexity
```

not based on:

```text
model size
benchmark hype
API popularity
```

---

# 79. Final Model Architecture Principle

> **Use the smallest, cheapest, most reliable model capable of solving each subproblem to the required quality level, and escalate only when the evidence state demands greater reasoning capability.**

This principle is central to building Tathvyn for millions of users.

---

# 80. Next Step

The next document should be:

**`11-system-architecture.md`**

It will connect the domain, retrieval, evidence, research-agent, verdict, and model layers into a production system architecture:

- service boundaries;
- request lifecycle;
- synchronous vs asynchronous execution;
- queues;
- databases;
- caches;
- vector storage;
- object storage;
- model workers;
- observability;
- scaling;
- reliability;
- and the path from a single-machine prototype to a system capable of serving millions of users.
