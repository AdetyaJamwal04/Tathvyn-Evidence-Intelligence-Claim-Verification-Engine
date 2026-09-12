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
        docs_retrieved: int = 0,
    ) -> ParentAggregationResult:
        """Aggregate atomic claim truth states into a canonical parent verdict.

        Args:
            atomic_evaluations: List of (AtomicClaim, AtomicClaimVerdict) pairs.
            claim_verifiability: Pre-classified claim verifiability.
            docs_retrieved: Number of source documents fetched during research.
                Used to distinguish genuine absence-of-evidence (fabrication signal)
                from failed retrieval.

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
            elif docs_retrieved >= 2 and verdict == AtomicClaimVerdict.INSUFFICIENT:
                # When topic documents were retrieved but zero corroboration was found
                iv = InternalVerdict.REFUTED
            else:
                iv = InternalVerdict.INSUFFICIENT_EVIDENCE

            pub = INTERNAL_TO_PUBLIC_VERDICT[iv]
            rationale = (
                f"Multi-source web search ({docs_retrieved} sources) found zero corroborating evidence. "
                "The complete absence of confirmation in authoritative records refutes the assertion."
                if iv == InternalVerdict.REFUTED and verdict == AtomicClaimVerdict.INSUFFICIENT
                else f"Single atomic proposition evaluated as {verdict.value}."
            )

            return ParentAggregationResult(
                internal_verdict=iv,
                public_label=pub,
                framing_concerns=False,
                rationale=rationale,
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

        # 5. All REFUTED (via negative-evidence path from atomic evaluator)
        if all(v == AtomicClaimVerdict.REFUTED for v in all_verdicts):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.REFUTED,
                public_label=PublicVerdict.LIKELY_FALSE,
                framing_concerns=False,
                rationale="No corroborating evidence found across searched sources. Extraordinary claims require extraordinary evidence.",
            )

        # 6. All INSUFFICIENT but documents WERE actually retrieved — this is the
        # "no evidence found for a searchable topic" signal (fabricated/false claims).
        if (
            all(v == AtomicClaimVerdict.INSUFFICIENT for v in all_verdicts)
            and docs_retrieved >= 2
            and support_count == 0
        ):
            return ParentAggregationResult(
                internal_verdict=InternalVerdict.REFUTED,
                public_label=PublicVerdict.LIKELY_FALSE,
                framing_concerns=False,
                rationale=(
                    f"Extensive multi-source search ({docs_retrieved} sources) found zero corroborating evidence. "
                    "For extraordinary factual claims, absence of any confirmation across authoritative sources "
                    "constitutes a refutation."
                ),
            )

        # 7. Default to INSUFFICIENT_EVIDENCE (truly no data — e.g., network failure or obscure topic)
        return ParentAggregationResult(
            internal_verdict=InternalVerdict.INSUFFICIENT_EVIDENCE,
            public_label=PublicVerdict.UNVERIFIED,
            framing_concerns=False,
            rationale="Insufficient evidence retrieved to establish truth or falsity.",
        )
