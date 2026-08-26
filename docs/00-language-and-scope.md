# Tathvyn — Language Scope and Internationalization Policy

## 1. Purpose

This document formally defines the language scope for Tathvyn MVP and establishes the system's behavioral contracts when encountering non-English input or multi-lingual web evidence.

---

## 2. MVP Language Scope: English-First

For Phase 0 through Phase 4 (MVP / V1):
- **Supported Input Language**: **English (en)**
- **Supported Evidence Retrieval Language**: **English (en)**
- **Output Language (Summaries, Verdicts, Citations)**: **English (en)**

### Rationale:
1. Local specialized ML components (`deberta-v3-large-mnli`, `bge-small-en-v1.5`, `en_core_web_trf`) are optimized and calibrated specifically on English NLP corpora.
2. Cross-lingual evidence retrieval introduces compounding uncertainties in translation nuance, stance classification, and entity normalization.
3. Establishing high scientific verification quality and confidence calibration on English claims is a prerequisite before expanding linguistic scope.

---

## 3. Input Language Detection & Handling Contract

When a claim is submitted via the API (`POST /api/v1/check`):

### 3.1 Language Detection
During the **Claim Intelligence** phase, the input text is processed by a fast, deterministic language detector (e.g., `py3langid` or `fasttext` language identification).

### 3.2 Behavior Matrix

| Detected Language | Confidence | System Behavior | HTTP Response Code |
|---|---|---|---|
| English (`en`) | $\ge 0.85$ | Proceed through normal verification pipeline | `200 OK` (Sync) / `202 Accepted` (Async) |
| Non-English (e.g. `es`, `fr`, `hi`, `zh`) | $\ge 0.85$ | Reject request with structured error explaining language limitation | `422 Unprocessable Entity` |
| Ambiguous / Low Confidence | $< 0.85$ | Attempt English processing with `language_warning` in response metadata | `200 OK` / `202 Accepted` |

### 3.3 Error Response Schema (Non-English Input)

```json
{
  "error_code": "UNSUPPORTED_LANGUAGE",
  "message": "Tathvyn MVP currently supports English claims only. Detected language: 'es' (Spanish) with confidence 0.96.",
  "detected_language": "es",
  "supported_languages": ["en"],
  "request_id": "req_non_en_123"
}
```

---

## 4. Multi-Lingual Web Evidence in English Verification

In rare scenarios, an English claim may retrieve foreign-language primary sources (e.g., a foreign government official decree or municipal announcement).

### MVP Contract:
1. Retrieval queries default to `lang:en` filtering in search provider parameters.
2. If non-English documents pass retrieval filters:
   - Text parsing flags the document language.
   - If translated text cannot be extracted with high confidence, the document is rejected with reason `UNSUPPORTED_LANGUAGE_EVIDENCE` rather than feeding uncalibrated text into the NLI model.

---

## 5. Roadmap to Multi-Lingual Verification (V2 / V3)

Future multilingual support will proceed in structured stages:

1. **Stage 1 (V2 - Cross-Lingual Retrieval)**:
   - User inputs English claim; system translates queries to retrieve primary sources in native languages (e.g., Spanish government notices), translates passages via neural MT, and runs English NLI.
2. **Stage 2 (V3 - Native Multilingual NLI & Embeddings)**:
   - Migrate local models to multilingual alternatives: `xlm-roberta-large-xnli`, `bge-m3`, and `spacy-xx-ent-wiki-sm`.
   - Benchmark against multilingual fact-checking datasets (e.g., X-Fact).
