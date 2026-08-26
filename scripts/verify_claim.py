"""Interactive CLI for Tathvyn Claim Verification.

Runs the complete adaptive research engine and fact verification pipeline
without requiring Docker, PostgreSQL, or Redis.
"""

import argparse
import asyncio
import sys

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tathvyn.common.config import get_settings
from tathvyn.common.enums import ResearchDepth
from tathvyn.orchestration.engine import AdaptiveResearchEngine
from tathvyn.retrieval.providers.mock import MockDocumentFetcher, MockSearchProvider


async def verify_single_claim(
    claim_text: str,
    depth: ResearchDepth = ResearchDepth.STANDARD,
    use_mock: bool = False,
) -> None:
    """Verify a single claim and print formatted decision output."""
    settings = get_settings()
    has_live_keys = bool(
        settings.tavily_api_key.get_secret_value()
        or settings.brave_search_api_key.get_secret_value()
    )

    should_use_mock = use_mock or not has_live_keys

    print(f'\n[1/4] 🚀 Analyzing Claim: "{claim_text}"')
    print(f"[*] Depth Profile: {depth.value}")

    if should_use_mock:
        print("[*] Mode:          Offline In-Memory Simulation (Mock Corroboration)")
        search_provider = MockSearchProvider()
        document_fetcher = MockDocumentFetcher(
            default_template=(
                f"Official documentation confirms that {claim_text}. "
                "This fact has been independently measured and verified across institutional records."
            )
        )
        engine = AdaptiveResearchEngine(
            search_provider=search_provider,
            document_fetcher=document_fetcher,
        )
    else:
        print("[*] Mode:          Live Real-Time Web Retrieval (Tavily/Brave Search)")
        engine = AdaptiveResearchEngine()

    print("[2/4] 🔎 Running Adaptive Research Graph & Evidence Cycle...")
    decision, state = await engine.verify(claim_text, depth=depth)

    print("[3/4] ⚖️ Epistemic Decision Reached!\n")
    print("-" * 65)
    print(f"📌 Public Verdict:        {decision.public_label.value}")
    print(f"📊 Internal Verdict:      {decision.verdict.value}")
    print(f"🎯 Calibrated Confidence: {decision.confidence * 100:.1f}%")
    print(f"📈 Evidence Sufficiency:  {decision.evidence_sufficiency * 100:.1f}%")
    print(f"⚠️  Framing Concerns:     {decision.framing_concerns}")
    print(f"🔄 Research Iterations:   {state.current_iteration}")
    print(f"⏹️  Stop Reason:          {decision.stop_reason}")
    print("-" * 65)
    print(f"\n📝 Grounded Summary:\n{decision.summary_text}\n")

    if decision.citations:
        print("📚 Grounded Citations:")
        for c in decision.citations:
            print(f"  [{c.citation_id}] {c.source_name} ({c.domain})")
            print(f"      URL: {c.url}")
            print(f'      Quote: "{c.supporting_passage}"\n')
    else:
        print("📚 Citations: None required or available.\n")
    print("=" * 65 + "\n")


async def main() -> None:
    parser = argparse.ArgumentParser(description="Tathvyn Claim Verification CLI")
    parser.add_argument("claim", nargs="*", help="The claim text to verify.")
    parser.add_argument(
        "--depth",
        choices=["FAST", "STANDARD", "DEEP"],
        default="STANDARD",
        help="Verification depth mode (FAST: 0 loops, STANDARD: <=2 loops, DEEP: <=3 loops).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Force in-memory mock search and document retrieval.",
    )

    parsed_args = parser.parse_args()

    if parsed_args.claim:
        claim_text = " ".join(parsed_args.claim)
    else:
        print("\n" + "=" * 65)
        print("🔍 Tathvyn — Automated Fact Verification Platform (MVP)")
        print("=" * 65)
        claim_text = input("\nEnter a claim to verify (or press Enter for default):\n> ").strip()
        if not claim_text:
            claim_text = "The James Webb Space Telescope operates around the Sun-Earth Lagrange Point 2 (L2)."

    depth = ResearchDepth(parsed_args.depth)
    await verify_single_claim(claim_text=claim_text, depth=depth, use_mock=parsed_args.mock)


if __name__ == "__main__":
    asyncio.run(main())
