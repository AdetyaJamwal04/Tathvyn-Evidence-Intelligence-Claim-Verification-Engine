"""Canonical Enums and Taxonomies for VeriFact.

This module is the programmatic single source of truth for all categorical taxonomies,
strictly adhering to verifact_docs/00-canonical-enums.md.
"""

from enum import StrEnum

# ==============================================================================
# Verdict Enums
# ==============================================================================


class InternalVerdict(StrEnum):
    """Canonical internal verdict produced by the Verdict Engine."""

    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    UNVERIFIABLE = "UNVERIFIABLE"


class PublicVerdict(StrEnum):
    """User-facing public labels derived deterministically from InternalVerdict."""

    LIKELY_TRUE = "LIKELY TRUE"
    LIKELY_FALSE = "LIKELY FALSE"
    PARTIALLY_TRUE = "PARTIALLY TRUE"
    UNVERIFIED = "UNVERIFIED"
    UNVERIFIABLE = "UNVERIFIABLE"


class AtomicClaimVerdict(StrEnum):
    """Verification state for an individual atomic claim proposition."""

    SUPPORTED = "SUPPORTED"
    REFUTED = "REFUTED"
    CONFLICTED = "CONFLICTED"
    INSUFFICIENT = "INSUFFICIENT"
    UNVERIFIABLE = "UNVERIFIABLE"


# Deterministic mapping dictionary from internal to public verdict
INTERNAL_TO_PUBLIC_VERDICT: dict[InternalVerdict, PublicVerdict] = {
    InternalVerdict.SUPPORTED: PublicVerdict.LIKELY_TRUE,
    InternalVerdict.REFUTED: PublicVerdict.LIKELY_FALSE,
    InternalVerdict.PARTIALLY_SUPPORTED: PublicVerdict.PARTIALLY_TRUE,
    InternalVerdict.INSUFFICIENT_EVIDENCE: PublicVerdict.UNVERIFIED,
    InternalVerdict.UNVERIFIABLE: PublicVerdict.UNVERIFIABLE,
}


# ==============================================================================
# Evidence Enums
# ==============================================================================


class EvidenceRelationship(StrEnum):
    """Logical / empirical relationship between an evidence passage and an atomic claim."""

    SUPPORTS = "SUPPORTS"
    PARTIALLY_SUPPORTS = "PARTIALLY_SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    PARTIALLY_CONTRADICTS = "PARTIALLY_CONTRADICTS"
    QUALIFIES = "QUALIFIES"
    CONTEXTUALIZES = "CONTEXTUALIZES"
    NEUTRAL = "NEUTRAL"


class EvidenceLifecycle(StrEnum):
    """Lifecycle states of an evidence item within a verification session."""

    CANDIDATE = "CANDIDATE"
    ASSESSED = "ASSESSED"
    VALIDATED = "VALIDATED"
    AGGREGATED = "AGGREGATED"
    USED_IN_VERDICT = "USED_IN_VERDICT"


class EvidenceRejectionReason(StrEnum):
    """Explicit reason for discarding candidate passage evidence."""

    IRRELEVANT = "IRRELEVANT"
    LOW_QUALITY = "LOW_QUALITY"
    DUPLICATE = "DUPLICATE"
    DERIVATIVE = "DERIVATIVE"
    TEMPORALLY_INVALID = "TEMPORALLY_INVALID"
    ENTITY_MISMATCH = "ENTITY_MISMATCH"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    EXTRACTION_ERROR = "EXTRACTION_ERROR"
    UNSUPPORTED_LANGUAGE_EVIDENCE = "UNSUPPORTED_LANGUAGE_EVIDENCE"


# ==============================================================================
# Claim Enums
# ==============================================================================


class ClaimType(StrEnum):
    """Multi-label classification of claim semantic characteristics."""

    FACTUAL = "FACTUAL"
    NUMERICAL = "NUMERICAL"
    TEMPORAL = "TEMPORAL"
    COMPARATIVE = "COMPARATIVE"
    CAUSAL = "CAUSAL"
    ATTRIBUTION = "ATTRIBUTION"
    HISTORICAL = "HISTORICAL"
    PREDICTIVE = "PREDICTIVE"
    DEFINITIONAL = "DEFINITIONAL"
    LEGAL = "LEGAL"
    SCIENTIFIC = "SCIENTIFIC"
    POLITICAL = "POLITICAL"
    FINANCIAL = "FINANCIAL"
    MEDICAL = "MEDICAL"
    OPINION = "OPINION"
    NORMATIVE = "NORMATIVE"
    COMPOUND = "COMPOUND"


