# Tathvyn — Adaptive Research Agent

## 1. Purpose

This document defines the research-control layer of Tathvyn.

The research agent is responsible for deciding:

- what to investigate;
- which tools to use;
- which claims require deeper research;
- which evidence gaps remain;
- when to search for contradictions;
- when to seek primary sources;
- when to escalate reasoning;
- when to stop.

The research agent is therefore not the final fact checker.

Its responsibility is to **efficiently construct a sufficiently strong evidence state from external information sources**.

---

# 2. Agent Principle

A conventional pipeline follows:

```text
Claim
 ↓
Search
 ↓
Retrieve
 ↓
LLM
 ↓
Answer
```

Tathvyn should eventually follow:

```text
Claim
 ↓
Understand
 ↓
Plan
 ↓
Research
 ↓
Assess
 ↓
Identify Gaps
 ↓
Research Again
 ↓
Assess Again
 ↓
Determine Sufficiency
 ↓
Stop
 ↓
Verify
```

The defining capability is **adaptive research under a bounded resource budget**.

---

# 3. Agent Responsibilities

The research agent SHALL:

1. understand the verification state;
2. maintain a research plan;
3. select the next research task;
4. select appropriate retrieval tools;
5. evaluate newly discovered evidence;
6. detect unresolved conflicts;
7. identify evidence gaps;
8. decide whether additional research has value;
9. enforce research budgets;
10. terminate research when stopping conditions are satisfied.

The agent SHALL NOT independently declare factual truth without evidence.

---

# 4. Research State

Conceptually:

```text
ResearchState
├── request
├── claim
├── atomic_claims
├── entities
├── temporal_context
├── research_plan
├── completed_tasks
├── pending_tasks
├── evidence
├── provenance
├── conflicts
├── evidence_sufficiency
├── uncertainty
├── budget
├── metrics
└── status
```

The state must remain serializable so research can be paused, resumed, inspected, or executed asynchronously.

---

# 5. Research Lifecycle

```text
INITIALIZE
    ↓
PLAN
    ↓
SELECT TASK
    ↓
EXECUTE TOOL
    ↓
INGEST RESULTS
    ↓
ASSESS EVIDENCE
    ↓
UPDATE STATE
    ↓
CHECK GAPS
    ↓
CHECK CONFLICTS
    ↓
CHECK SUFFICIENCY
    ↓
STOP OR CONTINUE
```

The loop may execute multiple iterations.

---

# 6. Research Plan

The research plan should contain:

```text
research objectives
atomic claims
task priorities
preferred source types
query candidates
budget
stopping policy
escalation policy
```

Example:

```text
Atomic Claim A
├── SUPPORT
├── CONTRADICT
└── PRIMARY_SOURCE

Atomic Claim B
├── SUPPORT
├── PRIMARY_SOURCE
└── TEMPORAL_CHECK
```

---

# 7. Research Tasks

A task represents one actionable research operation.

Examples:

```text
SEARCH_SUPPORT
SEARCH_CONTRADICTION
SEARCH_PRIMARY
SEARCH_ENTITY
SEARCH_TEMPORAL
SEARCH_CONFLICT
FETCH_DOCUMENT
FOLLOW_CITATION
VERIFY_NUMERIC_VALUE
```

Each task should have:

```text
task_id
objective
atomic_claim_id
priority
expected_value
estimated_cost
status
dependencies
```

---

# 8. Task Priority

Task priority should depend on:

```text
Claim Importance
Evidence Gap
Expected Information Gain
Source Quality Potential
Contradiction Potential
Cost
Latency
```

A conceptual priority function:

\[
Priority(t) =
rac{ExpectedInformationGain(t) 	imes Importance(t)}
{EstimatedCost(t)}
\]

This is an optimization concept, not an initial fixed implementation.

---

# 9. Expected Information Gain

A research action is valuable when it is likely to reduce uncertainty.

Examples:

### High value

- finding the original government notification;
- resolving a direct contradiction;
- locating the original scientific paper;
- determining whether two sources are actually discussing different metrics.

