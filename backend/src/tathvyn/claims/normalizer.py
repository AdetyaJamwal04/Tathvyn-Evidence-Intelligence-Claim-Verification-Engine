"""Linguistic Normalization and Inquiry Framing Removal.

Transforms colloquial, interrogative, or prefixed user inputs into standardized
declarative propositions and generates deterministic SHA256 content hashes.
"""

import hashlib
import re
from typing import NamedTuple


class NormalizedClaimResult(NamedTuple):
    """Result of claim normalization."""

    raw_text: str
    normalized_text: str
    content_hash: str
    was_framed_as_question: bool


# Single consolidated regex for common inquiry prefixes
_INQUIRY_PREFIX_PATTERN = re.compile(
    r"^(?:is\s+it\s+true\s+(?:that)?\s*|can\s+you\s+(?:please\s+)?verify\s+(?:that|if)?\s*|"
    r"please\s+fact[- ]check\s+(?:that|if)?\s*|i\s+heard\s+(?:that)?\s*|"
    r"(?:did|does|has|have|was|were)\s+)",
    re.IGNORECASE,
)


def normalize_claim_text(raw_text: str) -> NormalizedClaimResult:
    """Normalize whitespace, typography, and conversational question framing.

    Args:
        raw_text: The user's input claim.

    Returns:
        NormalizedClaimResult: Contains the normalized assertion text and SHA256 hash.
    """
    cleaned = raw_text.strip()

    # 1. Normalize typography (curly quotes to straight quotes, multiple spaces)
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    cleaned = re.sub(r"\s+", " ", cleaned)

    was_question = cleaned.endswith("?")
    if was_question:
        cleaned = cleaned[:-1].strip()

    # 2. Strip common conversational inquiry framing prefixes
    match = _INQUIRY_PREFIX_PATTERN.match(cleaned)
    stripped_text = cleaned[match.end() :].strip() if match else cleaned

    # Capitalize first letter and ensure clean sentence structure
    normalized_text = stripped_text[0].upper() + stripped_text[1:] if stripped_text else cleaned

    if not normalized_text.endswith("."):
        normalized_text += "."

    # 3. Compute deterministic SHA256 hash
    content_hash = hashlib.sha256(normalized_text.lower().encode("utf-8")).hexdigest()

    return NormalizedClaimResult(
        raw_text=raw_text,
        normalized_text=normalized_text,
        content_hash=content_hash,
        was_framed_as_question=was_question,
    )
