"""Tests for Seed Benchmark Dataset Integrity."""

import json
from pathlib import Path

from tathvyn.common.enums import InternalVerdict, PublicVerdict


def test_seed_benchmark_dataset_validity() -> None:
    """Verify benchmark_seed_v1.json contains 50 valid annotated claims."""
    benchmark_path = Path("tests/benchmarks/data/benchmark_seed_v1.json")
    assert benchmark_path.exists(), "Seed benchmark file missing!"

    with open(benchmark_path, encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 50, f"Expected 50 seed benchmark claims, found {len(data)}"

    canonical_verdicts = {v.value for v in InternalVerdict}
    canonical_public = {p.value for p in PublicVerdict}

    for item in data:
        assert "benchmark_id" in item
        assert "claim" in item and len(item["claim"]) > 10
        assert item["expected_verdict"] in canonical_verdicts, (
            f"Invalid verdict: {item['expected_verdict']}"
        )
        assert item["expected_public_label"] in canonical_public, (
            f"Invalid public label: {item['expected_public_label']}"
        )
