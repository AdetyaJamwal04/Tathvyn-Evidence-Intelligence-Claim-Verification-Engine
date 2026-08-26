"""Named Entity Extraction and Entity Disambiguation.

Extracts PERSON, ORG, GPE, PRODUCT, and EVENT entities using spaCy with
rule-based capitalization fallback for fast/offline execution.
"""

import re
from typing import Any

from tathvyn.common.logging import get_logger

logger = get_logger("entity_extractor")

# Lazy-loaded spaCy model container
_SPACY_NLP: Any = None


def _load_spacy_model() -> Any:
    """Lazy load spaCy transformer or small English model."""
    global _SPACY_NLP
    if _SPACY_NLP is not None:
        return _SPACY_NLP

    try:
        import spacy

        # Try loading transformer model first, fallback to small or blank
        for model_name in ["en_core_web_trf", "en_core_web_sm"]:
            try:
                _SPACY_NLP = spacy.load(model_name)
                logger.info("Loaded spaCy NER model", model=model_name)
                return _SPACY_NLP
            except Exception:
                continue
    except ImportError:
        pass

    return None


# Rule-based capitalized entity pattern as fallback
_CAPITALIZED_ENTITY_PATTERN = re.compile(
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+|\s+(?:of|the|and|for)\s+[A-Z][a-z]+)*\b"
)

_COMMON_TITLE_WORDS = {"The", "A", "An", "In", "On", "At", "By", "For", "With", "According", "If"}


def extract_named_entities(text: str) -> list[dict[str, Any]]:
    """Extract named entities from claim text.

    Returns:
        list[dict[str, Any]]: List of extracted entities with 'text', 'label', and char offsets.
    """
    nlp = _load_spacy_model()
    entities: list[dict[str, Any]] = []

    if nlp is not None:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in {"PERSON", "ORG", "GPE", "NORP", "FAC", "PRODUCT", "EVENT", "LAW"}:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start_char": ent.start_char,
                        "end_char": ent.end_char,
                    }
                )
        return entities

    # Fallback rule-based extractor if spaCy models are not downloaded locally
    for match in _CAPITALIZED_ENTITY_PATTERN.finditer(text):
        ent_text = match.group(0).strip()
        if ent_text in _COMMON_TITLE_WORDS:
            continue
        if len(ent_text) > 2:
            entities.append(
                {
                    "text": ent_text,
                    "label": "NAMED_ENTITY",
                    "start_char": match.start(),
                    "end_char": match.end(),
                }
            )

    return entities
