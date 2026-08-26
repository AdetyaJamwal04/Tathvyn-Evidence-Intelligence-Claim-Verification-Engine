# Tathvyn — Product Vision

## 1. Executive Vision

**Tathvyn is an evidence-grounded claim verification platform designed to determine what the available evidence supports, contradicts, or leaves unresolved.**

The long-term vision is not to build another chatbot that searches the web and produces a confident-sounding answer. Tathvyn is intended to become a **reliable verification and evidence intelligence layer** for applications, researchers, enterprises, journalists, analysts, and AI agents.

> **A claim should not be judged by how plausible it sounds, how many webpages repeat it, or what an LLM believes. It should be judged by the quality, relevance, independence, temporal validity, and consistency of the evidence available for it.**

## 2. Problem

The web contains enormous amounts of information, but information abundance does not imply reliability. A single claim may be surrounded by primary sources, scientific literature, government publications, journalism, outdated information, duplicated reporting, SEO content, social posts, misleading interpretations, contradictions, and fabricated information.

Search can retrieve these documents and LLMs can summarize them, but neither capability alone constitutes reliable verification.

The central product problem is:

> **How can a system autonomously find, evaluate, connect, and reason over evidence before making a claim-level judgment?**

## 3. Product Thesis

Tathvyn is built around five principles:

1. **Retrieval is not verification.**
2. **Evidence quality matters more than source count.**
3. **Verification must be claim-aware.**
4. **Uncertainty is a valid outcome.**
5. **Every conclusion must be traceable to evidence.**

## 4. What Tathvyn Is

Tathvyn is an adaptive, evidence-grounded claim verification system with five major capabilities:

1. **Claim Understanding** — understand what is actually being asserted.
2. **Evidence Discovery** — search for supporting, contradicting, and primary evidence.
3. **Evidence Assessment** — determine how evidence relates to the claim and evaluate its quality.
4. **Evidence Reasoning** — account for source quality, independence, contradictions, temporal validity, and claim coverage.
5. **Uncertainty-Aware Verdict Generation** — communicate what the evidence supports and what remains unresolved.

## 5. What Tathvyn Is Not

Tathvyn is not:

- a universal truth oracle;
- a search engine;
- a generic RAG chatbot;
- an LLM-powered truth detector;
- a popularity counter.

## 6. Core Verification Model

```text
User Claim
    ↓
Claim Understanding
    ↓
Atomic Claims
    ↓
Research Planning
    ↓
Evidence Discovery
    ↓
Evidence Extraction
    ↓
Evidence Assessment
    ↓
Source & Provenance Analysis
    ↓
Evidence Graph
    ↓
Evidence Sufficiency
    ↓
Verdict
    ↓
Calibrated Explanation
```

## 7. Atomic Claim Philosophy

Complex claims may contain several independently verifiable propositions. Tathvyn therefore decomposes compound claims into atomic claims and evaluates them individually before determining the status of the overall claim.

This enables the system to distinguish between fully supported, refuted, partially supported, misleading, and insufficiently evidenced statements.

## 8. Evidence as a First-Class Object

A webpage is not automatically evidence. Tathvyn treats evidence as a specific, traceable piece of information extracted from a source.

Evidence should retain:

- source and document identity;
- passage-level content;
- publication and retrieval time;
- relationship to the claim;
- retrieval and verification scores;
- source quality;
- provenance;
- independence;
- temporal validity.

## 9. Evidence Graph

The Evidence Graph connects claims, atomic claims, evidence, sources, and provenance.

```text
                     CLAIM
                       │
             ┌─────────┴─────────┐
             ↓                   ↓
       Atomic Claim A       Atomic Claim B
             │                   │
        ┌────┴────┐          ┌───┴────┐
        ↓         ↓          ↓        ↓
    Evidence 1 Evidence 2 Evidence 3 Evidence 4
        │         │
        ↓         ↓
    Source A   Source B
        │
        ↓
  Provenance Group
```

## 10. Active Contradiction Search

Verification must not be confirmation-only.

For sufficiently complex claims, Tathvyn should investigate:

- supporting evidence;
- contradicting evidence;
- primary-source evidence.

This reduces retrieval confirmation bias.

## 11. Adaptive Research

Not every claim deserves the same computational budget.

Simple claims with abundant authoritative evidence should be verified cheaply. Ambiguous, contentious, temporal, or poorly evidenced claims should receive deeper investigation.

The research controller should determine when to search again, seek primary sources, investigate contradictions, resolve unresolved atomic claims, invoke expensive reasoning, or stop.

The stopping decision should depend on **evidence sufficiency and expected value of additional research**, not an arbitrary search count.

## 12. Accuracy, Cost, and Scale

Tathvyn optimizes verification quality under realistic product constraints.

The system should use:

- tiered verification;
- model routing;
- batching;
- caching;
- reusable document processing;
- domain-aware retrieval;
- asynchronous deep verification;
- resource-aware research budgets.

Expensive operations should be used only where they provide measurable incremental value.

