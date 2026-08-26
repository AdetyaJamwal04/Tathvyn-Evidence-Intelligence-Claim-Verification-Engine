"""
Evidence Sufficiency Gate (Q_suff) Calculation.

Computes multi-dimensional evidence sufficiency based on independent corroboration,
relevance, and primary source authority scores.
"""

from __future__ import annotations

from typing import NamedTuple

from tathvyn.common.enums import AuthorityClass
from tathvyn.common.models.evidence import Evidence


class SufficiencyResult(NamedTuple):
    """Result of evidence sufficiency calculation."""

    sufficiency_score: float
    is_sufficient: bool
    total_evidence_weight: float
    reason: str


SUFFICIENCY_THRESHOLD = 1.5  # Standard threshold required for definitive verdict


def calculate_evidence_sufficiency(
    evidence_items: list[Evidence],
    threshold: float = SUFFICIENCY_THRESHOLD,
) -> SufficiencyResult:
    """Calculate multi-dimensional evidence sufficiency Q_suff.

    Args:
        evidence_items: List of assessed Evidence items.
        threshold: Sufficiency threshold mass (default 1.5).

    Returns:
        SufficiencyResult: Q_suff score [0.0, 1.0], is_sufficient boolean, and reason.
    """
    if not evidence_items:
        return SufficiencyResult(
            sufficiency_score=0.0,
            is_sufficient=False,
            total_evidence_weight=0.0,
            reason="No relevant evidence items retrieved.",
        )

    total_weight = 0.0
    primary_count = 0

    for e in evidence_items:
        # Check primary authority status
        is_primary = getattr(e, "authority_class", None) == AuthorityClass.PRIMARY or (e.source_quality_score >= 0.90)
        if is_primary:
            primary_count += 1

        # Weight = independence_score * source_quality_score * relevance_score
        weight = e.independence_score * e.source_quality_score * e.relevance_score
        if is_primary:
            weight *= 1.35  # Primary institutional authority escalation multiplier
        total_weight += weight

    q_suff = min(1.0, total_weight / threshold)
    # If primary institutional source is present, allow sufficiency to reach authoritative status
    if primary_count > 0:
        q_suff = max(q_suff, 0.85)

    is_sufficient = q_suff >= 0.60

    reason = (
        f"Evidence mass of {total_weight:.2f} satisfies sufficiency threshold (Q_suff = {q_suff:.2f})."
        if is_sufficient
        else f"Insufficient evidence mass ({total_weight:.2f} < threshold {threshold}). Q_suff = {q_suff:.2f}."
    )

    return SufficiencyResult(
        sufficiency_score=round(q_suff, 4),
        is_sufficient=is_sufficient,
        total_evidence_weight=round(total_weight, 4),
        reason=reason,
    )
