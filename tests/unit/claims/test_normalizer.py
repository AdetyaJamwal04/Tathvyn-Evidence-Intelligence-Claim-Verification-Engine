"""Tests for Claim Normalization and Framing Removal."""

from tathvyn.claims.normalizer import normalize_claim_text


def test_inquiry_framing_removal() -> None:
    """Verify conversational question prefixes are stripped."""
    raw = "Is it true that Albert Einstein failed mathematics in school?"
    result = normalize_claim_text(raw)
    assert result.was_framed_as_question is True
    assert "Is it true that" not in result.normalized_text
    assert result.normalized_text.startswith("Albert Einstein failed mathematics")


def test_whitespace_and_quote_normalization() -> None:
    """Verify smart quotes and irregular whitespace are normalized."""
    raw = "  “Neil Armstrong”   stated    ‘one small step’  "
    result = normalize_claim_text(raw)
    assert '"Neil Armstrong"' in result.normalized_text
    assert "'one small step'" in result.normalized_text
    assert "  " not in result.normalized_text
    assert len(result.content_hash) == 64


def test_declarative_claim_preservation() -> None:
    """Verify declarative assertions are preserved intact with a period."""
    raw = "India GDP grew 8.2% in FY24."
    result = normalize_claim_text(raw)
    assert result.normalized_text == "India GDP grew 8.2% in FY24."
    assert result.was_framed_as_question is False
