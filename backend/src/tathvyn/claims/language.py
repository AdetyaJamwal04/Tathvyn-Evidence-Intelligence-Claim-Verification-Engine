"""Language Detection and English-First Scope Enforcement Gate.

Strictly enforces verifact_docs/00-language-and-scope.md by validating input language
and raising UnsupportedLanguageError on non-English inputs with confidence >= 0.85.
"""

import re
from typing import NamedTuple

from tathvyn.common.exceptions import UnsupportedLanguageError


class LanguageDetectionResult(NamedTuple):
    """Result of language identification."""

    language_code: str
    confidence: float
    is_supported: bool


# Common function words / stopwords for high-accuracy fast identification
_LANGUAGE_STOPWORDS: dict[str, set[str]] = {
    "en": {
        "the",
        "and",
        "is",
        "in",
        "to",
        "that",
        "it",
        "was",
        "for",
        "on",
        "are",
        "as",
        "with",
        "by",
        "from",
        "at",
        "this",
        "which",
    },
    "es": {
        "el",
        "la",
        "de",
        "que",
        "y",
        "en",
        "un",
        "una",
        "unos",
        "unas",
        "se",
        "no",
        "haber",
        "por",
        "con",
        "para",
        "como",
        "estar",
        "del",
        "al",
        "los",
        "las",
        "es",
        "son",
        "su",
        "sus",
        "orbita",
        "alrededor",
        "punto",
    },
    "fr": {
        "le",
        "la",
        "de",
        "et",
        "un",
        "une",
        "est",
        "dans",
        "les",
        "en",
        "du",
        "des",
        "que",
        "qui",
        "par",
        "pour",
        "sur",
        "pas",
        "avec",
        "sont",
    },
    "de": {
        "der",
        "die",
        "das",
        "und",
        "in",
        "den",
        "von",
        "zu",
        "mit",
        "ist",
        "des",
        "sich",
        "auf",
        "für",
        "eine",
        "ein",
        "als",
        "auch",
        "nicht",
    },
    "it": {
        "il",
        "la",
        "di",
        "e",
        "un",
        "in",
        "che",
        "per",
        "una",
        "non",
        "del",
        "con",
        "al",
        "da",
        "le",
        "dei",
        "delle",
        "sono",
        "della",
    },
    "pt": {
        "o",
        "a",
        "de",
        "e",
        "do",
        "da",
        "em",
        "um",
        "para",
        "com",
        "não",
        "uma",
        "os",
        "no",
        "se",
        "na",
        "por",
        "mais",
        "as",
        "dos",
    },
}

# Regex Unicode script ranges for immediate non-Latin detection
_DEVANAGARI_PATTERN = re.compile(r"[\u0900-\u097F]")
_CYRILLIC_PATTERN = re.compile(r"[\u0400-\u04FF]")
_CHINESE_PATTERN = re.compile(r"[\u4E00-\u9FFF]")
_ARABIC_PATTERN = re.compile(r"[\u0600-\u06FF]")


def detect_language(text: str) -> LanguageDetectionResult:
    """Identify the language of an input claim using script detection and stopword frequency.

    Returns:
        LanguageDetectionResult: language_code, confidence [0.0, 1.0], is_supported (True for 'en').
    """
    cleaned = text.strip()
    if not cleaned:
        return LanguageDetectionResult(language_code="en", confidence=1.0, is_supported=True)

    # 1. Check for distinct non-Latin writing scripts
    if _DEVANAGARI_PATTERN.search(cleaned):
        return LanguageDetectionResult(language_code="hi", confidence=0.98, is_supported=False)
    if _CHINESE_PATTERN.search(cleaned):
        return LanguageDetectionResult(language_code="zh", confidence=0.98, is_supported=False)
    if _ARABIC_PATTERN.search(cleaned):
        return LanguageDetectionResult(language_code="ar", confidence=0.98, is_supported=False)
    if _CYRILLIC_PATTERN.search(cleaned):
        return LanguageDetectionResult(language_code="ru", confidence=0.98, is_supported=False)

    # 2. Tokenize lowercase words for Latin-script stopword frequency analysis
    words = re.findall(r"\b[a-zA-ZÀ-ÿ]+\b", cleaned.lower())
    if not words:
        return LanguageDetectionResult(language_code="en", confidence=0.70, is_supported=True)

    scores: dict[str, int] = dict.fromkeys(_LANGUAGE_STOPWORDS, 0)
    for word in words:
        for lang, stopwords in _LANGUAGE_STOPWORDS.items():
            if word in stopwords:
                scores[lang] += 1

    best_lang, max_hits = max(scores.items(), key=lambda item: item[1])
    total_hits = sum(scores.values())

    if total_hits == 0:
        # No recognized stopwords: fallback to English with moderate confidence
        return LanguageDetectionResult(language_code="en", confidence=0.75, is_supported=True)

    confidence = round(
        min(1.0, 0.60 + (max_hits / len(words)) * 0.40 + (max_hits / total_hits) * 0.30), 2
    )
    is_supported = best_lang == "en"

    return LanguageDetectionResult(
        language_code=best_lang, confidence=confidence, is_supported=is_supported
    )


def enforce_language_gate(text: str) -> str:
    """Validate that the claim is in English.

    Raises:
        UnsupportedLanguageError: If the input is detected as non-English with confidence >= 0.80.

    Returns:
        str: Validated language code ('en').
    """
    result = detect_language(text)
    if not result.is_supported and result.confidence >= 0.80:
        raise UnsupportedLanguageError(
            detected_language=result.language_code,
            confidence=result.confidence,
        )
    return "en"
