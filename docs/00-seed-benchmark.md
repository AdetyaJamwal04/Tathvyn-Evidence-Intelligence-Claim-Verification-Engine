# Tathvyn — Seed Benchmark Suite (v1.0)

## 1. Purpose

Tathvyn adheres to a core architectural principle: **no architecture change or complex reasoning subsystem shall be added without measurable empirical evaluation**.

To enable benchmark-driven development starting in Phase 0 and Phase 1, this document provides:
1. The **Benchmark Schema Specification**.
2. An initial **50-Claim Seed Benchmark Suite** spanning diverse domains, claim types, difficulty levels, and expected verdict outcomes.
3. The **Evaluation Runner Contract**.

---

## 2. Benchmark Case Schema

Each benchmark item is structured as a JSON object adhering to this schema:

```json
{
  "benchmark_id": "VF-BM-001",
  "claim": "India's real GDP grew by 8.2% in financial year 2023-24.",
  "expected_verdict": "SUPPORTED",
  "expected_public_label": "LIKELY TRUE",
  "claim_type": ["FACTUAL", "NUMERICAL", "TEMPORAL", "FINANCIAL"],
  "domain": "ECONOMICS",
  "difficulty": "EASY",
  "expected_atomic_claims": [
    "India experienced real GDP growth in fiscal year 2023-24.",
    "The real GDP growth rate for India in FY 2023-24 was 8.2%."
  ],
  "expected_primary_sources": [
    "Ministry of Statistics and Programme Implementation (MoSPI)",
    "Reserve Bank of India (RBI)"
  ],
  "notes": "Official release published May 31, 2024 confirming 8.2% FY24 growth."
}
```

---

## 3. Seed Dataset (50 Curated Benchmark Claims)

### Category A: Pure Factual & Scientific (Supported)
1. **VF-BM-001** | `SUPPORTED` | *The James Webb Space Telescope operates around the Sun-Earth Lagrange Point 2 (L2).* (ASTROPHYSICS, EASY)
2. **VF-BM-002** | `SUPPORTED` | *Penicillin was discovered by Alexander Fleming at St. Mary's Hospital in London in 1928.* (HISTORY/MEDICINE, EASY)
3. **VF-BM-003** | `SUPPORTED` | *CRISPR-Cas9 was adapted for genome editing in eukaryotic cells by teams including Feng Zhang and Jennifer Doudna.* (BIOTECHNOLOGY, MODERATE)
4. **VF-BM-004** | `SUPPORTED` | *The speed of light in a vacuum is exactly 299,792,458 meters per second by international definition.* (PHYSICS, EASY)
5. **VF-BM-005** | `SUPPORTED` | *mRNA vaccines against COVID-19 encode the viral spike protein rather than delivering live attenuated virus.* (MEDICINE, EASY)

### Category B: Numerical & Financial (Supported)
6. **VF-BM-006** | `SUPPORTED` | *India's real GDP grew by 8.2% in financial year 2023-24 according to MoSPI.* (ECONOMICS, EASY)
7. **VF-BM-007** | `SUPPORTED` | *Microsoft completed its acquisition of Activision Blizzard for approximately $68.7 billion in October 2023.* (FINANCE/TECH, EASY)
8. **VF-BM-008** | `SUPPORTED` | *The European Central Bank reduced its key deposit facility rate by 25 basis points in June 2024.* (FINANCE, MODERATE)
9. **VF-BM-009** | `SUPPORTED` | *Apple reached a market capitalization of $3 trillion for the first time in January 2022 during intraday trading.* (FINANCE, MODERATE)
10. **VF-BM-010** | `SUPPORTED` | *The global human population officially surpassed 8.0 billion people in November 2022 according to the United Nations.* (DEMOGRAPHICS, EASY)

### Category C: Direct Refutations / False Factual Claims (Refuted)
11. **VF-BM-011** | `REFUTED` | *The Great Wall of China is the only human-made structure visible to the unaided naked eye from low Earth orbit.* (AEROSPACE/GEOGRAPHY, EASY)
12. **VF-BM-012** | `REFUTED` | *Humans use only 10% of their brain capacity at any given time.* (NEUROSCIENCE, EASY)
13. **VF-BM-013** | `REFUTED` | *Albert Einstein failed his high school mathematics courses.* (HISTORY, EASY)
14. **VF-BM-014** | `REFUTED` | *The Eiffel Tower was permanently painted gold in honor of the 2024 Paris Olympics.* (EVENTS, EASY)
15. **VF-BM-015** | `REFUTED` | *Amazon CEO Jeff Bezos stepped down and was succeeded as CEO by Satya Nadella in 2021.* (BUSINESS, EASY)
16. **VF-BM-016** | `REFUTED` | *The United States Federal Reserve raised interest rates to 15% in 2023.* (FINANCE, EASY)
17. **VF-BM-017** | `REFUTED` | *Antibiotics are effective in directly killing viral pathogens like influenza and rhinovirus.* (MEDICINE, EASY)
18. **VF-BM-018** | `REFUTED` | *Mount Everest is located entirely within the sovereign territory of India.* (GEOGRAPHY, EASY)
19. **VF-BM-019** | `REFUTED` | *The Kyoto Protocol was ratified by unanimous vote of the United States Senate in 1998.* (POLITICS, MODERATE)
20. **VF-BM-020** | `REFUTED` | *Python programming language was created by Dennis Ritchie at Bell Labs in 1972.* (COMPUTING, EASY)

