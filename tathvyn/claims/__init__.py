"""Claim Intelligence Package."""

from tathvyn.claims.classifier import ClassificationResult, classify_claim
from tathvyn.claims.decomposer import decompose_claim
from tathvyn.claims.entity_extractor import extract_named_entities
from tathvyn.claims.language import LanguageDetectionResult, detect_language, enforce_language_gate
from tathvyn.claims.normalizer import NormalizedClaimResult, normalize_claim_text
from tathvyn.claims.pipeline import ClaimIntelligencePipeline
from tathvyn.claims.temporal_extractor import extract_temporal_constraints

__all__ = [
    "ClaimIntelligencePipeline",
    "ClassificationResult",
    "LanguageDetectionResult",
    "NormalizedClaimResult",
    "classify_claim",
    "decompose_claim",
    "detect_language",
    "enforce_language_gate",
    "extract_named_entities",
    "extract_temporal_constraints",
    "normalize_claim_text",
]
