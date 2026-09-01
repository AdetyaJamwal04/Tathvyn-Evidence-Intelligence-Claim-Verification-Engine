# Tathvyn — API and Product Contracts Specification (v1.0)

## 1. Purpose & API Design Principles

The Tathvyn REST API exposes a stable, versioned HTTP interface for automated fact verification. 

Key API Principles:
1. **Canonical Schema Stability**: Output verdicts and evidence structures adhere strictly to [00-canonical-enums.md](./00-canonical-enums.md).
2. **Epistemic Transparency**: Every response exposes calibrated confidence scores, evidence sufficiency metrics, and traceable citations.
3. **Idempotency & Deduplication**: Long-running or repeated requests utilize `Idempotency-Key` headers to prevent redundant computation.
4. **Structured Error Model**: Errors conform to RFC-7807 problem details, distinguishing infrastructure failures from epistemic uncertainty.

Base URL: `https://api.Tathvyn.io/api/v1`

---

## 2. Endpoints Overview

| Method | Path | Description | Typical Latency |
|---|---|---|---|
| `POST` | `/api/v1/check` | Synchronous verification (`FAST` or `STANDARD` mode) | 800ms – 3,500ms |
| `POST` | `/api/v1/research` | Asynchronous deep verification (`DEEP` mode) | Returns `202 Accepted` |
| `GET` | `/api/v1/research/{request_id}` | Poll status or fetch completed deep research result | < 50ms |
| `GET` | `/api/v1/verifications/{id}/evidence`| Fetch full evidence graph & provenance details | < 100ms |
| `GET` | `/api/v1/health` | Comprehensive system, model, and database health | < 20ms |

---

## 3. Synchronous Verification: `POST /api/v1/check`

### 3.1 Request Payload

```json
{
  "claim": "India's real GDP grew by 8.2% in financial year 2023-24 according to MoSPI.",
  "mode": "STANDARD",
  "client_context": {
    "domain_hint": "ECONOMICS",
    "required_freshness_days": 365
  }
}
```

#### Request Parameters:
- `claim` (string, required): The raw natural language assertion (10 to 1,000 characters).
- `mode` (string, optional, default: `"STANDARD"`): `"FAST"` (latency-optimized) or `"STANDARD"` (balanced quality).
- `client_context` (object, optional): Optional domain or temporal hints.

---

### 3.2 Response Payload (`200 OK`)

```json
{
  "request_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "claim_id": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",
  "normalized_claim": "India's real GDP grew by 8.2% in fiscal year 2023-24 according to MoSPI.",
  "verdict": "LIKELY TRUE",
  "internal_verdict": "SUPPORTED",
  "confidence": 0.94,
  "evidence_sufficiency": 0.91,
  "framing_concerns": false,
  "summary": "Official data released by India's Ministry of Statistics and Programme Implementation (MoSPI) on May 31, 2024 confirms that real GDP growth for the financial year 2023-24 stood at 8.2%, outperforming initial estimates.",
  "atomic_claims": [
    {
      "atomic_claim_id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
      "text": "India's real GDP grew by 8.2% in fiscal year 2023-24.",
      "verdict": "SUPPORTED",
      "materiality": "CRITICAL"
    },
    {
      "atomic_claim_id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
      "text": "The 8.2% growth figure was reported by MoSPI.",
      "verdict": "SUPPORTED",
      "materiality": "MATERIAL"
    }
  ],
  "citations": [
    {
      "citation_id": 1,
      "source_name": "Ministry of Statistics and Programme Implementation (MoSPI)",
      "domain": "mospi.gov.in",
      "url": "https://www.mospi.gov.in/press-release/gdp-estimates-fy24",
      "authority_class": "PRIMARY",
      "publication_date": "2024-05-31T12:00:00Z",
      "supporting_passage": "Real GDP or GDP at Constant Prices in the year 2023-24 is estimated to attain a level of ₹173.82 lakh crore, against the First Revised Estimates of ₹160.71 lakh crore for the year 2022-23. The growth in real GDP during 2023-24 is estimated at 8.2 per cent."
    }
  ],
  "metrics": {
    "latency_ms": 1842,
    "search_queries_dispatched": 2,
    "documents_analyzed": 4,
    "passages_scored": 12,
    "estimated_cost_usd": 0.0034
  },
  "versions": {
    "engine_version": "1.0.0",
    "model_registry_version": "2026.08.1",
    "policy_version": "standard_v1"
  }
}
```

---

## 4. Asynchronous Deep Research: `POST /api/v1/research`

Used for complex, multi-clause, or controversial claims requiring deep multi-round investigation.

### 4.1 Request Payload
```json
{
  "claim": "Sweden joined NATO in March 2024 as its 32nd member state, whereas Finland rejected NATO membership in 2023.",
  "mode": "DEEP",
  "webhook_url": "https://client.example.com/webhooks/Tathvyn"
}
```

### 4.2 Response Payload (`202 Accepted`)
```json
{
  "request_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "status": "QUEUED",
  "estimated_duration_seconds": 12.0,
  "status_url": "https://api.Tathvyn.io/api/v1/research/7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d"
}
```

---

## 5. Polling Deep Research Status: `GET /api/v1/research/{request_id}`

### 5.1 In-Progress Response (`200 OK`)
```json
{
  "request_id": "7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d",
  "status": "RESEARCHING",
  "progress_percentage": 65,
  "current_activity": "Resolving conflict on Finland NATO membership status",
  "elapsed_seconds": 6.4
}
```

### 5.2 Completed Response (`200 OK`)
Returns full payload matching the structure in §3.2 with `verdict: "PARTIALLY TRUE"` (since Sweden joined in 2024, but Finland joined in 2023 rather than rejecting).

---

## 6. Comprehensive Error Response Taxonomy (RFC-7807)

```json
{
  "type": "https://Tathvyn.io/errors/unsupported-language",
  "title": "Unsupported Language",
  "status": 422,
  "detail": "Tathvyn MVP currently supports English claims only. Detected language: 'fr' (French) with confidence 0.98.",
  "error_code": "UNSUPPORTED_LANGUAGE",
  "request_id": "req_error_7721",
  "timestamp": "2026-08-18T20:58:12.441Z"
}
```

### Error Code Mapping Table

| HTTP Status | Error Code | Description | Client Action |
|---|---|---|---|
| `400 Bad Request` | `EMPTY_CLAIM` | Input claim is missing or shorter than 10 characters | Provide valid claim text |
| `400 Bad Request` | `CLAIM_TOO_LONG` | Input claim exceeds 1,000 characters | Truncate or segment text |
| `401 Unauthorized` | `INVALID_API_KEY` | Missing or invalid Bearer authentication key | Supply valid API key |
| `422 Unprocessable`| `UNSUPPORTED_LANGUAGE` | Input claim is not English ($\ge 0.85$ confidence) | Submit English claim |
| `429 Too Many Req` | `RATE_LIMIT_EXCEEDED` | Request rate bucket exhausted | Retry with exponential backoff |
| `408 Request Timeout`| `RESEARCH_TIMEOUT` | Deep research exceeded configured time limit | Retry or check later |
| `500 Internal Error`| `INFRASTRUCTURE_FAILURE`| Database or local ML inference crash | Contact support; retry |