### Category D: Numerical Mismatch & Distorted Statistics (Refuted / Partially Supported)
21. **VF-BM-021** | `REFUTED` | *Global carbon dioxide emissions dropped by over 50% year-over-year in 2020 due to pandemic lockdowns.* (CLIMATE, MODERATE)
22. **VF-BM-022** | `PARTIALLY_SUPPORTED` | *Tesla delivered 2.5 million vehicles globally in 2023, setting a new company record.* (BUSINESS, MODERATE - Note: Record was set, but actual deliveries were ~1.81 million)
23. **VF-BM-023** | `PARTIALLY_SUPPORTED` | *The US national unemployment rate fell to 1.5% in 2023, the lowest level in 70 years.* (ECONOMICS, MODERATE - Note: Reached historic low 3.4%, not 1.5%)
24. **VF-BM-024** | `PARTIALLY_SUPPORTED` | *OpenAI was founded in December 2015 as a for-profit public corporation by Sam Altman and Elon Musk.* (TECH/LEGAL, MODERATE - Note: Founded Dec 2015 by Altman/Musk, but as non-profit)
25. **VF-BM-025** | `PARTIALLY_SUPPORTED` | *NASA's Apollo 11 mission landed Neil Armstrong and Buzz Aldrin on the Moon on July 20, 1969, and they stayed on the lunar surface for 3 weeks.* (HISTORY, MODERATE - Note: Landing date correct, surface stay was ~21.5 hours)

### Category E: Temporal Shifts & Outdated Facts (Refuted / Contextual)
26. **VF-BM-026** | `REFUTED` | *The United Kingdom is currently an active member state of the European Union.* (POLITICS, EASY - Post-Brexit status)
27. **VF-BM-027** | `REFUTED` | *Barack Obama is the incumbent sitting President of the United States in 2026.* (POLITICS, EASY)
28. **VF-BM-028** | `SUPPORTED` | *Queen Elizabeth II reigned as monarch of the United Kingdom from February 1952 until her death in September 2022.* (HISTORY, EASY)
29. **VF-BM-029** | `REFUTED` | *Pluto is classified as a major planet by the International Astronomical Union as of 2025.* (ASTRONOMY, EASY)
30. **VF-BM-030** | `PARTIALLY_SUPPORTED` | *Twitter operates under the corporate name Twitter Inc. with its headquarters located in San Francisco.* (BUSINESS, MODERATE - Merged into X Corp, headquarters moved/reorganized)

### Category F: Attributions & Quotes (Supported / Refuted)
31. **VF-BM-031** | `REFUTED` | *Winston Churchill said in 1940: "If you're going through hell, keep going."* (ATTRIBUTION, MODERATE - Apocryphal quote without historical record)
32. **VF-BM-032** | `SUPPORTED` | *Neil Armstrong stated "That's one small step for [a] man, one giant leap for mankind" upon stepping onto the lunar surface in 1969.* (ATTRIBUTION, EASY)
33. **VF-BM-033** | `REFUTED` | *Marie Curie said: "Be less curious about people and more curious about ideas" in her Nobel banquet speech of 1911.* (ATTRIBUTION, MODERATE - Often attributed but unverified in Nobel records)
34. **VF-BM-034** | `SUPPORTED` | *Martin Luther King Jr. delivered his "I Have a Dream" speech at the Lincoln Memorial during the March on Washington in August 1963.* (ATTRIBUTION/HISTORY, EASY)
35. **VF-BM-035** | `REFUTED` | *Bill Gates officially stated in 1981 that "640K of memory ought to be enough for anybody."* (ATTRIBUTION/TECH, MODERATE - Debunked quote)

