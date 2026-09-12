"""Tests for Benchmark Report Generator."""

import json
from pathlib import Path

from tathvyn.evaluation.metrics import evaluate_benchmark_predictions
from tathvyn.evaluation.reporter import BenchmarkReporter


def test_markdown_and_json_report_generation(tmp_path: Path) -> None:
    """Verify Markdown and JSON reports are generated with tables."""
    y_true = ["SUPPORTED", "REFUTED", "UNVERIFIABLE"]
    y_pred = ["SUPPORTED", "REFUTED", "UNVERIFIABLE"]
    confidences = [0.95, 0.90, 1.0]

    metrics = evaluate_benchmark_predictions(y_true, y_pred, confidences)
    claim_results = [
        {
            "claim_id": "c1",
            "raw_text": "Sample claim 1",
            "category": "SCIENCE",
            "expected_verdict": "SUPPORTED",
            "predicted_verdict": "SUPPORTED",
            "confidence": 0.95,
            "is_correct": True,
        },
        {
            "claim_id": "c2",
            "raw_text": "Sample claim 2",
            "category": "HISTORY",
            "expected_verdict": "REFUTED",
            "predicted_verdict": "REFUTED",
            "confidence": 0.90,
            "is_correct": True,
        },
        {
            "claim_id": "c3",
            "raw_text": "Sample claim 3",
            "category": "OPINION",
            "expected_verdict": "UNVERIFIABLE",
            "predicted_verdict": "UNVERIFIABLE",
            "confidence": 1.0,
            "is_correct": True,
        },
    ]

    reporter = BenchmarkReporter()
    md = reporter.format_markdown_report(metrics, claim_results)

    assert "# VeriFact Evaluation Report" in md
    assert "Macro-F1" in md
    assert "Confusion Matrix" in md
    assert "SCIENCE" in md

    json_file = tmp_path / "report.json"
    reporter.export_json_report(metrics, claim_results, json_file)

    assert json_file.exists()
    with open(json_file, encoding="utf-8") as f:
        data = json.load(f)
    assert data["summary"]["accuracy"] == 1.0
    assert len(data["claim_results"]) == 3
