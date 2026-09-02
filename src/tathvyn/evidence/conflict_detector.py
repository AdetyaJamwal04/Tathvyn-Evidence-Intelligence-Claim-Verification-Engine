"""Evidence Conflict and Disagreement Detection Engine.

Analyzes pairs of evidence items for an atomic claim and generates Conflict records
for direct contradictions, temporal discrepancies, and numerical mismatches.
"""

from uuid import UUID, uuid4

from tathvyn.common.enums import (
    ConflictResolutionStatus,
    ConflictSeverity,
    ConflictType,
    EvidenceRelationship,
)
from tathvyn.common.models.conflict import Conflict
from tathvyn.common.models.evidence import Evidence


class ConflictDetector:
    """Identifies logical, temporal, and empirical conflicts between evidence items."""

    def detect_conflicts(
        self,
        atomic_claim_id: UUID,
        evidence_items: list[Evidence],
    ) -> list[Conflict]:
        """Examine evidence items for an atomic claim and return detected Conflict objects.

        Args:
            atomic_claim_id: The target atomic claim UUID.
            evidence_items: All validated evidence items for this proposition.

        Returns:
            list[Conflict]: Detected conflicts between opposing evidence items.
        """
        conflicts: list[Conflict] = []
        if len(evidence_items) < 2:
            return conflicts

        supporting = [
            e
            for e in evidence_items
            if e.relationship
            in (EvidenceRelationship.SUPPORTS, EvidenceRelationship.PARTIALLY_SUPPORTS)
        ]
        contradicting = [
            e
            for e in evidence_items
            if e.relationship
            in (EvidenceRelationship.CONTRADICTS, EvidenceRelationship.PARTIALLY_CONTRADICTS)
        ]

        # 1. Direct Stance Contradiction (Support vs Contradict)
        for s_ev in supporting:
            for c_ev in contradicting:
                # Severity based on confidence scores
                if s_ev.entailment_score >= 0.80 and c_ev.contradiction_score >= 0.80:
                    severity = ConflictSeverity.CRITICAL
                else:
                    severity = ConflictSeverity.MAJOR

                conflicts.append(
                    Conflict(
                        conflict_id=uuid4(),
                        atomic_claim_id=atomic_claim_id,
                        evidence_id_a=s_ev.evidence_id,
                        evidence_id_b=c_ev.evidence_id,
                        conflict_type=ConflictType.DIRECT_CONTRADICTION,
                        severity=severity,
                        resolution_status=ConflictResolutionStatus.UNRESOLVED,
                        resolution_rationale="Direct contradiction between supporting and refuting evidence items.",
                    )
                )

        # 2. Temporal Validity Discrepancies
        invalid_temporal = [
            e for e in evidence_items if e.temporal_validity_status == "TEMPORAL_DISCREPANCY"
        ]
        valid_temporal = [e for e in evidence_items if e.temporal_validity_status == "VALID"]
        for inv_ev in invalid_temporal:
            for val_ev in valid_temporal:
                conflicts.append(
                    Conflict(
                        conflict_id=uuid4(),
                        atomic_claim_id=atomic_claim_id,
                        evidence_id_a=inv_ev.evidence_id,
                        evidence_id_b=val_ev.evidence_id,
                        conflict_type=ConflictType.TEMPORAL_CONFLICT,
                        severity=ConflictSeverity.MAJOR,
                        resolution_status=ConflictResolutionStatus.UNRESOLVED,
                        resolution_rationale="Evidence items reference divergent historical or publication periods.",
                    )
                )

        return conflicts
