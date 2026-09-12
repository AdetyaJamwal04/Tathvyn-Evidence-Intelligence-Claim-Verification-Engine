"""
Provenance Grouping, Authority Classification, and Syndication Deduplication.

Computes source independence scores based on domain clustering and verbatim quotation overlap.
"""

from __future__ import annotations

from urllib.parse import urlparse
from uuid import UUID, uuid4

from tathvyn.common.enums import AuthorityClass, ProvenanceDetectionMethod
from tathvyn.common.models.evidence import Evidence
from tathvyn.common.models.provenance import ProvenanceGroup
from tathvyn.common.models.source import Document, Passage

# Authoritative Primary Institutional Domains
_PRIMARY_INSTITUTIONAL_DOMAINS = {
    # Space & Science Agencies
    "isro.gov.in", "nasa.gov", "jpl.nasa.gov", "esa.int", "jaxa.jp", "cnsa.gov.cn", "dlr.de", "cnes.fr",
    # Government & Official Registries
    "pib.gov.in", "gov.in", "nic.in", "whitehouse.gov", "gov.uk", "europa.eu", "un.org", "who.int",
    "cdc.gov", "fda.gov", "nih.gov", "sec.gov", "rbi.org.in", "federalreserve.gov", "ecb.europa.eu",
    "supremecourt.gov", "sci.gov.in", "judiciary.uk", "justice.gov"
}

_ACADEMIC_PEER_REVIEWED_DOMAINS = {
    "nature.com", "science.org", "sciencedirect.com", "cell.com", "thelancet.com", "nejm.org",
    "pnas.org", "ieee.org", "acm.org", "arxiv.org", "biorxiv.org", "medrxiv.org", "springer.com",
    "wiley.com", "oup.com", "cambridge.org", "frontiersin.org", "plos.org", "mdpi.com"
}

_REPUTABLE_SECONDARY_DOMAINS = {
    "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk", "afp.com", "thehindu.com", "indianexpress.com",
    "nytimes.com", "wsj.com", "washingtonpost.com", "theguardian.com", "economist.com", "ft.com",
    "bloomberg.com", "scientificamerican.com", "newscientist.com"
}


def classify_authority_class(url: str, domain: str | None = None) -> AuthorityClass:
    """Classify the authority tier of a source domain."""
    if not domain and url:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().removeprefix("www.")
        except Exception:
            domain = ""

    if not domain:
        return AuthorityClass.SECONDARY

    domain_lower = domain.lower().removeprefix("www.")

    for prim in _PRIMARY_INSTITUTIONAL_DOMAINS:
        if domain_lower == prim or domain_lower.endswith("." + prim) or domain_lower.endswith(".gov") or domain_lower.endswith(".gov.in"):
            return AuthorityClass.PRIMARY

    for acad in _ACADEMIC_PEER_REVIEWED_DOMAINS:
        if domain_lower == acad or domain_lower.endswith("." + acad) or domain_lower.endswith(".edu") or domain_lower.endswith(".ac.in") or domain_lower.endswith(".ac.uk"):
            return AuthorityClass.PRIMARY

    for rep in _REPUTABLE_SECONDARY_DOMAINS:
        if domain_lower == rep or domain_lower.endswith("." + rep):
            return AuthorityClass.SECONDARY

    return AuthorityClass.SECONDARY


def _extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower().removeprefix("www.") or "unknown"
    except Exception:
        return "unknown"


def _compute_ngram_overlap(text_a: str, text_b: str, n: int = 6) -> float:
    """Compute Jaccard similarity of n-grams between two text passages."""
    words_a = text_a.lower().split()
    words_b = text_b.lower().split()

    if len(words_a) < n or len(words_b) < n:
        return 0.0

    ngrams_a = {tuple(words_a[i : i + n]) for i in range(len(words_a) - n + 1)}
    ngrams_b = {tuple(words_b[i : i + n]) for i in range(len(words_b) - n + 1)}

    if not ngrams_a or not ngrams_b:
        return 0.0

    intersection = len(ngrams_a.intersection(ngrams_b))
    union = len(ngrams_a.union(ngrams_b))

    return intersection / max(1, union)


class ProvenanceClusterer:
    """Clusters evidence items into ProvenanceGroups and computes independence weights with authority escalation."""

    def cluster_evidence(
        self,
        evidence_items: list[Evidence],
        passages_by_id: dict[UUID, Passage],
        documents_by_id: dict[UUID, Document],
    ) -> tuple[list[ProvenanceGroup], list[Evidence]]:
        """Group evidence by domain and verbatim quotation overlap."""
        if not evidence_items:
            return [], []

        clusters: list[ProvenanceGroup] = []
        domain_clusters: dict[str, ProvenanceGroup] = {}
        updated_evidence: list[Evidence] = []

        # 1. First pass: Cluster by canonical URL domain
        for ev in evidence_items:
            passage = passages_by_id.get(ev.passage_id)
            doc = documents_by_id.get(passage.document_id) if passage else None
            domain = _extract_domain(doc.url) if doc else "unknown"

            # Re-classify authority
            auth = classify_authority_class(doc.url if doc else "", domain)
            if auth == AuthorityClass.PRIMARY:
                ev.source_quality_score = max(ev.source_quality_score, 0.95)

            if domain not in domain_clusters:
                group = ProvenanceGroup(
                    provenance_group_id=uuid4(),
                    root_source_id=doc.source_id if doc else None,
                    member_evidence_ids=[ev.evidence_id],
                    detection_method=ProvenanceDetectionMethod.URL_DOMAIN_CLUSTERING,
                    cluster_confidence=1.0,
                )
                domain_clusters[domain] = group
                clusters.append(group)
                ev.independence_score = 1.0
                ev.provenance_group_id = group.provenance_group_id
            else:
                group = domain_clusters[domain]
                group.member_evidence_ids.append(ev.evidence_id)
                ev.independence_score = 0.25
                ev.provenance_group_id = group.provenance_group_id

            updated_evidence.append(ev)

        # 2. Second pass: Cross-domain verbatim quotation overlap check
        for i, ev_a in enumerate(updated_evidence):
            p_a = passages_by_id.get(ev_a.passage_id)
            if not p_a:
                continue

            for j in range(i + 1, len(updated_evidence)):
                ev_b = updated_evidence[j]
                if ev_a.provenance_group_id == ev_b.provenance_group_id:
                    continue

                p_b = passages_by_id.get(ev_b.passage_id)
                if not p_b:
                    continue

                overlap = _compute_ngram_overlap(p_a.text, p_b.text, n=6)
                if overlap >= 0.60:
                    ev_b.independence_score = min(ev_b.independence_score, 0.20)

        return clusters, updated_evidence