## 13. Product-Scale Philosophy

Tathvyn should be designed with millions of users as a long-term operating assumption.

Important capabilities include:

- claim and evidence caching;
- document and embedding reuse;
- batched inference;
- asynchronous workers;
- search-provider routing and fallback;
- horizontal scaling;
- rate limiting;
- observability;
- graceful degradation;
- model abstraction;
- cost-per-verification monitoring.

## 14. Accuracy Architecture

System quality should be decomposed into:

- claim understanding;
- retrieval;
- evidence assessment;
- source analysis;
- final verdict;
- confidence calibration;
- robustness.

## 15. Confidence

Model confidence, evidence strength, and probability of correctness are not automatically equivalent.

Tathvyn should eventually calibrate reported confidence empirically using measures such as:

- Expected Calibration Error;
- Brier score;
- reliability diagrams;
- calibration curves.

## 16. Model Philosophy

The architecture should remain model-agnostic.

Use deterministic methods where sufficient, specialized ML where appropriate, and LLM reasoning where it provides measurable incremental value.

Models should be replaceable without redesigning the product.

## 17. Security and Adversarial Considerations

Retrieved web content is **untrusted data, never instructions**.

The system must eventually address:

- prompt injection;
- SEO manipulation;
- poisoned search results;
- fabricated citations;
- source impersonation;
- manipulated metadata;
- duplicate misinformation;
- content laundering.

## 18. Temporal Awareness

Facts change. Tathvyn must distinguish:

- historical truth;
- current truth;
- time-dependent truth;
- future prediction;
- outdated evidence;
- unknown temporal validity.

## 19. Target Users

Initial and long-term users include:

- individuals checking online claims;
- researchers;
- journalists and analysts;
- developers integrating verification through an API;
- enterprises performing information validation;
- AI agents requiring independent factual verification.

## 20. Core Use Cases

### Consumer Verification

A user submits a claim encountered online and receives an evidence-backed assessment.

### Research Verification

A researcher asks Tathvyn to investigate a factual assertion using authoritative and primary sources.

### Developer API

An application sends claims to Tathvyn and receives structured verification results.

### AI-Agent Verification

An autonomous AI agent submits factual assertions to Tathvyn before presenting them to a user.

## 21. Differentiation

Conventional RAG generally follows:

```text
retrieve → generate
```

Tathvyn is intended to follow:

```text
understand
    ↓
decompose
    ↓
search supporting evidence
    ↓
search contradicting evidence
    ↓
seek primary sources
    ↓
assess evidence
    ↓
evaluate provenance and independence
    ↓
check temporal validity
    ↓
construct evidence graph
    ↓
determine evidence sufficiency
    ↓
research further if necessary
    ↓
produce calibrated verdict
```

The differentiation is therefore **evidence reasoning and adaptive verification**, not merely retrieval.

## 22. Long-Term Product Direction

The initial product may verify individual claims.

The longer-term product can become:

- a consumer verification service;
- a browser-level verification layer;
- a developer API;
- an enterprise verification platform;
- a research assistant;
- an infrastructure layer callable by autonomous AI agents.

## 23. Success Criteria

### Scientific quality

- strong benchmark performance;
- high evidence recall;
- accurate evidence attribution;
- calibrated confidence;
- robust contradiction handling.

### Engineering quality

- modular architecture;
- reproducible experiments;
- testable components;
- model abstraction;
- observability;
- fault tolerance;
- scalable infrastructure.

### Product quality

- useful UX;
- understandable explanations;
- transparent citations;
- predictable latency;
- controlled cost;
- graceful degradation.

### Agentic quality

- adaptive research;
- evidence-driven tool selection;
- iterative investigation;
- meaningful stopping decisions;
- explicit uncertainty handling.

## 24. Non-Goals

For the initial product, Tathvyn will not attempt to:

- establish metaphysical or absolute truth;
- verify every subjective opinion;
- predict future events as if they were present facts;
- replace domain experts in high-stakes decisions;
- treat an LLM's internal knowledge as evidence;
- optimize for minimum cost at the expense of verification quality.

## 25. Guiding Principle

> **Do not ask an AI whether something is true. Ask it to investigate what the evidence says.**

Tathvyn's purpose is not to manufacture certainty. Its purpose is to construct the best available evidence picture, reason over it transparently, and communicate both the conclusion and the remaining uncertainty.

---

# Final Vision

**Tathvyn aims to become an evidence intelligence and claim verification layer for the AI-native world.**

The immediate product is a sophisticated claim verification system.

The deeper objective is infrastructure capable of answering:

- What exactly is being claimed?
- What evidence exists?
- Where did that evidence originate?
- How independent and reliable is it?
- Does it actually support or contradict the claim?
- What remains uncertain?
- Is additional research worth its cost?

If Tathvyn can answer those questions reliably, efficiently, transparently, and at scale, it moves beyond a conventional RAG application and becomes a **general-purpose evidence reasoning system** for humans, applications, and autonomous AI agents.
