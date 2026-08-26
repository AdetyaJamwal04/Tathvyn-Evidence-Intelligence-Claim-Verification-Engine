"""Empirical Confidence Calibrator.

Applies temperature scaling, evidence sufficiency discounting, and uncertainty penalties
to ensure calibrated, reliable confidence scores and low ECE.
"""

import math


class ConfidenceCalibrator:
    """Calibrates confidence scores using temperature scaling and epistemic penalties."""

    def __init__(self, temperature: float = 1.25) -> None:
        self.temperature = temperature

    def calibrate(
        self,
        raw_confidence: float,
        sufficiency_score: float,
        has_temporal_discrepancy: bool = False,
        has_unresolved_conflict: bool = False,
    ) -> float:
        """Compute calibrated confidence score.

        Args:
            raw_confidence: Initial confidence estimate [0.0, 1.0].
            sufficiency_score: Q_suff [0.0, 1.0].
            has_temporal_discrepancy: True if evidence has date mismatches.
            has_unresolved_conflict: True if opposing evidence was detected.

        Returns:
            float: Calibrated confidence score in range [0.10, 0.98].
        """
        # Clamp raw confidence away from exact 0.0 / 1.0
        c = max(0.01, min(0.99, raw_confidence))

        # 1. Temperature scaling on logit
        logit = math.log(c / (1.0 - c))
        scaled_logit = logit / self.temperature
        calibrated = 1.0 / (1.0 + math.exp(-scaled_logit))

        # 2. Sufficiency scaling penalty
        suff_factor = 0.50 + (0.50 * max(0.0, min(1.0, sufficiency_score)))
        calibrated *= suff_factor

        # 3. Uncertainty penalties
        if has_temporal_discrepancy:
            calibrated *= 0.85

        if has_unresolved_conflict:
            calibrated *= 0.70

        # Bound calibrated confidence
        return round(max(0.10, min(0.98, calibrated)), 4)
