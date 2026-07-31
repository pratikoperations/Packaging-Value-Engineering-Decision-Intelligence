from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Iterable


class DatasetRole(str, Enum):
    EXISTING = "existing"
    PROPOSED = "proposed"


class ReviewStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CORRECTED = "corrected"


_ALLOWED_TRANSITIONS: dict[ReviewStatus, frozenset[ReviewStatus]] = {
    ReviewStatus.PENDING: frozenset(
        {ReviewStatus.ACCEPTED, ReviewStatus.REJECTED, ReviewStatus.CORRECTED}
    ),
    ReviewStatus.ACCEPTED: frozenset(),
    ReviewStatus.REJECTED: frozenset(),
    ReviewStatus.CORRECTED: frozenset(),
}


@dataclass(frozen=True)
class SpecificationCandidate:
    field_key: str
    original_value: object
    mandatory: bool = True
    status: ReviewStatus = ReviewStatus.PENDING
    corrected_value: object | None = None

    def __post_init__(self) -> None:
        if not self.field_key.strip():
            raise ValueError("field_key must not be empty")
        if self.status is ReviewStatus.CORRECTED and self.corrected_value is None:
            raise ValueError("corrected candidates require corrected_value")
        if self.status is not ReviewStatus.CORRECTED and self.corrected_value is not None:
            raise ValueError("corrected_value is only valid for corrected candidates")

    @property
    def final_value(self) -> object | None:
        if self.status is ReviewStatus.REJECTED:
            return None
        if self.status is ReviewStatus.CORRECTED:
            return self.corrected_value
        return self.original_value

    def transition(
        self,
        status: ReviewStatus,
        *,
        corrected_value: object | None = None,
    ) -> "SpecificationCandidate":
        if status not in _ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"invalid review transition: {self.status.value} -> {status.value}")
        if status is ReviewStatus.CORRECTED:
            if corrected_value is None:
                raise ValueError("corrected transition requires corrected_value")
            return replace(self, status=status, corrected_value=corrected_value)
        if corrected_value is not None:
            raise ValueError("corrected_value is only valid for corrected transition")
        return replace(self, status=status)


@dataclass(frozen=True)
class ExistingBaselineConfirmation:
    dataset_id: str
    confirmed: bool

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must not be empty")


@dataclass(frozen=True)
class SnapshotEligibilityResult:
    eligible: bool
    blockers: tuple[str, ...]


BLOCKER_EXISTING_BASELINE = "existing_baseline_not_confirmed"
BLOCKER_PROPOSED_DATASET = "proposed_dataset_missing"
BLOCKER_VALIDATION = "unresolved_validation_issue"
BLOCKER_PENDING_MANDATORY = "mandatory_candidate_pending"


def evaluate_snapshot_eligibility(
    *,
    existing_baseline: ExistingBaselineConfirmation | None,
    proposed_dataset_id: str | None,
    candidates: Iterable[SpecificationCandidate],
    has_unresolved_validation_issue: bool,
) -> SnapshotEligibilityResult:
    candidate_list = tuple(candidates)
    blockers: list[str] = []

    if existing_baseline is None or not existing_baseline.confirmed:
        blockers.append(BLOCKER_EXISTING_BASELINE)

    if proposed_dataset_id is None or not proposed_dataset_id.strip():
        blockers.append(BLOCKER_PROPOSED_DATASET)

    if has_unresolved_validation_issue:
        blockers.append(BLOCKER_VALIDATION)

    if any(
        candidate.mandatory and candidate.status is ReviewStatus.PENDING
        for candidate in candidate_list
    ):
        blockers.append(BLOCKER_PENDING_MANDATORY)

    return SnapshotEligibilityResult(
        eligible=not blockers,
        blockers=tuple(blockers),
    )