### Low value

- finding another blog repeating the same claim;
- retrieving ten sources from the same provenance cluster.

---

# 10. Research Objectives

The agent should maintain explicit objectives:

```text
SUPPORT
CONTRADICT
PRIMARY_SOURCE
CLARIFY_ENTITY
CLARIFY_TIME
RESOLVE_CONFLICT
FILL_CLAIM_GAP
VALIDATE_NUMERIC_VALUE
VALIDATE_DEFINITION
```

Each objective may require a different retrieval strategy.

---

# 11. Initial Research Policy

For substantive factual claims, the default research policy should attempt:

```text
1. Understand claim
2. Identify atomic claims
3. Search supporting evidence
4. Search contradicting evidence
5. Seek primary evidence
6. Assess evidence
7. Determine gaps
8. Escalate if necessary
9. Stop when sufficient
```

The depth should be adaptive.

---

# 12. Tool Abstraction

The research agent should interact with tools through stable interfaces.

Conceptually:

```text
Tool
├── name
├── capability
├── input_schema
├── output_schema
├── cost_model
├── latency_model
└── reliability
```

Potential tools:

```text
web_search
specialized_search
document_fetch
citation_follow
structured_data_lookup
entity_lookup
calculator
database_query
```

---

# 13. Tool Selection

Tool selection should depend on the research objective.

Example:

```text
Numerical claim
    ↓
Structured data lookup
    +
Official source search

Scientific claim
    ↓
Literature search
    +
Primary paper retrieval

Government policy claim
    ↓
Official domain search
    +
Legal/notification source retrieval
```

Generic web search should not be the universal solution.

---

# 14. Model Routing

Different research tasks may use different models.

Example:

```text
Cheap model
→ query generation

Embedding model
→ retrieval

Reranker
→ candidate ranking

NLI model
→ evidence assessment

Reasoning LLM
→ difficult conflict analysis
```

The agent should invoke expensive models only when required.

---

# 15. Agent vs Pipeline

A pipeline has predetermined execution:

```text
A → B → C → D
```

An agent has conditional execution:

```text
A
 ↓
if uncertain → B
if contradiction → C
if primary source missing → D
if sufficient → STOP
```

Tathvyn should use agentic behavior only where conditional decisions provide measurable value.

---

# 16. Research Loop

Conceptual loop:

```python
while not stopping_condition():

    task = select_next_task(state)

    result = execute(task)

    evidence = assess(result)

    state = update(state, evidence)

    gaps = identify_gaps(state)

    conflicts = identify_conflicts(state)

    update_research_plan(state, gaps, conflicts)
```

This is a conceptual model rather than implementation code.

---

# 17. Evidence Gap Detection

The agent should identify:

```text
uncovered atomic claims
weakly supported claims
missing primary sources
unresolved temporal context
ambiguous entities
unresolved contradictions
definition mismatches
numerical inconsistencies
```

Each gap should potentially generate a new task.

---

# 18. Coverage Matrix

The research state should maintain a coverage matrix.

Example:

| Atomic Claim | Support | Contradiction | Primary | Temporal | Status |
|---|---:|---:|---:|---:|---|
| A1 | ✓ | ✓ | ✓ | ✓ | Supported |
| A2 | ✓ | ✗ | ✗ | ✓ | Insufficient |
| A3 | ✓ | ✓ | ✗ | ✓ | Conflicted |

This gives the controller a structured view of research completeness.

---

# 19. Research Completeness

Completeness is not:

```text
10 sources found
```

It is closer to:

```text
Material atomic claims covered
+
support investigated
+
contradiction investigated
+
appropriate primary evidence sought
+
temporal constraints resolved
+
important conflicts investigated
```

---

# 20. Contradiction Hunting

The agent should actively investigate contradictions when:

- the claim is important;
- supporting evidence is strong;
- the evidence source is authoritative;
- the claim is controversial;
- independent sources disagree.

