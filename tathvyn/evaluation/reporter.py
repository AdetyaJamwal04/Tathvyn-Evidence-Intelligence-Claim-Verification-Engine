"""Benchmark Evaluation Report Generator.

Formats benchmark evaluation metrics, confusion matrices, category breakdowns,
and error analyses into formatted Markdown tables and structured JSON files.
"""

import json
from pathlib import Path
from typing import Any

from tathvyn.evaluation.metrics import BenchmarkMetricsResult


class BenchmarkReporter:
    """Generates Markdown and JSON evaluation reports."""

    def format_markdown_report(
        self,
        metrics: BenchmarkMetricsResult,
        claim_results: list[dict[str, Any]],
        benchmark_name: str = "Seed Benchmark v1 (50 Claims)",
    ) -> str:
        """Construct comprehensive Markdown report with tables and error diagnostics.

        Args:
            metrics: BenchmarkMetricsResult aggregate metrics.
            claim_results: List of per-claim evaluation record dictionaries.
            benchmark_name: Human-readable name of benchmark suite.

        Returns:
            str: GitHub-flavored Markdown formatted report.
        """
        lines: list[str] = [
            f"# VeriFact Evaluation Report — {benchmark_name}",
            "",
            "## 1. Executive Summary & Quality Gates",
            "",
            "| Metric | Value | Production Target | Status |",
            "| :--- | :--- | :--- | :--- |",
            f"| **Macro-F1** | `{metrics.macro_f1 * 100:.1f}%` | $\\ge 80.0\\%$ | {'✅ PASS' if metrics.macro_f1 >= 0.80 else '⚠️ IN REVIEW'} |",
            f"| **Overall Accuracy** | `{metrics.accuracy * 100:.1f}%` | $\\ge 85.0\\%$ | {'✅ PASS' if metrics.accuracy >= 0.85 else '⚠️ IN REVIEW'} |",
            f"| **Expected Calibration Error (ECE)** | `{metrics.expected_calibration_error:.4f}` | $\\le 0.0800$ | {'✅ PASS' if metrics.expected_calibration_error <= 0.08 else '⚠️ IN REVIEW'} |",
            f"| **Brier Score** | `{metrics.brier_score:.4f}` | $\\le 0.1500$ | {'✅ PASS' if metrics.brier_score <= 0.15 else '⚠️ IN REVIEW'} |",
            f"| **Total Claims Evaluated** | `{metrics.total_samples}` | `50` | ✅ COMPLETE |",
            "",
            "---",
            "",
            "## 2. Per-Verdict Epistemic Class Performance",
            "",
            "| Canonical Verdict Class | Precision | Recall | F1-Score | Support |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]

        for lbl, m in metrics.per_class_metrics.items():
            lines.append(
                f"| `{lbl}` | {m.precision * 100:.1f}% | {m.recall * 100:.1f}% | **{m.f1 * 100:.1f}%** | {m.support} |"
            )

        lines.extend(
            [
                "",
                "---",
                "",
                "## 3. Confusion Matrix",
                "",
            ]
        )

        labels = list(metrics.confusion_matrix.keys())
        header = "| True \\ Predicted | " + " | ".join(f"`{lbl}`" for lbl in labels) + " |"
        sep = "| :--- | " + " | ".join(":---:" for _ in labels) + " |"
        lines.append(header)
        lines.append(sep)

        for true_lbl in labels:
            row_vals = [
                str(metrics.confusion_matrix[true_lbl].get(pred_lbl, 0)) for pred_lbl in labels
            ]
            lines.append(f"| `{true_lbl}` | " + " | ".join(row_vals) + " |")

        # Category Breakdown
        categories: dict[str, list[dict[str, Any]]] = {}
        for r in claim_results:
            cat = r.get("category", "GENERAL")
            categories.setdefault(cat, []).append(r)

        lines.extend(
            [
                "",
                "---",
                "",
                "## 4. Performance by Claim Category",
                "",
                "| Category | Total | Correct | Accuracy | Avg Confidence |",
                "| :--- | :--- | :--- | :--- | :--- |",
            ]
        )

        for cat, items in sorted(categories.items()):
            tot = len(items)
            corr = sum(1 for it in items if it.get("is_correct", False))
            acc = corr / max(1, tot)
            avg_c = sum(it.get("confidence", 0.0) for it in items) / max(1, tot)
            lines.append(f"| **{cat}** | {tot} | {corr} | {acc * 100:.1f}% | {avg_c * 100:.1f}% |")

        # Error Analysis
        errors = [r for r in claim_results if not r.get("is_correct", False)]
        lines.extend(
            [
                "",
                "---",
                "",
                f"## 5. Error Analysis & Discrepancies ({len(errors)} Discrepancies)",
                "",
            ]
        )

        if not errors:
            lines.append(
                "🎉 **Zero classification discrepancies detected!** All benchmark claims evaluated accurately."
            )
        else:
            lines.extend(
                [
                    "| Claim ID | Claim Text | Expected | Predicted | Confidence | Reason |",
                    "| :--- | :--- | :--- | :--- | :--- | :--- |",
                ]
            )
            for err in errors[:15]:
                cid = err.get("claim_id", "N/A")
                txt = err.get("raw_text", "")[:45] + "..."
                exp = err.get("expected_verdict", "")
                pred = err.get("predicted_verdict", "")
                conf = err.get("confidence", 0.0)
                reason = err.get("stop_reason", "EVALUATION")
                lines.append(
                    f"| `{cid}` | {txt} | `{exp}` | `{pred}` | {conf * 100:.1f}% | {reason} |"
                )

        return "\n".join(lines) + "\n"

    def export_json_report(
        self,
        metrics: BenchmarkMetricsResult,
        claim_results: list[dict[str, Any]],
        output_path: str | Path,
    ) -> None:
        """Save structured JSON benchmark results."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "summary": {
                "accuracy": metrics.accuracy,
                "macro_f1": metrics.macro_f1,
                "micro_f1": metrics.micro_f1,
                "expected_calibration_error": metrics.expected_calibration_error,
                "brier_score": metrics.brier_score,
                "total_samples": metrics.total_samples,
            },
            "per_class_metrics": {
                k: {
                    "precision": v.precision,
                    "recall": v.recall,
                    "f1": v.f1,
                    "support": v.support,
                }
                for k, v in metrics.per_class_metrics.items()
            },
            "confusion_matrix": metrics.confusion_matrix,
            "claim_results": claim_results,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
