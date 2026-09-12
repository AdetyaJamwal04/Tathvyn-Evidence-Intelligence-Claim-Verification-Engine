"""Evaluation Metrics and Statistical Analysis Engine.

Calculates multi-class classification metrics (Accuracy, Macro-F1, Micro-F1,
Per-Class Precision/Recall), Expected Calibration Error (ECE), Multi-Class
Brier Score, and Confusion Matrix.
"""

from typing import NamedTuple

from tathvyn.common.enums import InternalVerdict


class PerClassMetrics(NamedTuple):
    """Precision, recall, and F1 for an individual verdict class."""

    precision: float
    recall: float
    f1: float
    support: int


class BenchmarkMetricsResult(NamedTuple):
    """Aggregate benchmark performance and calibration metrics."""

    accuracy: float
    macro_f1: float
    micro_f1: float
    expected_calibration_error: float
    brier_score: float
    total_samples: int
    per_class_metrics: dict[str, PerClassMetrics]
    confusion_matrix: dict[str, dict[str, int]]


ALL_VERDICTS = [
    InternalVerdict.SUPPORTED.value,
    InternalVerdict.REFUTED.value,
    InternalVerdict.PARTIALLY_SUPPORTED.value,
    InternalVerdict.INSUFFICIENT_EVIDENCE.value,
    InternalVerdict.UNVERIFIABLE.value,
]


def calculate_confusion_matrix(
    y_true: list[str],
    y_pred: list[str],
    labels: list[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Compute confusion matrix mapping true_label -> {pred_label: count}."""
    verdict_labels = labels or ALL_VERDICTS
    matrix: dict[str, dict[str, int]] = {
        true_lbl: dict.fromkeys(verdict_labels, 0) for true_lbl in verdict_labels
    }

    for t, p in zip(y_true, y_pred, strict=False):
        if t in matrix and p in matrix[t]:
            matrix[t][p] += 1

    return matrix


def calculate_per_class_metrics(
    matrix: dict[str, dict[str, int]],
    labels: list[str] | None = None,
) -> dict[str, PerClassMetrics]:
    """Compute precision, recall, and F1 score for each verdict class."""
    verdict_labels = labels or ALL_VERDICTS
    metrics: dict[str, PerClassMetrics] = {}

    for lbl in verdict_labels:
        tp = matrix[lbl][lbl]
        fn = sum(matrix[lbl][pred] for pred in verdict_labels if pred != lbl)
        fp = sum(matrix[actual][lbl] for actual in verdict_labels if actual != lbl)
        total_support = tp + fn

        precision = tp / max(1, (tp + fp)) if (tp + fp) > 0 else 0.0
        recall = tp / max(1, (tp + fn)) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        metrics[lbl] = PerClassMetrics(
            precision=round(precision, 4),
            recall=round(recall, 4),
            f1=round(f1, 4),
            support=total_support,
        )

    return metrics


def calculate_expected_calibration_error(
    confidences: list[float],
    correctness: list[bool],
    n_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE) across confidence bins.

    Args:
        confidences: Predicted confidence probability for each sample in [0.0, 1.0].
        correctness: Boolean indicating if prediction matched ground truth.
        n_bins: Number of equal-width bins (default 10).

    Returns:
        float: Weighted calibration error in [0.0, 1.0].
    """
    if not confidences or not correctness:
        return 0.0

    n_samples = len(confidences)
    bin_size = 1.0 / n_bins
    ece = 0.0

    for i in range(n_bins):
        bin_lower = i * bin_size
        bin_upper = (i + 1) * bin_size

        # Find items falling into this confidence interval
        bin_indices = [
            idx
            for idx, c in enumerate(confidences)
            if bin_lower <= c < bin_upper or (i == n_bins - 1 and c == 1.0)
        ]

        if not bin_indices:
            continue

        bin_count = len(bin_indices)
        avg_confidence = sum(confidences[idx] for idx in bin_indices) / bin_count
        avg_accuracy = sum(1.0 for idx in bin_indices if correctness[idx]) / bin_count

        bin_error = abs(avg_accuracy - avg_confidence)
        ece += (bin_count / n_samples) * bin_error

    return round(ece, 4)


def calculate_brier_score(
    confidences: list[float],
    correctness: list[bool],
) -> float:
    """Compute mean squared error between confidence probabilities and binary outcomes."""
    if not confidences or not correctness:
        return 0.0

    total_squared_error = sum(
        (conf - (1.0 if corr else 0.0)) ** 2
        for conf, corr in zip(confidences, correctness, strict=False)
    )
    return round(total_squared_error / len(confidences), 4)


def evaluate_benchmark_predictions(
    y_true: list[str],
    y_pred: list[str],
    confidences: list[float],
    labels: list[str] | None = None,
) -> BenchmarkMetricsResult:
    """Calculate comprehensive benchmark metrics from ground-truth and predictions.

    Args:
        y_true: Ground truth canonical verdict strings.
        y_pred: Predicted canonical verdict strings.
        confidences: Calibrated confidence scores.
        labels: Optional ordered list of verdict strings.

    Returns:
        BenchmarkMetricsResult: Complete metrics dataset.
    """
    total = len(y_true)
    if total == 0:
        return BenchmarkMetricsResult(
            accuracy=0.0,
            macro_f1=0.0,
            micro_f1=0.0,
            expected_calibration_error=0.0,
            brier_score=0.0,
            total_samples=0,
            per_class_metrics={},
            confusion_matrix={},
        )

    verdict_labels = labels or ALL_VERDICTS
    matrix = calculate_confusion_matrix(y_true, y_pred, labels=verdict_labels)
    per_class = calculate_per_class_metrics(matrix, labels=verdict_labels)

    correct_flags = [t == p for t, p in zip(y_true, y_pred, strict=False)]
    accuracy = sum(1.0 for c in correct_flags if c) / total

    # Macro-F1 is unweighted mean of active classes with support > 0
    active_classes = [metrics for metrics in per_class.values() if metrics.support > 0]
    macro_f1 = sum(m.f1 for m in active_classes) / max(1, len(active_classes))

    # Micro-F1 equals overall accuracy in single-label multi-class
    micro_f1 = accuracy

    ece = calculate_expected_calibration_error(confidences, correct_flags)
    brier = calculate_brier_score(confidences, correct_flags)

    return BenchmarkMetricsResult(
        accuracy=round(accuracy, 4),
        macro_f1=round(macro_f1, 4),
        micro_f1=round(micro_f1, 4),
        expected_calibration_error=ece,
        brier_score=brier,
        total_samples=total,
        per_class_metrics=per_class,
        confusion_matrix=matrix,
    )
