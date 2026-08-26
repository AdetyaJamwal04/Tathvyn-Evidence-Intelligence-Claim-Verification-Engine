"""Unit Tests for Input Sanitization and Attack Gating."""

import pytest

from tathvyn.common.exceptions import SecurityViolationError
from tathvyn.common.security.sanitizer import InputSanitizer


def test_sanitize_valid_claim() -> None:
    raw = "   The Eiffel Tower in Paris was completed in 1889.   "
    cleaned = InputSanitizer.sanitize_claim_text(raw)
    assert cleaned == "The Eiffel Tower in Paris was completed in 1889."


def test_sanitize_unicode_nfkc_normalization() -> None:
    # Full-width characters and ligatures
    raw = "Ｔｈｅ Ｅｉｆｆｅｌ Ｔｏｗｅｒ was built in 1889."
    cleaned = InputSanitizer.sanitize_claim_text(raw)
    assert cleaned == "The Eiffel Tower was built in 1889."


def test_sanitize_zero_width_and_control_characters() -> None:
    # Hidden zero-width spaces (\u200B) and null-like control chars (\x07)
    raw = "The\u200b\u200c James\u200d Webb\x07 Telescope."
    cleaned = InputSanitizer.sanitize_claim_text(raw)
    assert cleaned == "The James Webb Telescope."


def test_sanitize_rejects_null_bytes() -> None:
    with pytest.raises(SecurityViolationError, match="Null bytes detected"):
        InputSanitizer.sanitize_claim_text("Dangerous\x00claim")


def test_sanitize_rejects_too_short_input() -> None:
    with pytest.raises(SecurityViolationError, match="too short"):
        InputSanitizer.sanitize_claim_text("abc", min_chars=4)


def test_sanitize_rejects_too_long_input() -> None:
    long_text = "A" * 1500
    with pytest.raises(SecurityViolationError, match="exceeds maximum allowed size"):
        InputSanitizer.sanitize_claim_text(long_text, max_chars=1000)
