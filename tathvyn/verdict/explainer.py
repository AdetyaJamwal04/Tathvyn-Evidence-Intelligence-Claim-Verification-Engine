"""
Grounded Explanation Generator and Citation Builder.

Assembles verifiable human-readable summaries and structured Citation objects
linking claim verdicts directly to source passages and URLs.
"""

from __future__ import annotations

from uuid import UUID

from tathvyn.common.enums import InternalVerdict
from tathvyn.common.models.evidence import Evidence
from tathvyn.common.models.source import Document, Passage
from tathvyn.common.models.verdict import Citation


class GroundedExplanationBuilder:
    """Constructs grounded summaries and structured citations with epistemic nuance."""

    def build_citations(
        self,
        evidence_items: list[Evidence],
        passages_by_id: dict[UUID, Passage],
        documents_by_id: dict[UUID, Document],
        max_citations: int = 5,
    ) -> list[Citation]:
        """Build structured citations from top evidence items."""
        citations: list[Citation] = []
        seen_urls: set[str] = set()

        for idx, ev in enumerate(evidence_items[:max_citations], start=1):
            passage = passages_by_id.get(ev.passage_id)
            if not passage:
                continue

            doc = documents_by_id.get(passage.document_id)
            url = doc.url if doc else "https://unknown.source"
            if url in seen_urls:
                continue
            seen_urls.add(url)

            domain = (
                doc.canonical_url.split("/")[2]
                if doc and "/" in doc.canonical_url
                else "source.org"
            )
            title = doc.title if doc and doc.title else domain

            citations.append(
                Citation(
                    citation_id=idx,
                    source_name=title,
                    domain=domain,
                    url=url,
                    authority_class="PRIMARY" if any(p in domain for p in ("isro.gov.in", "nasa.gov", "pib.gov.in", ".gov")) else "SECONDARY",
                    publication_date=doc.published_at if doc else None,
                    supporting_passage=passage.text,
                )
            )

        return citations

    def generate_summary(
        self,
        claim_text: str,
        verdict: InternalVerdict,
        citations: list[Citation],
        rationale: str,
    ) -> str:
        """Generate a grounded natural language summary paragraph distinguishing factual premises from causal inferences."""
        if verdict == InternalVerdict.SUPPORTED:
            summary = f"The claim '{claim_text}' is verified as accurate based on corroborating primary/secondary sources."
        elif verdict == InternalVerdict.REFUTED:
            summary = f"The claim '{claim_text}' is refuted by official and authoritative sources."
        elif verdict == InternalVerdict.PARTIALLY_SUPPORTED:
            summary = (
                f"The claim '{claim_text}' is a mixture of verified facts and unsupported or inaccurate inferences: "
                f"while specific empirical assertions are corroborated, the causal conclusion or scope requires substantial qualification."
            )
        elif verdict == InternalVerdict.UNVERIFIABLE:
            summary = f"The claim '{claim_text}' is unverifiable because it constitutes a subjective opinion, aesthetic preference, or normative value judgment."
        else:
            summary = f"The claim '{claim_text}' cannot be definitively verified due to insufficient public evidence or conflicting reports."

        if citations:
            citation_refs = ", ".join(f"[{c.citation_id}] ({c.domain})" for c in citations[:3])
            summary += f" Key sources: {citation_refs}."

        return summary
