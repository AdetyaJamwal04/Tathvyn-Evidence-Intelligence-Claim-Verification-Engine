"""
Causal and relational inference validator.
Distinguishes between factual verification, factual contradiction, and unsupported logical/causal leaps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tathvyn.common.enums import EvidenceRelationship


@dataclass
class InferenceValidator:
    """Detects invalid causal leaps and unsupported inferences in compound propositions."""

    causal_connectives: tuple[str, ...] = (
        "proves that",
        "which proves",
        "proving that",
        "proves",
        "proves the existence of",
        "because of which",
        "caused by",
        "resulting in",
        "which established that",
    )

    def is_causal_proposition(self, text: str) -> bool:
        """Check if a proposition asserts a causal/inferential link between two entities/events."""
        text_lower = text.lower()
        return any(conn in text_lower for conn in self.causal_connectives)

    def extract_premise_and_conclusion(self, text: str) -> tuple[str, str] | None:
        """Split a causal statement into Premise (A) and Inferred Conclusion (B)."""
        pattern = re.compile(
            r'^(.*?)\s+(?:proves that|which proves that|which proves|proving that|proves)\s+(.*)$',
            re.IGNORECASE,
        )
        match = pattern.match(text.strip().rstrip("."))
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return None

    def evaluate_causal_grounding(
        self,
        claim_text: str,
        evidence_passages: list[str],
    ) -> tuple[bool, str]:
        """Evaluate whether the causal inference claimed in the proposition is backed by the retrieved evidence.
        
        Returns:
            (is_supported, explanation)
        """
        if not self.is_causal_proposition(claim_text):
            return True, "Standard factual proposition (non-causal)."

        parts = self.extract_premise_and_conclusion(claim_text)
        if not parts:
            return True, "Non-decomposable causal structure."

        premise, conclusion = parts
        premise_lower = premise.lower()
        conclusion_lower = conclusion.lower()

        # Check if the combined premise + conclusion relationship is evidenced in retrieved text
        combined_mentions = 0
        premise_mentions = 0

        for passage in evidence_passages:
            p_lower = passage.lower()
            if any(k in p_lower for k in premise_lower.split() if len(k) > 3):
                premise_mentions += 1
                if any(c in p_lower for c in conclusion_lower.split() if len(c) > 3):
                    combined_mentions += 1

        if premise_mentions > 0 and combined_mentions == 0:
            return (
                False,
                f"Unsupported Causal Inference: Premise '{premise}' is documented, but the inferred conclusion '{conclusion}' lacks empirical causal linkage in primary literature.",
            )

        return True, "Causal inference sufficiently addressed in evidence."
