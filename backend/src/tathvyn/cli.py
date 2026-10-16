"""Tathvyn - Command-Line Interface and Service Dispatcher.

Usage:
    tathvyn server [--port 8080] [--reload]
    tathvyn verify "Claim text here" [--depth FAST|STANDARD|DEEP]
    tathvyn benchmark
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from tathvyn.common.enums import VerificationMode
from tathvyn.common.logging import get_logger

logger = get_logger("cli")


def main() -> None:
    """Parse CLI arguments and dispatch to server or verification runner."""
    # Ensure UTF-8 output on Windows consoles
    if sys.platform == "win32":
        try:
            reconfig_out = getattr(sys.stdout, "reconfigure", None)
            if callable(reconfig_out):
                reconfig_out(encoding="utf-8", errors="replace")
            reconfig_err = getattr(sys.stderr, "reconfigure", None)
            if callable(reconfig_err):
                reconfig_err(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        prog="tathvyn",
        description="Tathvyn: Evidence Intelligence & Claim Verification Engine",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # 1. Server Subcommand
    server_parser = subparsers.add_parser("server", help="Start the FastAPI REST API server")
    server_parser.add_argument("--host", default="0.0.0.0", help="Host address (default: 0.0.0.0)")
    server_parser.add_argument("--port", type=int, default=8080, help="Port number (default: 8080)")
    server_parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")

    # 2. Verify Subcommand
    verify_parser = subparsers.add_parser("verify", help="Verify a natural language claim")
    verify_parser.add_argument("claim", nargs="+", help="Natural language claim string")
    verify_parser.add_argument(
        "--depth",
        choices=["FAST", "STANDARD", "DEEP"],
        default="STANDARD",
        help="Verification depth mode (default: STANDARD)",
    )
    verify_parser.add_argument("--mock", action="store_true", help="Use mock provider instead of live search")

    # 3. Benchmark Subcommand
    subparsers.add_parser("benchmark", help="Run 50-claim evaluation benchmark")

    args = parser.parse_args()

    if args.command == "server" or args.command is None:
        import uvicorn

        host = getattr(args, "host", "0.0.0.0")
        port = getattr(args, "port", 8080)
        reload = getattr(args, "reload", False)
        print(f"🚀 Starting Tathvyn API server on http://{host}:{port} (docs at /docs)...")
        uvicorn.run("tathvyn.api.app:create_app", factory=True, host=host, port=port, reload=reload)

    elif args.command == "verify":
        claim_text = " ".join(args.claim)
        depth = VerificationMode(args.depth)
        try:
            from pathlib import Path
            scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from scripts.verify_claim import verify_single_claim  # type: ignore[import-not-found]
            asyncio.run(verify_single_claim(claim_text=claim_text, depth=depth, use_mock=args.mock))
        except ImportError:
            from tathvyn.orchestration.engine import AdaptiveResearchEngine
            engine = AdaptiveResearchEngine()
            decision, _ = asyncio.run(engine.verify(claim_text=claim_text, depth=depth))
            print(f"Verdict: {decision.verdict.value} (Confidence: {decision.confidence:.2f})")

    elif args.command == "benchmark":
        try:
            from pathlib import Path
            scripts_dir = Path(__file__).resolve().parents[3] / "scripts"
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))
            from scripts.run_benchmark import (  # type: ignore[import-not-found]
                main as run_benchmark_main,
            )
            asyncio.run(run_benchmark_main())
        except ImportError:
            from tathvyn.evaluation.runner import BenchmarkRunner
            runner = BenchmarkRunner()
            asyncio.run(runner.run_benchmark(benchmark_file="tests/benchmarks/data/benchmark_seed_v1.json"))


if __name__ == "__main__":
    main()
