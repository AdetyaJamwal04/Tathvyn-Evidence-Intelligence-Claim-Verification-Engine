"""
Targeted primary-source query formulator with entity authority mapping and causal bridge generation.
"""

from __future__ import annotations

import re
from uuid import UUID

from tathvyn.claims.entity_extractor import extract_named_entities
from tathvyn.claims.temporal_extractor import extract_temporal_constraints
from tathvyn.common.models.claim import AtomicClaim
from tathvyn.common.models.conflict import Conflict


_ENTITY_PRIMARY_DOMAIN_MAP = {
    # Space & Science Agencies
    "chandrayaan": "isro.gov.in",
    "isro": "isro.gov.in",
    "pragyan": "isro.gov.in",
    "vikram": "isro.gov.in",
    "aditya-l1": "isro.gov.in",
    "gaganyaan": "isro.gov.in",
    "nasa": "nasa.gov",
    "perseverance": "jpl.nasa.gov",
    "curiosity": "jpl.nasa.gov",
    "jwst": "nasa.gov",
    "webb": "nasa.gov",
    "artemis": "nasa.gov",
    "esa": "esa.int",
    "cnsa": "cnsa.gov.cn",
    
    # Government & Policy
    "india": "pib.gov.in",
    "indian government": "pib.gov.in",
    "parliament": "sansad.in",
    "rbi": "rbi.org.in",
    "white house": "whitehouse.gov",
    "us government": "gov",
    "federal reserve": "federalreserve.gov",
    
    # Health & Science
    "who": "who.int",
    "cdc": "cdc.gov",
    "fda": "fda.gov",
    "nih": "nih.gov"
}


class QueryFormulator:
    """Formulates and optimizes search queries across research iterations with primary authority escalation."""

    def formulate_initial_queries(
        self,
        atomic_claims: list[AtomicClaim],
        max_queries: int = 5,
    ) -> list[tuple[UUID, str]]:
        """Generate first-pass search queries for decomposed atomic propositions."""
        queries: list[tuple[UUID, str]] = []
        for ac in atomic_claims[:max_queries]:
            queries.append((ac.atomic_claim_id, ac.text.strip()))
        return queries

    def formulate_refinement_queries(
        self,
        unresolved_atomic_claims: list[AtomicClaim],
        past_queries: list[str],
        max_queries: int = 3,
    ) -> list[tuple[UUID, str]]:
        """Generate targeted sub-queries for unverified or low-coverage atomic claims with primary domain escalation."""
        refined_queries: list[tuple[UUID, str]] = []
        seen = {q.lower() for q in past_queries}

        for ac in unresolved_atomic_claims:
            if len(refined_queries) >= max_queries:
                break

            text_lower = ac.text.lower()
            cleaned = re.sub(r'[^\w\s\-\.\$₹€£%]', '', ac.text)

            # 1. Targeted primary institutional domain search
            for entity_keyword, primary_domain in _ENTITY_PRIMARY_DOMAIN_MAP.items():
                if entity_keyword in text_lower:
                    keywords = [w for w in cleaned.split() if len(w) > 2 and w.lower() not in ("the", "and", "that", "was", "has", "during", "its")]
                    primary_q = f"{' '.join(keywords[:6])} site:{primary_domain}"
                    if primary_q.lower() not in seen:
                        refined_queries.append((ac.atomic_claim_id, primary_q))
                        seen.add(primary_q.lower())
                    break

            if len(refined_queries) >= max_queries:
                break

            # 2. Causal bridge queries
            if any(conn in text_lower for conn in ("prove", "proves", "proving", "because", "due to", "caused")):
                causal_keywords = [w for w in cleaned.split() if w.lower() not in ("the", "that", "this", "during", "about", "only")]
                causal_q = f"{' '.join(causal_keywords[:6])} scientific data"
                if causal_q.lower() not in seen:
                    refined_queries.append((ac.atomic_claim_id, causal_q))
                    seen.add(causal_q.lower())

            if len(refined_queries) >= max_queries:
                break

            entities = extract_named_entities(ac.text)
            temporals = extract_temporal_constraints(ac.text)

            entity_str = " ".join(e["text"] for e in entities[:3])
            temp_str = " ".join(str(t.get("year", "")) for t in temporals if "year" in t)

            candidate_query = f"{entity_str} {temp_str} official documentation report".strip()
            if not candidate_query or candidate_query.lower() in seen:
                candidate_query = f"{ac.text} primary sources official records"

            if candidate_query.lower() not in seen:
                refined_queries.append((ac.atomic_claim_id, candidate_query))
                seen.add(candidate_query.lower())

        return refined_queries

    def formulate_conflict_resolution_queries(
        self,
        conflicts: list[Conflict],
        atomic_claims_by_id: dict[UUID, AtomicClaim],
        past_queries: list[str],
        max_queries: int = 2,
    ) -> list[tuple[UUID, str]]:
        """Generate authoritative primary-source queries specifically targeting detected contradictions."""
        conflict_queries: list[tuple[UUID, str]] = []
        seen = {q.lower() for q in past_queries}

        for conf in conflicts:
            if len(conflict_queries) >= max_queries:
                break

            ac = atomic_claims_by_id.get(conf.atomic_claim_id)
            if not ac:
                continue

            query = f"{ac.text} official archives government statement factual record"
            if query.lower() not in seen:
                conflict_queries.append((ac.atomic_claim_id, query))
                seen.add(query.lower())

        return conflict_queries
