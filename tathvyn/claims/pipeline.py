"""End-to-End Claim Intelligence Pipeline.

Orchestrates language gating, normalization, semantic classification, entity/temporal
extraction, and conservative atomic decomposition into a unified ClaimAnalysis object.
"""

from uuid import UUID, uuid4

from tathvyn.claims.classifier import classify_claim
from tathvyn.claims.decomposer import decompose_claim
from tathvyn.claims.entity_extractor import extract_named_entities
from tathvyn.claims.language import enforce_language_gate
from tathvyn.claims.normalizer import normalize_claim_text
from tathvyn.claims.temporal_extractor import extract_temporal_constraints
from tathvyn.common.logging import get_logger
from tathvyn.common.models.claim import Claim, ClaimAnalysis
from tathvyn.common.security import InputSanitizer

logger = get_logger("claim_intelligence")


class ClaimIntelligencePipeline:
    """Pipeline coordinating all Phase 1 Claim Intelligence capabilities."""

    def __init__(self) -> None:
        logger.info("Initialized ClaimIntelligencePipeline")

    def analyze(self, raw_input: str, request_id: UUID | None = None) -> ClaimAnalysis:
        """Execute complete claim intelligence on raw input.

        Args:
            raw_input: Raw string supplied by the user / API.
            request_id: Optional client / session UUID.

        Returns:
            ClaimAnalysis: Validated claim, atomic claims, classification, and entities.
        """
        req_id = request_id or uuid4()

        # 0. Input Sanitization & Attack Gating (Unicode NFKC, zero-width stripping, length limits)
        sanitized_input = InputSanitizer.sanitize_claim_text(raw_input)

        # 1. Language Gate: Reject non-English inputs early with HTTP 422
        language_code = enforce_language_gate(sanitized_input)

        # 2. Text Normalization & Framing Removal
        norm_result = normalize_claim_text(sanitized_input)

        # 3. Multi-Label Semantic Classification
        classification = classify_claim(norm_result.normalized_text)

        # 4. Entity and Temporal Extraction
        entities = extract_named_entities(norm_result.normalized_text)
        temporal_intervals = extract_temporal_constraints(norm_result.normalized_text)

        # 5. Construct Parent Claim Model
        claim = Claim(
            claim_id=uuid4(),
            request_id=req_id,
            raw_text=raw_input,
            normalized_text=norm_result.normalized_text,
            language_code=language_code,
            primary_type=classification.primary_type,
            secondary_types=classification.secondary_types,
            domain=classification.domain,
            complexity=classification.complexity,
            verifiability=classification.verifiability,
            is_atomic=False,
            content_hash=norm_result.content_hash,
        )

        # 6. Conservative Atomic Decomposition
        atomic_claims = decompose_claim(claim)

        # If single atomic claim was returned and text matches parent, mark parent is_atomic accordingly
        if len(atomic_claims) == 1:
            claim.is_atomic = True

        logger.info(
            "Claim analyzed successfully",
            claim_id=str(claim.claim_id),
            primary_type=claim.primary_type.value,
            atomic_count=len(atomic_claims),
            domain=claim.domain,
        )

        return ClaimAnalysis(
            claim=claim,
            atomic_claims=atomic_claims,
            extracted_entities=[
                {"text": e["text"], "label": str(e.get("label", "NAMED_ENTITY"))} for e in entities
            ],
            extracted_temporal_intervals=[
                {k: str(v) for k, v in t.items()} for t in temporal_intervals
            ],
            verifiability_reasoning=classification.verifiability_reasoning,
        )
