# Architecture Decision Record (ADR) Template

All architectural, algorithmic, infrastructure, or model selection decisions in Tathvyn must be formally recorded using this template. Store completed records under `docs/adr/ADR-XXX-short-title.md`.

---

# ADR-[NUMBER]: [Title of Decision]

- **Status**: [PROPOSED | ACCEPTED | REJECTED | DEPRECATED | SUPERSEDED by ADR-YYY]
- **Date**: YYYY-MM-DD
- **Author(s)**: [Name / Role]
- **Deciders**: [List of reviewers / stakeholders]
- **Impacted Subsystems**: [e.g. Retrieval, NLI, Verdict Engine, Storage]

---

## 1. Context and Problem Statement

[Describe the context, requirements, constraints, and problem motivating this decision. Explain why the current approach is insufficient or why a choice is needed now.]

---

## 2. Decision Drivers

- [Driver 1: e.g. Latency reduction target < 1.5s]
- [Driver 2: e.g. Evidence recall improvement on numerical claims]
- [Driver 3: e.g. API cost constraint < $0.01 per standard check]
- [Driver 4: e.g. Avoidance of multi-service operational overhead]

---

## 3. Considered Options

1. **Option 1**: [Description of Option 1]
2. **Option 2**: [Description of Option 2]
3. **Option 3**: [Description of Option 3]

---

## 4. Decision Outcome

**Chosen Option**: **Option X** because [concise rationale summarizing the primary advantages].

### 4.1 Expected Consequences

#### Positive Consequences
- [Positive consequence 1]
- [Positive consequence 2]

#### Negative Consequences / Trade-offs
- [Negative consequence or trade-off 1]
- [Mitigation strategy for negative consequence 1]

---

## 5. Empirical Benchmark Evidence

| Option | Macro F1 | Recall@5 | p95 Latency | Est. Cost / 1k | Notes |
|---|---|---|---|---|---|
| Option 1 | 0.82 | 0.88 | 1200ms | $4.20 | Baseline |
| Option 2 (Chosen) | 0.89 | 0.94 | 850ms | $1.80 | Statistically significant improvement |
| Option 3 | 0.87 | 0.91 | 2400ms | $8.50 | Exceeds latency/cost budget |

*Benchmark Suite Used*: `tests/benchmarks/benchmark_seed_v1.json` (N=50)

---

## 6. Implementation & Migration Plan

1. [Step 1: Interface definition]
2. [Step 2: Component implementation]
3. [Step 3: Unit and integration tests]
4. [Step 4: Deprecation of legacy component]

---

## 7. "Revisit When" Condition

Re-evaluate this decision when any of the following triggers occur:
- [Condition 1: e.g. Traffic scales beyond 100 requests per second]
- [Condition 2: e.g. A new open-source model outperforms the chosen model on the MTEB benchmark by >5%]
- [Condition 3: e.g. Provider pricing increases by more than 20%]
