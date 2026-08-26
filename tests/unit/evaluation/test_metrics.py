"""Tests for Evaluation Metrics Engine."""

from tathvyn.evaluation.metrics import (
    calculate_brier_score,
    calculate_confusion_matrix,
    calculate_expected_calibration_error,
    calculate_per_class_metrics,
    evaluate_benchmark_predictions,
)


def test_perfect_accuracy_and_f1() -> None:
    """Verify perfect predictions yield 1.0 accuracy and 1.0 F1."""
    y_true = ["SUPPORTED", "REFUTED", "UNVERIFIABLE"]
    y_pred = ["SUPPORTED", "REFUTED", "UNVERIFIABLE"]
    confidences = [0.95, 0.90, 1.0]

    result = evaluate_benchmark_predictions(y_true, y_pred, confidences)

    assert result.accuracy == 1.0
    assert result.macro_f1 == 1.0
    assert result.total_samples == 3
    assert result.expected_calibration_error >= 0.0


def test_confusion_matrix_and_per_class() -> None:
    """Verify confusion matrix counts and per-class precision/recall."""
    y_true = ["SUPPORTED", "SUPPORTED", "REFUTED"]
    y_pred = ["SUPPORTED", "REFUTED", "REFUTED"]

    matrix = calculate_confusion_matrix(y_true, y_pred)
    assert matrix["SUPPORTED"]["SUPPORTED"] == 1
    assert matrix["SUPPORTED"]["REFUTED"] == 1
    assert matrix["REFUTED"]["REFUTED"] == 1

    per_class = calculate_per_class_metrics(matrix)
    assert per_class["SUPPORTED"].recall == 0.50
    assert per_class["REFUTED"].recall == 1.0


def test_expected_calibration_error() -> None:
    """Verify ECE calculation with known calibration gap."""
    confidences = [0.90, 0.90, 0.90, 0.90]
    correctness = [
        True,
        True,
        False,
        False,
    ]  # True accuracy = 0.50, confidence = 0.90 -> error = 0.40

    ece = calculate_expected_calibration_error(confidences, correctness, n_bins=10)
    assert round(ece, 2) == 0.40


def test_brier_score() -> None:
    """Verify quadratic Brier score calculation."""
    confidences = [1.0, 0.0]
    correctness = [True, False]
    brier = calculate_brier_score(confidences, correctness)
    assert brier == 0.0