A useful pattern is:

```text
Current conclusion:
SUPPORTED

Agent question:
"What evidence would make this conclusion wrong?"
```

The answer becomes a research objective.

---

# 21. Adversarial Research

The agent should eventually perform an adversarial pass for difficult claims.

Conceptually:

```text
Current Evidence
      ↓
Assume conclusion may be wrong
      ↓
Search for strongest counterevidence
      ↓
Evaluate
      ↓
Update confidence
```

This is stronger than simply searching for pages containing the word "false."

---

# 22. Primary-Source Escalation

If secondary evidence is strong but primary evidence is missing:

```text
Secondary evidence
      ↓
Identify referenced original
      ↓
Search original
      ↓
Retrieve original
      ↓
Compare secondary interpretation
```

If the primary source cannot be found, the uncertainty should remain visible.

---

# 23. Citation Following

A useful research behavior is:

```text
Relevant Article
      ↓
Reference / citation
      ↓
Original source
      ↓
Original evidence
```

Citation following can significantly improve evidence quality.

---

# 24. Conflict Resolution Loop

When contradictory evidence appears:

```text
Conflict detected
      ↓
Compare claim scope
      ↓
Compare entities
      ↓
Compare time
      ↓
Compare definitions
      ↓
Compare methodology
      ↓
Check provenance
      ↓
Search for authoritative resolution
      ↓
Resolved / unresolved
```

The agent should not simply average contradictory scores.

---

# 25. Numerical Conflict Resolution

For numerical claims:

```text
Value disagreement
      ↓
Normalize units
      ↓
Normalize period
      ↓
Normalize population
      ↓
Normalize metric
      ↓
Check revisions
      ↓
Check methodology
      ↓
Resolve or preserve conflict
```

This should use deterministic computation wherever possible.

---

# 26. Research Depth

The agent should support different depths.

```text
DEPTH 0
Basic validation

DEPTH 1
Single-stage retrieval

DEPTH 2
Multi-source evidence assessment

DEPTH 3
Contradiction + primary-source search

DEPTH 4
Adaptive deep research
```

Depth should be selected based on claim difficulty and product requirements.

---

# 27. Claim Complexity

Potential complexity signals:

```text
Number of atomic claims
Entity ambiguity
Temporal ambiguity
Numerical complexity
Causal reasoning
Source scarcity
Evidence disagreement
Domain specificity
Claim specificity
```

A complex claim should receive more research budget than a trivial one.

---

# 28. Research Budget Allocation

Budget can be divided among atomic claims.

Example:

```text
Total budget = 100 units

A1 → 50
A2 → 30
A3 → 20
```

Allocation should reflect:

```text
Materiality
Uncertainty
Difficulty
Expected information gain
```

---

# 29. Budget Consumption

Every operation should consume measurable resources.

Examples:

```text
Search API call
Document fetch
Embedding batch
Reranker inference
NLI inference
LLM tokens
Latency
Storage
```

The controller should know the remaining budget at all times.

---

# 30. Cost-Aware Escalation

The agent should prefer:

```text
cheap operation with high expected value
```

before:

```text
expensive operation with uncertain value
```

Example:

```text
Check cached document
    ↓
Search official source
    ↓
Run NLI
    ↓
Use expensive LLM reasoning
```

rather than immediately invoking an expensive LLM.

---

# 31. Stopping Policy

Research may stop when any of the following is satisfied:

### Strong Support

Strong, relevant, sufficiently independent evidence supports the claim and contradiction search finds no material counterevidence.

### Strong Refutation

Strong evidence directly contradicts the claim.

### Resolved Conflict

The apparent conflict has been explained through time, scope, definition, methodology, or provenance.

### Insufficient Evidence

Research budget is exhausted or further research has low expected value.

### Unverifiable

The proposition cannot reasonably be verified.

---

# 32. Stopping Must Not Be Source-Count Based

Avoid:

```text
Stop after 5 sources.
```

Instead:

```text
Stop when evidence sufficiency is achieved.
```

