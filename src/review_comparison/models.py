"""Governed review and comparison models for PVE 2.0 Build Group D.

No canonical mapping, persistence, provider connection, or decision logic is included.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Tuple

from src.ai_extraction import AmbiguityCode, ConfidenceBand, ExtractionCandidate
from src.document_intake import DocumentRole, SourceBlockType, SourceLocation


class ReviewError(ValueError):
    """Raised when a review action violates the controlled workflow."""


class ReviewState(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CORRECTED_CONFIRMED = "corrected_confirmed"
    INTENTIONALLY_OMITTED = "intentionally_omitted"
    REJECTED = "rejected"


class ComparisonStatus(str, Enum):
    UNCHANGED = "unchanged"
    CHANGED = "changed"
    EXISTING_MISSING = "existing_missing"
    PROPOSED_MISSING = "proposed_missing"
    BOTH_MISSING = "both_missing"
    UNIT_CONFLICT = "unit_conflict"
    NOT_COMPARABLE = "not_comparable"


@dataclass(frozen=True)
class SourceEvidence:
    block_id: str
    block_type: SourceBlockType
    excerpt: str
    location: SourceLocation


@dataclass(frozen=True)
class CandidateReview:
    candidate: ExtractionCandidate
    source: SourceEvidence
    state: ReviewState = ReviewState.PENDING
    corrected_value: Any = None
    corrected_unit: str | None = None
    reviewer_note: str | None = None

    @property
    def effective_value(self) -> Any:
        if self.state is ReviewState.CORRECTED_CONFIRMED:
            return self.corrected_value
        if self.state is ReviewState.CONFIRMED:
            return self.candidate.normalized_value
        return None

    @property
    def effective_unit(self) -> str | None:
        if self.state is ReviewState.CORRECTED_CONFIRMED:
            return self.corrected_unit
        if self.state is ReviewState.CONFIRMED:
            return self.candidate.unit
        return None

    @property
    def is_accepted(self) -> bool:
        return self.state in {ReviewState.CONFIRMED, ReviewState.CORRECTED_CONFIRMED}


@dataclass(frozen=True)
class FieldReviewGroup:
    field_name: str
    document_role: DocumentRole
    reviews: Tuple[CandidateReview, ...]
    resolved_candidate_index: int | None = None

    @property
    def has_multiple_candidates(self) -> bool:
        return len(self.reviews) > 1

    @property
    def selected_review(self) -> CandidateReview | None:
        if self.resolved_candidate_index is None:
            accepted = tuple(review for review in self.reviews if review.is_accepted)
            return accepted[0] if len(accepted) == 1 else None
        if not 0 <= self.resolved_candidate_index < len(self.reviews):
            return None
        return self.reviews[self.resolved_candidate_index]


@dataclass(frozen=True)
class FieldComparison:
    field_name: str
    existing: CandidateReview | None
    proposed: CandidateReview | None
    status: ComparisonStatus
    change: Any = None
    change_percent: float | None = None


@dataclass(frozen=True)
class ChangeSummary:
    total_fields: int
    changed: int
    unchanged: int
    existing_missing: int
    proposed_missing: int
    both_missing: int
    unit_conflicts: int
    not_comparable: int
    unresolved_fields: Tuple[str, ...]