class ClaimVerifiability(StrEnum):
    """Feasibility of evaluating a proposition against objective evidence."""

    VERIFIABLE = "VERIFIABLE"
    PARTIALLY_VERIFIABLE = "PARTIALLY_VERIFIABLE"
    UNVERIFIABLE = "UNVERIFIABLE"
    SUBJECTIVE = "SUBJECTIVE"


class ClaimComplexity(StrEnum):
    """Estimated resource & reasoning complexity of a claim."""

    SIMPLE = "SIMPLE"
    MODERATE = "MODERATE"
    COMPLEX = "COMPLEX"
    HIGHLY_COMPLEX = "HIGHLY_COMPLEX"


class Materiality(StrEnum):
    """Impact of an atomic claim's truth value on its parent claim."""

    CRITICAL = "CRITICAL"
    MATERIAL = "MATERIAL"
    CONTEXTUAL = "CONTEXTUAL"


# ==============================================================================
# Source Enums
# ==============================================================================


class SourceType(StrEnum):
    """Organizational / structural category of an information publisher."""

    GOVERNMENT = "GOVERNMENT"
    INTERNATIONAL_ORGANIZATION = "INTERNATIONAL_ORGANIZATION"
    SCIENTIFIC_JOURNAL = "SCIENTIFIC_JOURNAL"
    UNIVERSITY = "UNIVERSITY"
    NEWS_WIRE = "NEWS_WIRE"
    NEWS_ORGANIZATION = "NEWS_ORGANIZATION"
    COMPANY_OFFICIAL = "COMPANY_OFFICIAL"
    REGULATORY_FILING = "REGULATORY_FILING"
    LEGAL_DOCUMENT = "LEGAL_DOCUMENT"
    REFERENCE_WORK = "REFERENCE_WORK"
    BLOG = "BLOG"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    FORUM = "FORUM"
    WIKI = "WIKI"
    AGGREGATOR = "AGGREGATOR"
    UNKNOWN = "UNKNOWN"


class AuthorityClass(StrEnum):
    """Proximity of a source to the underlying fact, decree, or measurement."""

    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    TERTIARY = "TERTIARY"
    DERIVATIVE = "DERIVATIVE"
    UNKNOWN = "UNKNOWN"


# ==============================================================================
# Research Orchestrator Enums
# ==============================================================================


class VerificationMode(StrEnum):
    """Product verification depth / latency profiles."""

    FAST = "FAST"
    STANDARD = "STANDARD"
    DEEP = "DEEP"


ResearchDepth = VerificationMode


class BudgetUnit(StrEnum):
    """Units of resource expenditure."""

    SEARCH_QUERIES = "SEARCH_QUERIES"
    TOKENS = "TOKENS"
    SECONDS = "SECONDS"
    USD = "USD"


class ResearchLoopDecision(StrEnum):
    """Adaptive action chosen by the research loop controller."""

    TERMINATE = "TERMINATE"
    REFINE_SEARCH = "REFINE_SEARCH"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"


class ResearchObjective(StrEnum):
    """Explicit intent for a retrieval or extraction task."""

    FIND_SUPPORT = "FIND_SUPPORT"
    FIND_CONTRADICTION = "FIND_CONTRADICTION"
    FIND_PRIMARY_SOURCE = "FIND_PRIMARY_SOURCE"
    FIND_ORIGINAL_REPORT = "FIND_ORIGINAL_REPORT"
    RESOLVE_ENTITY = "RESOLVE_ENTITY"
    RESOLVE_DATE = "RESOLVE_DATE"
    VERIFY_NUMBER = "VERIFY_NUMBER"
    VERIFY_QUOTE = "VERIFY_QUOTE"
    VERIFY_COMPARISON = "VERIFY_COMPARISON"
    INVESTIGATE_CONFLICT = "INVESTIGATE_CONFLICT"
    FIND_CONTEXT = "FIND_CONTEXT"


