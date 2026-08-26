"""Tests for Benchmark Evaluation Runner."""

import json
from pathlib import Path

import pytest

from tathvyn.evaluation.runner import BenchmarkRunner


@pytest.mark.asyncio
async def test_benchmark_runner_execution(tmp_path: Path) -> None:
    """Verify benchmark runner parses JSON, runs pipeline, and produces metrics."""
    test_data = {
        "benchmark_id": "test_suite_v1",
        "claims": [
            {
                "claim_id": "test_1",
                "raw_text": "The speed of light in vacuum is approximately 299,792,458 m/s.",
                "category": "PHYSICS",
                "expected_verdict": "SUPPORTED",
                "ground_truth_context": "The speed of light in vacuum is exactly 299,792,458 m/s by international definition.",
            },
            {
                "claim_id": "test_2",
                "raw_text": "Chocolate ice cream is the absolute greatest dessert ever created.",
                "category": "OPINION",
                "expected_verdict": "UNVERIFIABLE",
            },
        ],
    }

    bench_file = tmp_path / "test_benchmark.json"
    with open(bench_file, "w", encoding="utf-8") as f:
        json.dump(test_data, f)

    runner = BenchmarkRunner()
    metrics, claim_results = await runner.run_benchmark(bench_file)

    assert metrics.total_samples == 2
    assert len(claim_results) == 2
    assert claim_results[0]["is_correct"] is True
    assert claim_results[1]["is_correct"] is True
    assert metrics.accuracy == 1.0