Source count is only one possible signal.

---

# 33. Expected Value of Additional Research

Conceptually:

\[
EVSI =
P(	ext{decision changes})
	imes
Value(	ext{decision improvement})
-
Cost(	ext{research})
\]

If:

```text
EVSI < threshold
```

the agent may stop.

The actual model should be validated experimentally.

---

# 34. Confidence-Driven Research

Low confidence can trigger deeper research.

However:

> **Low confidence alone does not tell the agent what to search for.**

The agent should identify the uncertainty source first.

Example:

```text
Low confidence
    ↓
Why?
    ↓
Missing primary source
    ↓
PRIMARY_SOURCE task
```

or:

```text
Low confidence
    ↓
Why?
    ↓
Source conflict
    ↓
RESOLVE_CONFLICT task
```

---

# 35. Research Policy

The research policy determines:

```text
Allowed tools
Maximum depth
Budget
Escalation rules
Stopping rules
Source preferences
Freshness requirements
High-stakes restrictions
```

Policy should be versioned.

---

# 36. Policy Versioning

Every research result should record:

```text
research_policy_version
tool_registry_version
model_versions
aggregation_policy_version
```

This enables reproducibility.

---

# 37. Failure Recovery

The agent should recover from:

```text
Search provider failure
Document fetch failure
Model timeout
Parser failure
Rate limit
Malformed response
Partial evidence
Tool unavailable
```

Recovery strategies:

```text
retry
fallback provider
alternative query
alternative source
skip task
reduce depth
continue with partial evidence
```

---

# 38. Failure Must Not Become Evidence

This is a critical invariant.

```text
Search failed
```

does not mean:

```text
No supporting evidence exists.
```

Likewise:

```text
Primary source unavailable
```

does not mean:

```text
Claim is false.
```

Operational failures and epistemic states must remain separate.

---

# 39. Research State Machine

Conceptually:

```text
INITIALIZED
    ↓
PLANNING
    ↓
RESEARCHING
    ↓
ASSESSING
    ↓
UPDATING
    ↓
 ┌──┴──────────────┐
 ↓                 ↓
CONTINUE          STOP
 ↓
RESEARCHING
```

Stop reasons should be explicit.

---

# 40. Stop Reasons

Initial stop reasons:

```text
SUFFICIENT_EVIDENCE
STRONG_CONTRADICTION
RESOLVED_CONFLICT
UNVERIFIABLE
BUDGET_EXHAUSTED
LOW_EXPECTED_VALUE
TIMEOUT
SYSTEM_LIMIT
```

A verdict should retain the stop reason internally.

---

# 41. Research Trace

A complete trace should look like:

```text
Request
  ↓
Claim
  ↓
Atomic Claim
  ↓
Research Plan
  ↓
Task T1
  ↓
Query Q1
  ↓
Provider P1
  ↓
Documents
  ↓
Evidence
  ↓
Assessment
  ↓
Gap Detected
  ↓
Task T2
  ↓
Primary Source
  ↓
Conflict Detected
  ↓
Task T3
  ↓
Conflict Resolved
  ↓
Evidence Sufficiency
  ↓
STOP
```

This trace is essential for debugging and scientific evaluation.

---

# 42. Agent Memory

The research agent should maintain task-local state.

Long-term global memory should be introduced cautiously.

Potential reusable knowledge:

```text
Document metadata
Source provenance
Previously verified claims
Known source relationships
Entity mappings
```

However, stale factual memory must not bypass fresh evidence requirements.

---

# 43. Claim Cache vs Truth Memory

A cached result should represent:

```text
"Previous verification found these sources and reached this conclusion."
```

not:

```text
"This claim is permanently true."
```

A new request may require re-verification if:

- the claim is time-sensitive;
- evidence may have changed;
- source revisions are possible;
- the user requests fresh verification.

---

# 44. Multi-Agent Consideration

The initial implementation does not require many agents.

Possible future specialized roles:

