"""Multi-Label Semantic Classifier for Claims.

Categorizes claims across semantic types (Factual, Numerical, Temporal,
Comparative, Causal, Attribution, Opinion, Normative, Compound),
domains, complexity, and epistemic verifiability.
"""

import re
from typing import NamedTuple

from tathvyn.common.enums import ClaimComplexity, ClaimType, ClaimVerifiability


class ClassificationResult(NamedTuple):
    """Result of multi-label semantic claim classification."""

    primary_type: ClaimType
    secondary_types: list[ClaimType]
    domain: str
    complexity: ClaimComplexity
    verifiability: ClaimVerifiability
    verifiability_reasoning: str


# Pattern dictionaries for multi-label detection
_NUMERICAL_PATTERN = re.compile(
    r"\b(?:\$|€|£|₹)?\d+(?:[.,]\d+)?\s*(?:%|percent|billion|million|trillion|meters|miles|kg|scrolls|basis\s+points|years)?\b",
    re.IGNORECASE,
)
_TEMPORAL_PATTERN = re.compile(
    r"\b(?:in\s+\d{4}|during\s+\d{4}|between\s+\d{4}|since\s+\d{4}|as\s+of\s+\d{4}|currently|recently|in\s+the\s+\d{2,4}s)\b",
    re.IGNORECASE,
)
_COMPARATIVE_PATTERN = re.compile(
    r"\b(?:more\s+than|less\s+than|higher\s+than|lower\s+than|faster\s+than|compared\s+to|surpassed|exceeded)\b",
    re.IGNORECASE,
)
_CAUSAL_PATTERN = re.compile(
    r"\b(?:caused\s+by|led\s+to|resulted\s+in|due\s+to|because\s+of|attributed\s+to|consequence\s+of)\b",
    re.IGNORECASE,
)
_ATTRIBUTION_PATTERN = re.compile(
    r"""(?:\b(?:said|stated|declared|claimed|tweeted|announced|wrote|delivered\s+his)\b|['"].+?['"])""",
    re.IGNORECASE,
)
_OPINION_PATTERN = re.compile(
    r"\b(?:tastes?\s+(?:\w+\s+)?better|culturally\s+inferior|better\s+than|worse\s+than|delicious|best|worst|greatest|finest|favorite|favourite|beautiful|ugly|overrated|underrated|awful|wonderful|terrible|horrible|disgusting|masterpiece|inferior\s+to|superior\s+to|fundamentally\s+reducible\s+to)\b",
    re.IGNORECASE,
)
_NORMATIVE_PATTERN = re.compile(
    r"\b(?:should\s+immediately|should\s+be|must\s+never|ought\s+to|morally\s+impermissible|morally|unethical|obligated\s+to)\b",
    re.IGNORECASE,
)

# Domain keyword dictionaries
_DOMAIN_KEYWORDS: dict[str, set[str]] = {
    "ECONOMICS": {
        "gdp",
        "inflation",
        "unemployment",
        "interest",
        "central bank",
        "fed",
        "rbi",
        "tax",
        "revenue",
        "fiscal",
        "trade deficit",
        "recession",
    },
    "FINANCE": {
        "stock",
        "shares",
        "ipo",
        "acquisition",
        "billion",
        "trillion",
        "valuation",
        "series a",
    },
    "MEDICINE": {
        "vaccine",
        "pathogen",
        "virus",
        "antibiotics",
        "penicillin",
        "mrna",
        "crispr",
        "brain",
        "medical",
        "disease",
    },
    "PHYSICS": {"speed of light", "vacuum", "gravitational", "quantum", "energy", "atoms", "mass"},
    "ASTRONOMY": {
        "telescope",
        "lagrange",
        "planet",
        "orbit",
        "moon",
        "lunar",
        "pluto",
        "apollo",
        "jwst",
        "nasa",
    },
    "POLITICS": {
        "president",
        "senate",
        "election",
        "parliament",
        "vote",
        "treaty",
        "sovereign",
        "kyoto protocol",
        "european union",
    },
    "TECH": {
        "gpu",
        "ai",
        "openai",
        "microsoft",
        "apple",
        "google",
        "python",
        "software",
        "nvidia",
        "bitcoin",
    },
    "HISTORY": {
        "churchill",
        "einstein",
        "alexandria",
        "ancient",
        "monarch",
        "world war",
        "1969",
        "1928",
        "1940",
    },
}


