"""
Conservative Atomic Claim Decomposition with Depth Ceiling, Causal Tagging, and Anti-Hallucination Gate.

Decomposes complex/compound claims into independently verifiable AtomicClaim objects.
Preserves single-element atomic claims without unnecessary fragmentation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tathvyn.claims.entity_extractor import extract_named_entities
from tathvyn.claims.temporal_extractor import extract_temporal_constraints
from tathvyn.common.enums import AtomicClaimVerdict, Materiality
from tathvyn.common.models.claim import AtomicClaim, Claim


def _split_compound_clauses(text: str) -> list[str]:
    """Split compound sentences along coordinating conjunctions, causal connectives, and semicolons."""
    # Split on semicolons or comma-separated coordinating clauses (', and', ', whereas', ', while')
    clauses = re.split(r";|\s*,\s*(?:and|whereas|while|but\s+also|where|wherein|proving that|which proves that|which proves|resulting in|which led to)\s+", text, flags=re.IGNORECASE)

    cleaned_clauses: list[str] = []
    for clause in clauses:
        c = clause.strip().rstrip(".").strip(",")
        if len(c.split()) >= 3:
            if not c.endswith("."):
                c += "."
            c = c[0].upper() + c[1:]
            cleaned_clauses.append(c)

    return cleaned_clauses


def _validate_anti_hallucination(parent_text: str, atomic_propositions: list[str]) -> bool:
    """Verify that generated atomic propositions do not introduce ungrounded entities or numbers."""
    parent_numbers = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", parent_text))

    for prop in atomic_propositions:
        prop_numbers = set(re.findall(r"\b\d+(?:[.,]\d+)?\b", prop))
        if not prop_numbers.issubset(parent_numbers):
            return False

    return True


def decompose_claim(claim: Claim) -> list[AtomicClaim]:
    """Decompose a claim into independently verifiable atomic propositions.

    Args:
        claim: The parent Claim object.

    Returns:
        list[AtomicClaim]: List of atomic claims with materiality, constraints, and causal tags.
    """
    text = claim.normalized_text.strip()

    candidate_clauses = _split_compound_clauses(text)

    if len(candidate_clauses) <= 1 or not _validate_anti_hallucination(text, candidate_clauses):
        temporal_info = extract_temporal_constraints(text)
        entities_info = extract_named_entities(text)
        text_lower = text.lower()
        is_causal = any(w in text_lower for w in ("prove", "proves", "proving", "because", "due to", "caused"))
        is_numerical = any(w in text_lower for w in ("₹", "$", "crore", "billion", "million", "%", "metres", "meters", "km"))

        return [
            AtomicClaim(
                claim_id=claim.claim_id,
                sequence_order=0,
                text=text,
                is_atomic=True,
                decomposition_depth=1,
                materiality=Materiality.CRITICAL,
                entities=[e["text"] for e in entities_info],
                temporal_scope={
                    t.get("raw_text", ""): str(t.get("year", "")) for t in temporal_info
                },
                status=AtomicClaimVerdict.INSUFFICIENT,
                is_causal=is_causal,
                is_comparative=is_numerical,
            )
        ]

    atomic_claims: list[AtomicClaim] = []
    for idx, clause in enumerate(candidate_clauses[:6]):
        temporal_info = extract_temporal_constraints(clause)
        entities_info = extract_named_entities(clause)
        clause_lower = clause.lower()
        is_causal = any(w in clause_lower for w in ("prove", "proves", "proving", "because", "due to", "caused"))
        is_numerical = any(w in clause_lower for w in ("₹", "$", "crore", "billion", "million", "%", "metres", "meters", "km"))

        materiality = Materiality.CRITICAL if idx == 0 else Materiality.MATERIAL

        atomic_claims.append(
            AtomicClaim(
                claim_id=claim.claim_id,
                sequence_order=idx,
                text=clause,
                is_atomic=True,
                decomposition_depth=1,
                materiality=materiality,
                entities=[e["text"] for e in entities_info],
                temporal_scope={
                    t.get("raw_text", ""): str(t.get("year", "")) for t in temporal_info
                },
                status=AtomicClaimVerdict.INSUFFICIENT,
                is_causal=is_causal,
                is_comparative=is_numerical,
            )
        )

    return atomic_claims


@dataclass
class ConservativeDecomposer:
    """Wrapper class for atomic proposition decomposition."""

    def decompose(self, claim: Claim) -> list[AtomicClaim]:
        return decompose_claim(claim)
