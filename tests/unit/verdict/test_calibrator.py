"""Tests for Confidence Calibrator."""

from tathvyn.verdict.calibrator import ConfidenceCalibrator


def test_confidence_calibration_scaling() -> None:
    """Verify confidence is calibrated within bounds."""
    calibrator = ConfidenceCalibrator()
    calibrated = calibrator.calibrate(raw_confidence=0.95, sufficiency_score=1.0)
    assert 0.10 <= calibrated <= 0.98


def test_uncertainty_penalties() -> None:
    """Verify penalties reduce confidence under temporal discrepancies or conflicts."""
    calibrator = ConfidenceCalibrator()
    c_normal = calibrator.calibrate(raw_confidence=0.90, sufficiency_score=1.0)
    c_penalty = calibrator.calibrate(
        raw_confidence=0.90,
        sufficiency_score=1.0,
        has_temporal_discrepancy=True,
        has_unresolved_conflict=True,
    )
    assert c_penalty < c_normal
