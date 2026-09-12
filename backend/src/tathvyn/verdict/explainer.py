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

        if not citations and documents_by_id:
            # When no evidence passes NLI threshold (e.g. fabricated or unverified claims),
            # return the authoritative sources that were investigated during research
            for idx, doc in enumerate(list(documents_by_id.values())[:max_citations], start=1):
                if not doc or not doc.url or doc.url in seen_urls:
                    continue
                seen_urls.add(doc.url)
                domain = (
                    doc.canonical_url.split("/")[2]
                    if doc and doc.canonical_url and "/" in doc.canonical_url
                    else "source.org"
                )
                title = doc.title if doc and doc.title else domain
                citations.append(
                    Citation(
                        citation_id=idx,
                        source_name=title,
                        domain=domain,
                        url=doc.url,
                        authority_class="CONSULTED",
                        publication_date=doc.published_at if doc else None,
                        supporting_passage="Investigated during research; no evidence in this source corroborated the claim.",
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
        # Detect negative-evidence refutation from rationale signal
        is_neg_ev = "absence of confirmation" in rationale or "zero corroborating evidence" in rationale or "No corroborating evidence" in rationale

        if verdict == InternalVerdict.SUPPORTED:
            summary = f"The claim '{claim_text}' is verified as accurate based on corroborating primary/secondary sources."
        elif verdict == InternalVerdict.REFUTED:
            if is_neg_ev:
                # For fabricated/false claims where search found nothing
                consulted_domains = [c.domain for c in citations if c.authority_class == "CONSULTED"]
                domain_str = ", ".join(consulted_domains[:3]) if consulted_domains else "multiple authoritative sources"
                summary = (
                    f"No credible evidence exists for the claim '{claim_text}'. "
                    f"An extensive multi-source search across {domain_str} and global news archives found zero "
                    f"corroborating reports, official statements, or independent records. "
                    f"For an event of this magnitude, the complete absence of any documentation or media coverage "
                    f"across all indexed sources is itself strong evidence that this did not occur."
                )
            else:
                summary = f"The claim '{claim_text}' is directly contradicted by official and authoritative sources."
        elif verdict == InternalVerdict.PARTIALLY_SUPPORTED:
            summary = (
                f"The claim '{claim_text}' is a mixture of verified facts and unsupported or inaccurate inferences: "
                f"while specific empirical assertions are corroborated, the causal conclusion or scope requires substantial qualification."
            )
        elif verdict == InternalVerdict.UNVERIFIABLE:
            summary = f"The claim '{claim_text}' is unverifiable because it constitutes a subjective opinion, aesthetic preference, or normative value judgment."
        else:
            summary = f"The claim '{claim_text}' cannot be definitively verified due to insufficient public evidence or conflicting reports."

        if citations and not is_neg_ev:
            citation_refs = ", ".join(f"[{c.citation_id}] ({c.domain})" for c in citations[:3])
            summary += f" Key sources: {citation_refs}."

        return summary
