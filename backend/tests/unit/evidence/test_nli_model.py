"""Tests for DeBERTa-v3 NLI Stance Classifier."""

import pytest

from tathvyn.common.enums import EvidenceRelationship
from tathvyn.models.nli import DeBERTaNLIModel


@pytest.mark.asyncio
async def test_nli_entailment_support() -> None:
    """Verify entailment premise-hypothesis pair maps to SUPPORTS."""
    nli = DeBERTaNLIModel()
    premise = "Penicillin was discovered by Alexander Fleming at St. Mary's Hospital in 1928."
    hypothesis = "Alexander Fleming discovered penicillin in 1928."

    stance = await nli.predict_stance(premise, hypothesis)

    assert stance.relationship == EvidenceRelationship.SUPPORTS
    assert stance.entailment_prob > 0.60


@pytest.mark.asyncio
async def test_nli_contradiction() -> None:
    """Verify refutation premise maps to CONTRADICTS."""
    nli = DeBERTaNLIModel()
    premise = "Dennis Ritchie did not create Python; Guido van Rossum created Python in 1991."
    hypothesis = "Python was created by Dennis Ritchie."

    stance = await nli.predict_stance(premise, hypothesis)

    assert stance.relationship in (
        EvidenceRelationship.CONTRADICTS,
        EvidenceRelationship.PARTIALLY_CONTRADICTS,
    )
    assert stance.contradiction_prob > 0.50
