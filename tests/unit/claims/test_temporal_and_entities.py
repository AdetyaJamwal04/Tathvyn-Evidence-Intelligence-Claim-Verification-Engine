"""Tests for Temporal Constraint and Named Entity Extractors."""

from tathvyn.claims.entity_extractor import extract_named_entities
from tathvyn.claims.temporal_extractor import extract_temporal_constraints


def test_extract_temporal_years_and_dates() -> None:
    """Verify extraction of dates, standalone years, and fiscal periods."""
    text = (
        "On July 20, 1969, Apollo 11 landed on the Moon, and later in FY 2023-24 investments rose."
    )
    intervals = extract_temporal_constraints(text)

    types = {i["type"] for i in intervals}
    assert "EXACT_DATE" in types
    assert "FISCAL_YEAR" in types

    exact_date = next(i for i in intervals if i["type"] == "EXACT_DATE")
    assert exact_date["year"] == 1969
    assert exact_date["month"] == "July"
    assert exact_date["day"] == 20


def test_extract_relative_temporal_anchors() -> None:
    """Verify relative markers (currently, recently)."""
    text = "The United Kingdom is currently an active member of the EU."
    intervals = extract_temporal_constraints(text)
    assert any(i.get("temporal_anchor") == "PRESENT" for i in intervals)


def test_extract_named_entities() -> None:
    """Verify entity extraction on benchmark assertions."""
    text = "Microsoft completed its acquisition of Activision Blizzard in 2023."
    entities = extract_named_entities(text)
    entity_texts = {e["text"] for e in entities}

    assert any("Microsoft" in ent for ent in entity_texts)
    assert any("Activision" in ent for ent in entity_texts)
