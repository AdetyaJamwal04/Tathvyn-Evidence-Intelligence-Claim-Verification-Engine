"""Tests for Sub-Goal and Query Formulator."""

from uuid import uuid4

from tathvyn.common.enums import ConflictSeverity, ConflictType
from tathvyn.common.models.claim import AtomicClaim
from tathvyn.common.models.conflict import Conflict
from tathvyn.orchestration.formulator import QueryFormulator


def test_initial_query_formulation() -> None:
    """Verify initial queries extract proposition text."""
    formulator = QueryFormulator()
    ac = AtomicClaim(claim_id=uuid4(), text="JWST was launched on December 25, 2021.")

    queries = formulator.formulate_initial_queries([ac])
    assert len(queries) == 1
    assert queries[0][0] == ac.atomic_claim_id
    assert "JWST was launched" in queries[0][1]


def test_refinement_query_formulation() -> None:
    """Verify refinement queries include keywords and avoid duplicates."""
    formulator = QueryFormulator()
    ac = AtomicClaim(
        claim_id=uuid4(), text="Sweden joined NATO as 32nd member state in March 2024."
    )

    past_queries = ["Sweden joined NATO as 32nd member state in March 2024."]
    refined = formulator.formulate_refinement_queries([ac], past_queries=past_queries)

    assert len(refined) == 1
    assert refined[0][0] == ac.atomic_claim_id
    assert refined[0][1] not in past_queries


def test_conflict_resolution_query_formulation() -> None:
    """Verify conflict resolution queries target official government archives."""
    formulator = QueryFormulator()
    ac = AtomicClaim(claim_id=uuid4(), text="Treaty signature event occurred in 1998.")
    conf = Conflict(
        conflict_id=uuid4(),
        atomic_claim_id=ac.atomic_claim_id,
        evidence_id_a=uuid4(),
        evidence_id_b=uuid4(),
        conflict_type=ConflictType.DIRECT_CONTRADICTION,
        severity=ConflictSeverity.CRITICAL,
    )

    queries = formulator.formulate_conflict_resolution_queries(
        conflicts=[conf],
        atomic_claims_by_id={ac.atomic_claim_id: ac},
        past_queries=[],
    )

    assert len(queries) == 1
    assert "official archives" in queries[0][1]