### Category G: Compound Multi-Clause Claims (Partially Supported / Refuted)
36. **VF-BM-036** | `PARTIALLY_SUPPORTED` | *Google was founded by Larry Page and Sergey Brin in September 1998, and its initial IPO raised $50 billion on the NYSE in 2000.* (TECH/FINANCE, HARD - Founded Sept 1998 on NASDAQ in 2004 raising $1.9B)
37. **VF-BM-037** | `PARTIALLY_SUPPORTED` | *The Panama Canal connects the Atlantic and Pacific oceans, was completed by France in 1914, and is 50 miles long.* (GEOGRAPHY/HISTORY, MODERATE - US completed, not France)
38. **VF-BM-038** | `SUPPORTED` | *The Human Genome Project began in 1990, was declared complete in 2003, and was funded by the US Department of Energy and NIH.* (GENETICS, MODERATE)
39. **VF-BM-039** | `PARTIALLY_SUPPORTED` | *Sweden joined NATO in March 2024 as its 32nd member state, whereas Finland rejected NATO membership in 2023.* (GEOPOLITICS, HARD - Sweden joined March 2024 as 32nd, but Finland joined in April 2023 as 31st)
40. **VF-BM-040** | `PARTIALLY_SUPPORTED` | *Nvidia designed the H100 GPU architecture, which was released in 2022 and is manufactured by Intel in Oregon.* (HARDWARE, MODERATE - Designed by Nvidia in 2022, but manufactured by TSMC in Taiwan)

### Category H: Insufficient Evidence & Epistemic Abstention (Insufficient Evidence)
41. **VF-BM-041** | `INSUFFICIENT_EVIDENCE` | *A covert meeting between private executives from Company X and Company Y took place in Zurich on January 14, 2026 to discuss hostile takeover pricing.* (CORPORATE_ESPIONAGE, HARD - Privately held / non-public assertion)
42. **VF-BM-042** | `INSUFFICIENT_EVIDENCE` | *Secret negotiations between country A and country B resulted in an unwritten pact to restrict lithium exports starting Q4 2026.* (GEOPOLITICS, HARD - Unsubstantiated rumor/leak)
43. **VF-BM-043** | `INSUFFICIENT_EVIDENCE` | *The anonymous founder of Bitcoin, Satoshi Nakamoto, was a single mathematician born in Germany in 1968.* (CRYPTOGRAPHY, HARD - Identity unconfirmed by definitive evidence)
44. **VF-BM-044** | `INSUFFICIENT_EVIDENCE` | *A newly formed startup named QuantumVort closed a $100M Series A round led by Benchmark in secret stealth mode in August 2026.* (VENTURE_CAPITAL, HARD - Non-public entity)
45. **VF-BM-045** | `INSUFFICIENT_EVIDENCE` | *The ancient library of Alexandria contained exactly 732,419 scrolls at the time of its first fire.* (ANCIENT_HISTORY, HARD - Exact historical numerical count inaccessible)

### Category I: Subjective, Normative & Inherently Unverifiable (Unverifiable)
46. **VF-BM-046** | `UNVERIFIABLE` | *Vanilla ice cream tastes significantly better than chocolate ice cream.* (SUBJECTIVE/PREFERENCE, EASY)
47. **VF-BM-047** | `UNVERIFIABLE` | *The government should immediately lower all corporate tax rates to zero.* (NORMATIVE/POLICY, EASY)
48. **VF-BM-048** | `UNVERIFIABLE` | *Modern contemporary art produced after 1990 is culturally inferior to Renaissance oil paintings.* (AESTHETICS/VALUE_JUDGMENT, EASY)
49. **VF-BM-049** | `UNVERIFIABLE` | *Consciousness in biological organisms is fundamentally reducible to quantum gravitational collapse in microtubules.* (METAPHYSICS/PHILOSOPHY, HARD)
50. **VF-BM-050** | `UNVERIFIABLE` | *It is morally impermissible to utilize generative AI models to compose creative poetry.* (ETHICS/NORMATIVE, EASY)

---

## 4. Evaluation Runner Protocol

The automated evaluation runner (`tests/benchmarks/run_benchmark.py`) SHALL:
1. Ingest all 50 items from `benchmark_seed_v1.json`.
2. Execute the verification pipeline under configured mode (`STANDARD` or `FAST`).
3. Compute metrics:
   - **Verdict Accuracy**: Exact match between `expected_verdict` and returned `verdict`.
   - **Abstention Precision & Recall**: Accuracy in correctly classifying `INSUFFICIENT_EVIDENCE` and `UNVERIFIABLE` without false directional certainty.
   - **Macro F1 Score**: Unweighted average of F1 across all 5 canonical internal verdict classes.
   - **Evidence Recall@K**: Proportion of expected primary sources present in the final evidence snapshot.
   - **Mean Latency & Cost Per Check**.
