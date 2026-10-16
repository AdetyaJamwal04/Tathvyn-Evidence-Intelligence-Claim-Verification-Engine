# VeriFact Evaluation Report — Seed Benchmark v1 (50 Claims)

## 1. Executive Summary & Quality Gates

| Metric | Value | Production Target | Status |
| :--- | :--- | :--- | :--- |
| **Macro-F1** | `83.3%` | $\ge 80.0\%$ | ✅ PASS |
| **Overall Accuracy** | `86.0%` | $\ge 85.0\%$ | ✅ PASS |
| **Expected Calibration Error (ECE)** | `0.0599` | $\le 0.0800$ | ✅ PASS |
| **Brier Score** | `0.1457` | $\le 0.1500$ | ✅ PASS |
| **Total Claims Evaluated** | `50` | `50` | ✅ COMPLETE |

---

## 2. Per-Verdict Epistemic Class Performance

| Canonical Verdict Class | Precision | Recall | F1-Score | Support |
| :--- | :--- | :--- | :--- | :--- |
| `SUPPORTED` | 66.7% | 100.0% | **80.0%** | 14 |
| `REFUTED` | 100.0% | 100.0% | **100.0%** | 17 |
| `PARTIALLY_SUPPORTED` | 100.0% | 22.2% | **36.4%** | 9 |
| `INSUFFICIENT_EVIDENCE` | 100.0% | 100.0% | **100.0%** | 5 |
| `UNVERIFIABLE` | 100.0% | 100.0% | **100.0%** | 5 |

---

## 3. Confusion Matrix

| True \ Predicted | `SUPPORTED` | `REFUTED` | `PARTIALLY_SUPPORTED` | `INSUFFICIENT_EVIDENCE` | `UNVERIFIABLE` |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `SUPPORTED` | 14 | 0 | 0 | 0 | 0 |
| `REFUTED` | 0 | 17 | 0 | 0 | 0 |
| `PARTIALLY_SUPPORTED` | 7 | 0 | 2 | 0 | 0 |
| `INSUFFICIENT_EVIDENCE` | 0 | 0 | 0 | 5 | 0 |
| `UNVERIFIABLE` | 0 | 0 | 0 | 0 | 5 |

---

## 4. Performance by Claim Category

| Category | Total | Correct | Accuracy | Avg Confidence |
| :--- | :--- | :--- | :--- | :--- |
| **AEROSPACE** | 1 | 1 | 100.0% | 81.9% |
| **AESTHETICS** | 1 | 1 | 100.0% | 100.0% |
| **ANCIENT_HISTORY** | 1 | 1 | 100.0% | 45.0% |
| **ASTRONOMY** | 1 | 1 | 100.0% | 81.9% |
| **ASTROPHYSICS** | 1 | 1 | 100.0% | 81.9% |
| **BIOTECHNOLOGY** | 1 | 1 | 100.0% | 81.9% |
| **BUSINESS** | 5 | 3 | 60.0% | 74.5% |
| **CLIMATE** | 1 | 1 | 100.0% | 81.9% |
| **COMPUTING** | 1 | 1 | 100.0% | 81.9% |
| **CRYPTOGRAPHY** | 1 | 1 | 100.0% | 45.0% |
| **DEMOGRAPHICS** | 1 | 1 | 100.0% | 81.9% |
| **ECONOMICS** | 2 | 1 | 50.0% | 81.9% |
| **ETHICS** | 1 | 1 | 100.0% | 100.0% |
| **EVENTS** | 1 | 1 | 100.0% | 81.9% |
| **FINANCE** | 3 | 3 | 100.0% | 81.9% |
| **GENETICS** | 1 | 1 | 100.0% | 81.9% |
| **GEOGRAPHY** | 2 | 2 | 100.0% | 81.9% |
| **GEOPOLITICS** | 2 | 1 | 50.0% | 63.5% |
| **HARDWARE** | 1 | 0 | 0.0% | 81.9% |
| **HISTORY** | 7 | 7 | 100.0% | 81.9% |
| **MEDICINE** | 3 | 3 | 100.0% | 81.9% |
| **NEUROSCIENCE** | 1 | 1 | 100.0% | 81.9% |
| **PHILOSOPHY** | 1 | 1 | 100.0% | 100.0% |
| **PHYSICS** | 1 | 1 | 100.0% | 81.9% |
| **POLICY** | 1 | 1 | 100.0% | 100.0% |
| **POLITICS** | 3 | 3 | 100.0% | 81.9% |
| **SUBJECTIVE** | 1 | 1 | 100.0% | 100.0% |
| **TECH** | 3 | 1 | 33.3% | 81.9% |
| **VENTURE_CAPITAL** | 1 | 1 | 100.0% | 45.0% |

---

## 5. Error Analysis & Discrepancies (7 Discrepancies)

| Claim ID | Claim Text | Expected | Predicted | Confidence | Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `VF-BM-022` | Tesla delivered 2.5 million vehicles globally... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-023` | The US national unemployment rate fell to 1.5... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-024` | OpenAI was founded in December 2015 as a for-... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-030` | Twitter operates under the corporate name Twi... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-036` | Google was founded by Larry Page and Sergey B... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-039` | Sweden joined NATO in March 2024 as its 32nd ... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
| `VF-BM-040` | Nvidia designed the H100 GPU architecture, wh... | `PARTIALLY_SUPPORTED` | `SUPPORTED` | 81.9% | SUFFICIENT_EVIDENCE |
