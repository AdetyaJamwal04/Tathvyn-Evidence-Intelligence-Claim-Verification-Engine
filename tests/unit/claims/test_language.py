"""Tests for Language Detection and Language Gate Enforcer."""

import pytest

from tathvyn.claims.language import detect_language, enforce_language_gate
from tathvyn.common.exceptions import UnsupportedLanguageError


def test_english_detection_and_gate() -> None:
    """Verify standard English claims pass the language gate."""
    claim = "The speed of light in a vacuum is 299,792,458 meters per second."
    result = detect_language(claim)
    assert result.is_supported is True
    assert result.language_code == "en"

    validated_lang = enforce_language_gate(claim)
    assert validated_lang == "en"


def test_non_english_rejection() -> None:
    """Verify non-English claims raise UnsupportedLanguageError (HTTP 422)."""
    # Spanish
    spanish_claim = "La velocidad de la luz en el vacío es de 299.792.458 metros por segundo."
    with pytest.raises(UnsupportedLanguageError) as exc_info:
        enforce_language_gate(spanish_claim)
    assert exc_info.value.status_code == 422
    assert exc_info.value.error_code == "UNSUPPORTED_LANGUAGE"
    assert exc_info.value.details["detected_language"] == "es"

    # Hindi (Devanagari script)
    hindi_claim = "भारत की जीडीपी विकास दर 8.2 प्रतिशत रही।"
    with pytest.raises(UnsupportedLanguageError) as exc_info:
        enforce_language_gate(hindi_claim)
    assert exc_info.value.details["detected_language"] == "hi"

    # French
    french_claim = "Le président de la république a annoncé une nouvelle loi hier soir."
    with pytest.raises(UnsupportedLanguageError) as exc_info:
        enforce_language_gate(french_claim)
    assert exc_info.value.details["detected_language"] == "fr"


def test_empty_string_handling() -> None:
    """Verify empty string returns fallback without crashing."""
    result = detect_language("")
    assert result.is_supported is True
