"""PVE 2.0 Build Group D review and comparison boundary."""

from .comparison import build_change_summary, compare_fields
from .models import (
    CandidateReview,
    ChangeSummary,
    ComparisonStatus,
    FieldComparison,
    FieldReviewGroup,
    ReviewError,
    ReviewState,
    SourceEvidence,
)
from .review_service import (
    build_candidate_reviews,
    confirm,
    correct_and_confirm,
    group_reviews,
    intentionally_omit,
    reject,
    resolve_candidate,
    unresolved_reason,
)

__all__ = [
    "CandidateReview",
    "ChangeSummary",
    "ComparisonStatus",
    "FieldComparison",
    "FieldReviewGroup",
    "ReviewError",
    "ReviewState",
    "SourceEvidence",
    "build_candidate_reviews",
    "build_change_summary",
    "compare_fields",
    "confirm",
    "correct_and_confirm",
    "group_reviews",
    "intentionally_omit",
    "reject",
    "resolve_candidate",
    "unresolved_reason",
]
