"""CLI Script to Execute the Tathvyn 50-Claim Seed Benchmark.

Usage:
    uv run python scripts/run_benchmark.py [--max-claims 10] [--output reports/]
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tathvyn.evaluation.reporter import BenchmarkReporter
from tathvyn.evaluation.runner import BenchmarkRunner


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Tathvyn automated benchmark evaluation suite."
    )
    parser.add_argument(
        "--benchmark-file",
        type=str,
        default="tests/benchmarks/data/benchmark_seed_v1.json",
        help="Path to the seed benchmark JSON file.",
    )
    parser.add_argument(
        "--max-claims",
        type=int,
        default=None,
        help="Limit the number of claims to evaluate.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="reports",
        help="Directory to save generated evaluation reports.",
    )

    args = parser.parse_args()

    benchmark_path = Path(args.benchmark_file)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 65)
    print("🧪 Tathvyn Automated Benchmark Evaluation Suite")
    print(f"📁 Benchmark:  {benchmark_path}")
    print(f"📊 Max Claims: {args.max_claims or 'ALL (50)'}")
    print("=" * 65 + "\n")

    runner = BenchmarkRunner()
    metrics, claim_results = await runner.run_benchmark(
        benchmark_file=benchmark_path,
        max_claims=args.max_claims,
    )

    reporter = BenchmarkReporter()
    md_report = reporter.format_markdown_report(metrics, claim_results)

    md_path = output_dir / "benchmark_report_v1.md"
    json_path = output_dir / "benchmark_report_v1.json"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    reporter.export_json_report(metrics, claim_results, json_path)

    print("-" * 65)
    print("📈 Benchmark Execution Completed Successfully!")
    print(f"   Accuracy:                    {metrics.accuracy * 100:.1f}%")
    print(f"   Macro-F1:                    {metrics.macro_f1 * 100:.1f}%")
    print(f"   Expected Calibration Error:  {metrics.expected_calibration_error:.4f}")
    print(f"   Brier Score:                 {metrics.brier_score:.4f}")
    print(f"   Total Evaluated:             {metrics.total_samples}")
    print("-" * 65)
    print(f"📝 Markdown Report: {md_path.resolve()}")
    print(f"📄 JSON Report:     {json_path.resolve()}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
