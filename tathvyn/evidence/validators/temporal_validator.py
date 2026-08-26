"""Temporal Overlap and Expiration Validator.

Compares document publication dates and historical event mentions against the
claim's required temporal interval to ensure evidence temporal validity.
"""

from typing import NamedTuple

from tathvyn.claims.temporal_extractor import extract_temporal_constraints


class TemporalValidationResult(NamedTuple):
    """Result of temporal validity assessment."""

    is_temporally_valid: bool
    status: str
    claim_years: list[int]
    evidence_years: list[int]


def validate_temporal_alignment(
    claim_text: str,
    evidence_text: str,
    evidence_published_year: int | None = None,
) -> TemporalValidationResult:
    """Validate whether an evidence passage aligns temporally with the claim.

    Args:
        claim_text: The atomic claim text.
        evidence_text: The passage text.
        evidence_published_year: Optional document publication year.

    Returns:
        TemporalValidationResult: Validity boolean and status.
    """
    c_intervals = extract_temporal_constraints(claim_text)
    e_intervals = extract_temporal_constraints(evidence_text)

    c_years = [i["year"] for i in c_intervals if "year" in i]
    e_years = [i["year"] for i in e_intervals if "year" in i]

    if evidence_published_year and evidence_published_year not in e_years:
        e_years.append(evidence_published_year)

    # If claim doesn't specify a specific year or time period, temporal check passes
    if not c_years:
        return TemporalValidationResult(
            is_temporally_valid=True,
            status="UNCONSTRAINED_TEMPORAL",
            claim_years=[],
            evidence_years=e_years,
        )

    # If claim has specific years and evidence mentions years: check intersection or proximity (+- 1 year)
    if e_years:
        has_overlap = any(any(abs(cy - ey) <= 1 for ey in e_years) for cy in c_years)
        status = "VALID" if has_overlap else "TEMPORAL_DISCREPANCY"
        return TemporalValidationResult(
            is_temporally_valid=has_overlap,
            status=status,
            claim_years=c_years,
            evidence_years=e_years,
        )

    # If evidence has no years mentioned, assume valid if not explicitly contradicted
    return TemporalValidationResult(
        is_temporally_valid=True,
        status="NO_EVIDENCE_TIMESTAMP",
        claim_years=c_years,
        evidence_years=[],
    )
