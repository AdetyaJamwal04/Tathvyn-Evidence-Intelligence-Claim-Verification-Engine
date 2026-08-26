"""
Parent Verdict Aggregator module with nuanced compound claim arbitration.
"""

from __future__ import annotations

from dataclasses import dataclass
from tathvyn.common.enums import (
    INTERNAL_TO_PUBLIC_VERDICT,
    AtomicClaimVerdict,
    ClaimVerifiability,
    InternalVerdict,
    Materiality,
    PublicVerdict,
)
from tathvyn.common.models.claim import AtomicClaim


@dataclass
class ParentAggregationResult:
    """The synthetic outcome of aggregating atomic propositions into a parent claim verdict."""

    internal_verdict: InternalVerdict
    public_label: PublicVerdict
    framing_concerns: bool
    rationale: str


class ParentVerdictAggregator:
    """Aggregates atomic claim proposition evaluations into parent claim verdicts."""

    def aggregate_verdicts(
        self,
        atomic_evaluations: list[tuple[AtomicClaim, AtomicClaimVerdict]],
        claim_verifiability: ClaimVerifiability = ClaimVerifiability.VERIFIABLE,
    ) -> ParentAggregationResult:
        """Aggregate atomic claim truth states into a canonical parent verdict.

        Args:
            atomic_evaluations: List of (AtomicClaim, AtomicClaimVerdict) pairs.
            claim_verifiability: Pre-classified claim verifiability.

        Returns:
            ParentAggregationResult: internal verdict, public label, and framing flags.
        """
        if claim_verifiability == ClaimVerifiability.UNVERIFIABLE:
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.UNVERIFIABLE,
                public_label=PublicVerdict.UNVERIFIABLE,
                framing_concerns=False,
                rationale="Claim is intrinsically subjective, opinion-based, or normative.",
            )

        if not atomic_evaluations:
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.INSUFFICIENT_EVIDENCE,
                public_label=PublicVerdict.UNVERIFIED,
                framing_concerns=False,
                rationale="No atomic claims evaluated.",
            )

        # Single atomic claim case
        if len(atomic_evaluations) == 1:
            _, verdict = atomic_evaluations[0]
            if verdict == AtomicClaimVerdict.SUPPORTED:
                iv = InternalVerdict.SUPPORTED
            elif verdict == AtomicClaimVerdict.REFUTED:
                iv = InternalVerdict.REFUTED
            elif verdict == AtomicClaimVerdict.UNVERIFIABLE:
                iv = InternalVerdict.UNVERIFIABLE
            else:
                iv = InternalVerdict.INSUFFICIENT_EVIDENCE

            return ParentAggregationResult(
                internal_verdict=iv,
                public_label=INTERNAL_TO_PUBLIC_VERDICT[iv],
                framing_concerns=False,
                rationale=f"Single atomic proposition evaluated as {verdict.value}.",
            )

        # Multi-claim compound aggregation logic
        critical_evals = [
            v for ac, v in atomic_evaluations if ac.materiality == Materiality.CRITICAL
        ]
        all_verdicts = [v for _, v in atomic_evaluations]

        # Count occurrences
        support_count = all_verdicts.count(AtomicClaimVerdict.SUPPORTED)
        refute_count = all_verdicts.count(AtomicClaimVerdict.REFUTED)
        insufficient_count = all_verdicts.count(AtomicClaimVerdict.INSUFFICIENT)

        # 1. Unanimous Support across all propositions
        if all(v == AtomicClaimVerdict.SUPPORTED for v in all_verdicts):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.SUPPORTED,
                public_label=PublicVerdict.LIKELY_TRUE,
                framing_concerns=False,
                rationale="All atomic propositions independently corroborated.",
            )

        # 2. Unanimous Refutation
        if all(v == AtomicClaimVerdict.REFUTED for v in all_verdicts):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.REFUTED,
                public_label=PublicVerdict.LIKELY_FALSE,
                framing_concerns=False,
                rationale="All atomic propositions decisively refuted by evidence.",
            )

        # 3. Mixed Truth Values (true factual premises combined with an unproven/refuted causal leap or error)
        if support_count > 0 and (refute_count > 0 or insufficient_count > 0):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.PARTIALLY_SUPPORTED,
                public_label=PublicVerdict.PARTIALLY_TRUE,
                framing_concerns=True,
                rationale=(
                    f"Compound claim combines verified factual elements ({support_count}/{len(all_verdicts)}) "
                    f"with unproven, misleading, or contradicted inferences ({refute_count + insufficient_count}/{len(all_verdicts)})."
                ),
            )

        # 4. Critical proposition refuted with no support
        if any(v == AtomicClaimVerdict.REFUTED for v in critical_evals) and support_count == 0:
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.REFUTED,
                public_label=PublicVerdict.LIKELY_FALSE,
                framing_concerns=False,
                rationale="Critical core proposition refuted by evidence.",
            )

        # 5. Default to INSUFFICIENT_EVIDENCE
        return ParentAggregationResult(
            internal_verdict=InternalVerdict.INSUFFICIENT_EVIDENCE,
            public_label=PublicVerdict.UNVERIFIED,
            framing_concerns=False,
            rationale="Insufficient evidence retrieved to establish truth or falsity.",
        )