```text
Research Planner
Search Specialist
Evidence Analyst
Source Analyst
Conflict Resolver
Verifier
```

But these should only be separated when independent specialization provides measurable benefits.

---

# 45. Single-Agent Baseline

Before implementing multi-agent orchestration, establish:

```text
One controller
+
specialized tools
+
deterministic services
+
specialized models
```

This provides a clean baseline.

Multi-agent complexity should be justified by:

- quality improvement;
- parallelism;
- reliability;
- specialization;
- maintainability.

---

# 46. Parallel Research

Independent research tasks can execute concurrently.

Example:

```text
Atomic Claim A
├── Support Search ──────┐
├── Contradiction Search ├── parallel
└── Primary Search ──────┘
```

Parallelism can reduce latency but must respect:

- provider rate limits;
- budget;
- concurrency;
- cost.

---

# 47. Sequential Research

Some tasks depend on previous results.

Example:

```text
Find article
    ↓
Extract cited source
    ↓
Search cited source
    ↓
Compare original
```

The controller must therefore support task dependencies.

---

# 48. Research Graph

Research can be represented as a graph:

```text
Claim
  ↓
Research Objective
  ↓
Research Task
  ↓
Tool Call
  ↓
Evidence
  ↓
New Gap
  ↓
New Research Task
```

This makes the investigation process explicit.

---

# 49. Agent Observability

The agent should record:

```text
Why was this task selected?
Why was this tool selected?
What evidence was found?
What changed in the state?
Why did research continue?
Why did research stop?
What budget remained?
```

These questions are more important than simply logging tool calls.

---

# 50. Research Metrics

Agent-level metrics should include:

### Research efficiency

```text
Evidence gained / cost
Evidence gained / latency
```

### Research effectiveness

```text
Final evidence recall
Contradiction recall
Primary-source recall
```

### Decision quality

```text
Verdict accuracy
Calibration
```

### Control quality

```text
Unnecessary research rate
Premature stopping rate
Budget violation rate
```

---

# 51. Research Ablations

The adaptive agent should be compared against simpler policies.

### A

Fixed number of searches.

### B

Fixed number of documents.

### C

Fixed-depth pipeline.

### D

Evidence-sufficiency stopping.

### E

Evidence-sufficiency + expected-value research.

The objective is to establish whether agentic control actually improves the quality-cost frontier.

---

# 52. Agent Failure Taxonomy

Initial failures:

```text
BAD_PLAN
WRONG_TASK_PRIORITY
PREMATURE_STOP
OVER_RESEARCH
TOOL_MISSELECTION
QUERY_REPETITION
CONFIRMATION_BIAS
MISSED_CONTRADICTION
MISSED_PRIMARY_SOURCE
BUDGET_WASTE
FAILURE_RECOVERY_ERROR
STATE_CORRUPTION
```

These should be tracked independently from model-level errors.

---

# 53. Confirmation Bias Defense

The agent must actively prevent:

```text
First plausible evidence
        ↓
More searches supporting same conclusion
        ↓
False confidence
```

Defenses include:

- explicit contradiction objectives;
- source diversity;
- provenance clustering;
- adversarial research;
- stopping constraints;
- evidence coverage requirements.

---

# 54. Agent Safety Boundary

The agent may:

```text
Search
Fetch
Parse
Compare
Analyze
Plan
Reason
```

The agent must not treat retrieved content as executable instructions.

Tool outputs are data.

---

# 55. High-Stakes Escalation

For high-stakes domains, the research agent may require:

```text
Higher evidence threshold
+
Primary-source preference
+
Additional contradiction search
+
Stricter confidence ceiling
+
Human review
```

The policy should be domain-configurable.

---

# 56. Research API Contract

Conceptually:

```python
research(
    claim,
    context,
    policy,
    budget
) -> ResearchResult
```

Where:

```text
ResearchResult
├── atomic_claims
├── evidence
├── provenance
├── conflicts
├── coverage
├── sufficiency
├── uncertainty
├── trace
├── metrics
├── stop_reason
└── budget_consumption
```