def classify_claim(text: str) -> ClassificationResult:
    """Classify a claim's semantic type, domain, complexity, and verifiability."""
    cleaned = text.strip()
    detected_types: set[ClaimType] = set()

    # Check attribution first (attribution statements are historical and empirical)
    is_attribution = bool(_ATTRIBUTION_PATTERN.search(cleaned))
    if is_attribution:
        detected_types.add(ClaimType.ATTRIBUTION)

    # Check normative & opinion (if not pure attribution)
    is_normative = bool(_NORMATIVE_PATTERN.search(cleaned))
    is_opinion = bool(_OPINION_PATTERN.search(cleaned))

    if is_normative and not is_attribution:
        detected_types.add(ClaimType.NORMATIVE)
    if is_opinion and not is_attribution:
        detected_types.add(ClaimType.OPINION)

    if _NUMERICAL_PATTERN.search(cleaned):
        detected_types.add(ClaimType.NUMERICAL)
    if _TEMPORAL_PATTERN.search(cleaned):
        detected_types.add(ClaimType.TEMPORAL)
    if _COMPARATIVE_PATTERN.search(cleaned):
        detected_types.add(ClaimType.COMPARATIVE)
    if _CAUSAL_PATTERN.search(cleaned):
        detected_types.add(ClaimType.CAUSAL)

    # Check compound indicators (conjunctions linking clauses)
    if (
        re.search(r"\b(?:and|whereas|while|but\s+also)\b", cleaned, re.IGNORECASE)
        and len(cleaned.split()) > 15
    ):
        detected_types.add(ClaimType.COMPOUND)

    if not detected_types or not (is_normative or is_opinion):
        detected_types.add(ClaimType.FACTUAL)

    # Select Primary Type
    if ClaimType.ATTRIBUTION in detected_types:
        primary_type = ClaimType.ATTRIBUTION
    elif ClaimType.NORMATIVE in detected_types:
        primary_type = ClaimType.NORMATIVE
    elif ClaimType.OPINION in detected_types:
        primary_type = ClaimType.OPINION
    elif ClaimType.NUMERICAL in detected_types:
        primary_type = ClaimType.NUMERICAL
    elif ClaimType.COMPOUND in detected_types:
        primary_type = ClaimType.COMPOUND
    else:
        primary_type = ClaimType.FACTUAL

    secondary_types = [t for t in detected_types if t != primary_type]

    # Detect Domain
    text_lower = cleaned.lower()
    domain = "GENERAL"
    max_domain_hits = 0
    for d_name, keywords in _DOMAIN_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits > max_domain_hits:
            max_domain_hits = hits
            domain = d_name

    # Determine Verifiability
    if primary_type in (ClaimType.OPINION, ClaimType.NORMATIVE):
        verifiability = ClaimVerifiability.UNVERIFIABLE
        reasoning = f"Claim expresses subjective opinion or normative moral judgment ({primary_type.value})."
    else:
        verifiability = ClaimVerifiability.VERIFIABLE
        reasoning = f"Claim makes testable empirical assertions in domain {domain}."

    # Determine Complexity
    word_count = len(cleaned.split())
    if word_count > 25 or len(detected_types) >= 3:
        complexity = ClaimComplexity.COMPLEX
    elif word_count > 12 or len(detected_types) >= 2:
        complexity = ClaimComplexity.MODERATE
    else:
        complexity = ClaimComplexity.SIMPLE

    return ClassificationResult(
        primary_type=primary_type,
        secondary_types=secondary_types,
        domain=domain,
        complexity=complexity,
        verifiability=verifiability,
        verifiability_reasoning=reasoning,
    )
