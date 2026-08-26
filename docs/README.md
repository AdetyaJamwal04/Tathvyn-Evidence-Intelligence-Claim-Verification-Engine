# Tathvyn — Architecture and Engineering Documentation

Welcome to the comprehensive architecture and design specification for **Tathvyn**, an evidence-grounded claim verification platform designed for automated, calibrated, and auditable fact verification.

---

## 1. Documentation Index & Map

The documentation is organized into three major tiers: **Foundations & Canonical Standards (00–05)**, **Core Subsystem Specifications (06–17)**, and **Production & Scale Engineering (18–26)**.

```text
Tathvyn_docs/
├── 00-canonical-enums.md                              # Single source of truth for all taxonomies and enums
├── 00-stack-selection.md                              # Concrete Phase 0 / MVP technology choices
├── 00-seed-benchmark.md                               # 50-claim seed benchmark suite & evaluation runner contract
├── 00-adr-template.md                                 # Architecture Decision Record template
├── 00-phase-0-definition-of-done.md                   # Concrete deliverables and gate criteria for Phase 0
├── 00-language-and-scope.md                           # Language scope (English-first) and rejection policy
│
├── 01-product-vision.md                               # Vision, problem space, and core system philosophy
├── 02-problem-definition.md                           # Formal mathematical problem definition & epistemic taxonomy
├── 03-requirements.md                                 # Complete product, functional, and non-functional requirements
├── 04-domain-model.md                                 # Canonical domain entities, objects, and relationships
├── 05-verification-methodology.md                     # Step-by-step verification lifecycle and edge cases
│
├── 06-retrieval-strategy.md                           # Information retrieval strategy, queries, and provider abstraction
├── 07-evidence-model.md                               # Evidence scoring, stances, provenance, and sufficiency
├── 08-research-agent.md                               # Adaptive research controller, task planning, and stopping logic
├── 09-verdict-engine.md                               # Decision layer, aggregation logic, and epistemic boundaries
├── 10-model-architecture.md                           # Local vs API ML architecture, registry, and pipelines
│
├── 11-system-architecture.md                          # High-level service architecture, jobs, and deployment model
├── 12-data-architecture.md                            # Database schemas, storage tiers, and snapshot versioning
├── 13-retrieval-architecture.md                       # Detailed retrieval pipeline, ranking fusion, and indexing
├── 14-evidence-engineering.md                         # Passage extraction, normalization, and stance assessment
├── 15-query-and-claim-intelligence.md                 # Claim detection, decomposition, and query synthesis
├── 16-evaluation-and-benchmarking.md                  # Multi-level evaluation suite, calibration metrics, and gates
├── 17-verdict-engine-and-calibration.md               # Verdict scoring, probability calibration, and abstention
│
├── 18-research-orchestrator.md                        # Control plane state machine, action selection, and tracing
├── 19-system-architecture-and-services.md             # Service boundaries, modular monolith design, and queues
├── 20-security-safety-and-adversarial-resilience.md   # SSRF protection, prompt injection defense, and sandboxing
├── 21-cost-latency-and-scale.md                       # Cost models, latency budgets, batching, and degradation
├── 22-mleops-and-model-lifecycle.md                   # Model registry, shadow deployments, and drift detection
├── 23-data-schema-and-provenance.md                   # Relational & vector schemas, provenance graphs, and snapshots
├── 24-api-and-product-contracts.md                    # REST API specifications, response schemas, and errors
├── 25-deployment-ci-cd-and-production-readiness.md    # Docker, CI/CD pipelines, observability, and checklist
└── 26-project-roadmap-and-implementation-order.md     # Phased roadmap, entry/exit criteria, and implementation plan
```

---

## 2. End-to-End Architectural Progression

Tathvyn enforces a strict, multi-stage pipeline where raw text is converted into structured evidence before reaching a final verdict:

```text
User Claim Input
       ↓
[00-language-and-scope.md] ── Language Detection & Filtering
       ↓
[15-query-and-claim-intelligence.md] ── Claim Classification & Atomic Decomposition
       ↓
[18-research-orchestrator.md] ── Adaptive Planning & Action Selection
       ↓
[06-retrieval-strategy.md / 13-retrieval-architecture.md] ── Multi-Provider Search & Doc Fetch
       ↓
[14-evidence-engineering.md] ── Passage Extraction, Stance Detection & NLI
       ↓
[07-evidence-model.md / 23-data-schema-and-provenance.md] ── Provenance Clustering & Evidence Graph
       ↓
[09-verdict-engine.md / 17-verdict-engine-and-calibration.md] ── Sufficiency Gate & Verdict Decision
       ↓
[24-api-and-product-contracts.md] ── Structured Output, Confidence & Citations
```

---

## 3. Core Epistemic Invariants

Across all documents, Tathvyn maintains these non-negotiable principles:

1. **Evidence Grounding**: The system never issues a directional verdict based solely on internal LLM parameters or knowledge.
2. **Semantic Similarity $\neq$ Evidence**: Finding a topically similar webpage does not constitute proof or refutation.
3. **Absence $\neq$ Refutation**: Failure to retrieve evidence must produce `INSUFFICIENT_EVIDENCE`, never `REFUTED`.
4. **Source Count $\neq$ Independence**: Fifty derivative blog posts republishing one press release count as one evidence unit.
5. **No False Precision**: Raw model logits are not exposed as truth probabilities; confidence must be empirically calibrated.
6. **Untrusted Web Data**: Retrieved web pages are strictly treated as passive data, never executable instructions.
7. **Traceability**: Every verdict is permanently linked to an immutable evidence snapshot and source passage citations.