The research layer should not itself be responsible for user-facing prose.

---

# 57. Research Agent Invariants

### INV-A-001

The agent must maintain explicit research state.

### INV-A-002

Every research task must have an objective.

### INV-A-003

Every task must consume measurable resources.

### INV-A-004

Research failures must remain distinct from epistemic conclusions.

### INV-A-005

Contradiction search must be available as a first-class objective.

### INV-A-006

Primary-source discovery must be available as a first-class objective.

### INV-A-007

Research should stop based on evidence sufficiency or resource constraints, not arbitrary source count.

### INV-A-008

Agent decisions must be observable.

### INV-A-009

Retrieved content is untrusted data.

### INV-A-010

Multi-agent complexity must be justified experimentally.

---

# 58. Conceptual Controller

```text
initialize_state()

while state.status == RESEARCHING:

    update_coverage(state)

    if evidence_sufficient(state):
        stop(SUFFICIENT_EVIDENCE)

    if claim_unverifiable(state):
        stop(UNVERIFIABLE)

    task = select_high_value_task(
        gaps,
        conflicts,
        budget,
        policy
    )

    if task is None:
        stop(LOW_EXPECTED_VALUE)

    result = execute_task(task)

    if result.failed:
        recover_or_record_failure(result)
        continue

    evidence = process_result(result)

    update_state(evidence)

    if budget_exhausted():
        stop(BUDGET_EXHAUSTED)
```

This controller should remain deterministic where possible.

---

# 59. Agentic Intelligence

The key intelligence of the research agent is not:

> "Can it call many tools?"

It is:

> **Can it identify the most valuable next piece of information to acquire?**

This distinction is central to the design.

---

# 60. Research Agent as Decision System

The research agent can eventually be modeled as a sequential decision process.

At state \(S_t\):

\[
a_t = \pi(S_t)
\]

where:

- \(S_t\) = current evidence/research state;
- \(a_t\) = next research action;
- \(\pi\) = research policy.

The action should maximize expected verification utility under resource constraints.

Conceptually:

\[
a^* =
rg\max_a
rac{ExpectedInformationGain(a)}
{Cost(a)}
\]

subject to:

\[
Budget(a) \leq RemainingBudget
\]

This provides a principled foundation for future learned research policies.

---

# 61. Product-Scale Implication

At millions of requests, agentic research must not mean unlimited tool calls.

Instead:

```text
Adaptive Intelligence
+
Strict Budgets
+
Caching
+
Parallelism
+
Model Routing
+
Provider Routing
+
Evidence Reuse
```

The agent should become more selective as scale increases, not simply more expensive.

---

# 62. Research Agent Roadmap

### Phase 1

Deterministic controller:

```text
fixed objectives
+
fixed escalation rules
+
fixed budgets
```

### Phase 2

Evidence-aware controller:

```text
coverage
+
conflict
+
sufficiency
```

### Phase 3

Cost-aware controller:

```text
expected information gain
+
cost
+
latency
```

### Phase 4

Learned controller:

```text
historical traces
+
outcome data
+
research policy optimization
```

The learned policy should only replace deterministic logic where it demonstrates measurable improvement.

---

# 63. Final Principle

> **The research agent should spend computation where it can most reduce uncertainty, not where it can most easily produce more text.**

A successful Tathvyn agent therefore behaves less like a chatbot and more like a bounded research investigator:

```text
Observe
  ↓
Hypothesize
  ↓
Investigate
  ↓
Evaluate
  ↓
Challenge
  ↓
Update
  ↓
Stop when justified
```

---

# 64. Next Step

The next document should be:

**`09-verdict-engine.md`**

It will define the final decision layer:

- atomic verdict computation;
- evidence aggregation;
- support vs contradiction;
- materiality;
- misleading claims;
- uncertainty;
- confidence calibration;
- verdict thresholds;
- hard constraints;
- conflict handling;
- and the interface between the research state and final verification result.