class ResearchActionType(StrEnum):
    """Discrete executable actions selectable by the Research Orchestrator."""

    SEARCH_SUPPORT = "SEARCH_SUPPORT"
    SEARCH_CONTRADICTION = "SEARCH_CONTRADICTION"
    SEARCH_PRIMARY = "SEARCH_PRIMARY"
    SEARCH_TEMPORAL = "SEARCH_TEMPORAL"
    SEARCH_NUMERICAL = "SEARCH_NUMERICAL"
    SEARCH_ENTITY = "SEARCH_ENTITY"
    FETCH_DOCUMENT = "FETCH_DOCUMENT"
    FOLLOW_CITATION = "FOLLOW_CITATION"
    RESOLVE_CONFLICT = "RESOLVE_CONFLICT"
    STOP = "STOP"


class ResearchStopReason(StrEnum):
    """Explicit justification for concluding adaptive research."""

    SUFFICIENT_EVIDENCE = "SUFFICIENT_EVIDENCE"
    STRONG_CONTRADICTION = "STRONG_CONTRADICTION"
    RESOLVED_CONFLICT = "RESOLVED_CONFLICT"
    UNVERIFIABLE = "UNVERIFIABLE"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    LOW_EXPECTED_VALUE = "LOW_EXPECTED_VALUE"
    TIMEOUT = "TIMEOUT"
    SYSTEM_LIMIT = "SYSTEM_LIMIT"
    NO_RELEVANT_SOURCES = "NO_RELEVANT_SOURCES"


class ResearchStateStatus(StrEnum):
    """Status lifecycle of a verification research session."""

    RECEIVED = "RECEIVED"
    ANALYZING = "ANALYZING"
    PLANNED = "PLANNED"
    RESEARCHING = "RESEARCHING"
    EVALUATING = "EVALUATING"
    CONFLICT_RESOLUTION = "CONFLICT_RESOLUTION"
    RECOVERY = "RECOVERY"
    READY_FOR_VERDICT = "READY_FOR_VERDICT"
    VERDICT = "VERDICT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"


# ==============================================================================
# Conflict Enums
# ==============================================================================


class ConflictType(StrEnum):
    """Nature of disagreement between evidence items."""

    DIRECT_CONTRADICTION = "DIRECT_CONTRADICTION"
    TEMPORAL_CONFLICT = "TEMPORAL_CONFLICT"
    DEFINITION_CONFLICT = "DEFINITION_CONFLICT"
    NUMERICAL_CONFLICT = "NUMERICAL_CONFLICT"
    ENTITY_CONFLICT = "ENTITY_CONFLICT"
    METHODOLOGICAL_CONFLICT = "METHODOLOGICAL_CONFLICT"
    SOURCE_CONFLICT = "SOURCE_CONFLICT"


class ConflictSeverity(StrEnum):
    """Material severity of an evidence conflict."""

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


class ConflictResolutionStatus(StrEnum):
    """Status of conflict investigation."""

    UNRESOLVED = "UNRESOLVED"
    RESOLVED_TEMPORAL = "RESOLVED_TEMPORAL"
    RESOLVED_DEFINITION = "RESOLVED_DEFINITION"
    RESOLVED_METHODOLOGY = "RESOLVED_METHODOLOGY"
    RESOLVED_ENTITY = "RESOLVED_ENTITY"
    RESOLVED_SCOPE = "RESOLVED_SCOPE"
    UNRESOLVABLE = "UNRESOLVABLE"


# ==============================================================================
# Provenance Enums
# ==============================================================================


class ProvenanceRelationship(StrEnum):
    """Derivation edge relationship between documents."""

    DERIVED_FROM = "DERIVED_FROM"
    CITES = "CITES"
    QUOTES = "QUOTES"
    DUPLICATES = "DUPLICATES"
    QUALIFIES = "QUALIFIES"


class ProvenanceDetectionMethod(StrEnum):
    """Method used to establish provenance clustering."""

    URL_DOMAIN_CLUSTERING = "URL_DOMAIN_CLUSTERING"
    EXACT_QUOTATION_OVERLAP = "EXACT_QUOTATION_OVERLAP"
    CITATION_GRAPH = "CITATION_GRAPH"
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
