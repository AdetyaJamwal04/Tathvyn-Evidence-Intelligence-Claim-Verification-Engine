"""
Deterministic numerical and economic comparative validator.
Supports international & Indian numbering systems (Crore/Lakh/Billion), multi-currency, and relative tolerances.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import NamedTuple

from tathvyn.common.enums import EvidenceRelationship


class NumericalValidationResult(NamedTuple):
    """Result of numerical comparison."""

    is_compatible: bool
    discrepancy_ratio: float
    claim_numbers: list[float]
    evidence_numbers: list[float]
    validation_status: str


def _extract_numbers(text: str) -> list[float]:
    """Extract raw float numbers from text, removing commas."""
    matches = re.findall(r"\b\d+(?:[.,]\d+)?\b", text)
    numbers: list[float] = []
    for m in matches:
        cleaned = m.replace(",", "")
        try:
            numbers.append(float(cleaned))
        except ValueError:
            continue
    return numbers


def validate_numerical_consistency(
    claim_text: str,
    evidence_text: str,
    relative_tolerance: float = 0.05,
) -> NumericalValidationResult:
    """Validate whether numerical values in claim are corroborated by evidence text."""
    c_nums = _extract_numbers(claim_text)
    e_nums = _extract_numbers(evidence_text)

    if not c_nums:
        return NumericalValidationResult(
            is_compatible=True,
            discrepancy_ratio=0.0,
            claim_numbers=[],
            evidence_numbers=e_nums,
            validation_status="NO_NUMERICAL_ASSERTION",
        )

    if not e_nums:
        return NumericalValidationResult(
            is_compatible=False,
            discrepancy_ratio=1.0,
            claim_numbers=c_nums,
            evidence_numbers=[],
            validation_status="MISSING_EVIDENCE_NUMBERS",
        )

    max_discrepancy = 0.0
    all_matched = True

    for c_val in c_nums:
        if c_val == 0.0:
            min_diff = min(abs(e_val) for e_val in e_nums)
            rel_error = min_diff
        else:
            rel_error = min(abs(c_val - e_val) / abs(c_val) for e_val in e_nums)

        if rel_error > relative_tolerance:
            all_matched = False
        max_discrepancy = max(max_discrepancy, rel_error)

    status = "VALID" if all_matched else "NUMERICAL_MISMATCH"

    return NumericalValidationResult(
        is_compatible=all_matched,
        discrepancy_ratio=round(max_discrepancy, 4),
        claim_numbers=c_nums,
        evidence_numbers=e_nums,
        validation_status=status,
    )


@dataclass
class NumericalValidator:
    """Extracts, normalizes, and compares numerical & financial quantities across claims and evidence."""

    tolerance_ratio: float = 0.15

    def normalize_quantity(self, text: str) -> list[dict[str, float | str]]:
        """Extract and normalize quantities into standard base units."""
        results: list[dict[str, float | str]] = []
        patterns = [
            (r'(?:₹|rs\.?|inr)\s*([\d\.]+)\s*(crore|cr|lakh|lac|million|billion|b|m)?', 'INR'),
            (r'(?:\$|usd)\s*([\d\.]+)\s*(billion|b|million|m|trillion|t)?', 'USD'),
            (r'([\d\.]+)\s*(crore|cr|lakh|lac|billion|b|million|m|trillion|t)\b', 'COUNT'),
            (r'([\d\.]+)\s*(metres|meters|metre|meter|m|km|kilometers|kilometres)\b', 'DISTANCE'),
            (r'([\d\.]+)\s*(?:earth\s*)?(days|day|hours|hrs|years|yrs)\b', 'TIME'),
        ]

        text_lower = text.lower()
        unit_multipliers = {
            'lakh': 1e5,
            'lac': 1e5,
            'crore': 1e7,
            'cr': 1e7,
            'million': 1e6,
            'm': 1e6,
            'billion': 1e9,
            'b': 1e9,
            'trillion': 1e12,
            't': 1e12,
            'km': 1000.0,
            'kilometers': 1000.0,
            'kilometres': 1000.0,
            'metres': 1.0,
            'meters': 1.0,
            'metre': 1.0,
            'meter': 1.0,
            'days': 1.0,
            'day': 1.0,
            'hours': 1.0 / 24.0,
            'hrs': 1.0 / 24.0,
            'years': 365.0,
            'yrs': 365.0,
        }

        for regex, kind in patterns:
            for match in re.finditer(regex, text_lower):
                val_str = match.group(1)
                unit_str = match.group(2) if match.lastindex and match.lastindex >= 2 else None
                try:
                    base_val = float(val_str)
                    multiplier = unit_multipliers.get(unit_str, 1.0) if unit_str else 1.0
                    normalized_value = base_val * multiplier
                    results.append({
                        'kind': kind,
                        'raw_value': base_val,
                        'unit': unit_str or '',
                        'normalized_value': normalized_value,
                        'matched_text': match.group(0),
                    })
                except (ValueError, TypeError):
                    continue

        return results

    def validate_quantities(self, claim_text: str, evidence_text: str) -> EvidenceRelationship | None:
        """Validate numerical consistency between claim and supporting evidence passage."""
        claim_quantities = self.normalize_quantity(claim_text)
        evidence_quantities = self.normalize_quantity(evidence_text)

        if not claim_quantities or not evidence_quantities:
            return None

        for cq in claim_quantities:
            for eq in evidence_quantities:
                if cq['kind'] == eq['kind']:
                    c_val = float(cq['normalized_value'])
                    e_val = float(eq['normalized_value'])

                    diff = abs(c_val - e_val)
                    max_val = max(abs(c_val), abs(e_val), 1e-6)
                    ratio_diff = diff / max_val

                    if ratio_diff <= self.tolerance_ratio:
                        return EvidenceRelationship.ENTAILMENT
                    elif ratio_diff > 0.50:
                        return EvidenceRelationship.CONTRADICTION

                if cq['kind'] == 'INR' and eq['kind'] == 'USD':
                    c_val_usd = float(cq['normalized_value']) / 83.0
                    e_val_usd = float(eq['normalized_value'])
                    ratio = abs(c_val_usd - e_val_usd) / max(c_val_usd, e_val_usd, 1.0)
                    if ratio <= self.tolerance_ratio:
                        return EvidenceRelationship.ENTAILMENT

        return None
