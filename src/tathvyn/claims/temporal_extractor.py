"""Temporal Scope and Date Interval Extraction.

Extracts explicit years, fiscal periods, exact dates, and relative temporal constraints
from claim text and maps them into structured intervals.
"""

import re
from typing import Any

# Regex patterns for temporal extraction
_YEAR_PATTERN = re.compile(r"\b(18\d{2}|19\d{2}|20\d{2})\b")
_FISCAL_YEAR_PATTERN = re.compile(
    r"\b(?:FY|financial\s+year|fiscal\s+year)\s*(\d{2,4})[-/]?(\d{2,4})?\b", re.IGNORECASE
)
_MONTH_YEAR_PATTERN = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b",
    re.IGNORECASE,
)
_FULL_DATE_PATTERN = re.compile(
    r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b",
    re.IGNORECASE,
)
_RELATIVE_TEMPORAL_TERMS = {
    "currently": "PRESENT",
    "today": "PRESENT",
    "now": "PRESENT",
    "recent": "RECENT",
    "recently": "RECENT",
    "historic": "PAST",
    "historically": "PAST",
    "ancient": "ANCIENT",
}


def extract_temporal_constraints(text: str) -> list[dict[str, Any]]:
    """Extract all temporal constraints from text and return normalized interval dictionaries.

    Returns:
        list[dict[str, Any]]: List of extracted temporal intervals and markers.
    """
    intervals: list[dict[str, Any]] = []

    # 1. Full dates (e.g. "July 20, 1969")
    for match in _FULL_DATE_PATTERN.finditer(text):
        month, day, year = match.groups()
        intervals.append(
            {
                "type": "EXACT_DATE",
                "raw_text": match.group(0),
                "year": int(year),
                "month": month.capitalize(),
                "day": int(day),
                "normalized_iso": f"{year}-{month}-{day}",
            }
        )

    # 2. Month + Year (e.g. "October 2023")
    for match in _MONTH_YEAR_PATTERN.finditer(text):
        month, year = match.groups()
        # Avoid duplicating if already matched in full date
        if not any(
            item.get("year") == int(year) and item.get("month") == month.capitalize()
            for item in intervals
        ):
            intervals.append(
                {
                    "type": "MONTH_YEAR",
                    "raw_text": match.group(0),
                    "year": int(year),
                    "month": month.capitalize(),
                }
            )

    # 3. Fiscal / Financial years (e.g. "financial year 2023-24")
    for match in _FISCAL_YEAR_PATTERN.finditer(text):
        start_y = match.group(1)
        end_y = match.group(2)
        intervals.append(
            {
                "type": "FISCAL_YEAR",
                "raw_text": match.group(0),
                "start_year": start_y,
                "end_year": end_y,
            }
        )

    # 4. Standalone 4-digit years (e.g. "in 2025")
    for match in _YEAR_PATTERN.finditer(text):
        year_str = match.group(0)
        year_val = int(year_str)
        if not any(item.get("year") == year_val for item in intervals):
            intervals.append(
                {
                    "type": "YEAR",
                    "raw_text": year_str,
                    "year": year_val,
                }
            )

    # 5. Relative temporal markers (e.g. "currently", "recently")
    words = text.lower().split()
    for word in words:
        cleaned_word = word.strip(".,;:!?()[]\"'")
        if cleaned_word in _RELATIVE_TEMPORAL_TERMS:
            intervals.append(
                {
                    "type": "RELATIVE_TEMPORAL",
                    "raw_text": cleaned_word,
                    "temporal_anchor": _RELATIVE_TEMPORAL_TERMS[cleaned_word],
                }
            )

    return intervals
