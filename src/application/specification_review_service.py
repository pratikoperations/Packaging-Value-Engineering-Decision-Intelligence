from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping, Sequence

from src.domain.specification_review import (
    DatasetRole,
    ExistingBaselineConfirmation,
    ReviewStatus,
    SnapshotEligibilityResult,
    SpecificationCandidate,
    evaluate_snapshot_eligibility,
)


class SpecificationReviewError(ValueError):
    """Presentation-safe application error for governed specification review."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ReviewableField:
    field_key: str
    path: tuple[str, ...]
    mandatory: bool = True

    def __post_init__(self) -> None:
        if not self.field_key.strip():
            raise ValueError("field_key must not be empty")
        if not self.path or any(not part.strip() for part in self.path):
            raise ValueError("path must contain non-empty segments")


@dataclass(frozen=True)
class AssignedDataset:
    dataset_id: str
    project_id: str
    role: DatasetRole
    canonical_data: Mapping[str, object]
    validation_status: str = "valid"

    def __post_init__(self) -> None:
        if not self.dataset_id.strip():
            raise ValueError("dataset_id must not be empty")
        if not self.project_id.strip():
            raise ValueError("project_id must not be empty")


@dataclass(frozen=True)
class SpecificationComparison:
    field_key: str
    existing_value: object
    candidate: SpecificationCandidate


@dataclass(frozen=True)
class SpecificationReviewState:
    project_id: str
    existing_dataset_id: str
    proposed_dataset_id: str
    comparisons: tuple[SpecificationComparison, ...]
    existing_baseline: ExistingBaselineConfirmation | None = None
    has_unresolved_validation_issue: bool = False
    eligibility: SnapshotEligibilityResult | None = None


class SpecificationReviewService:
    """Orchestrate Existing-vs-Proposed review without persistence or UI side effects."""

    def initialize_review(
        self,
        *,
        existing: AssignedDataset,
        proposed: AssignedDataset,
        fields: Sequence[ReviewableField],
    ) -> SpecificationReviewState:
        self._validate_dataset_pair(existing, proposed)
        self._validate_registry(fields)

        comparisons: list[SpecificationComparison] = []
        for field in fields:
            existing_value = self._read_path(existing.canonical_data, field.path)
            proposed_value = self._read_path(proposed.canonical_data, field.path)
            if existing_value == proposed_value:
                continue
            comparisons.append(
                SpecificationComparison(
                    field_key=field.field_key,
                    existing_value=existing_value,
                    candidate=SpecificationCandidate(
                        field_key=field.field_key,
                        original_value=proposed_value,
                        mandatory=field.mandatory,
                    ),
                )
            )

        state = SpecificationReviewState(
            project_id=existing.project_id,
            existing_dataset_id=existing.dataset_id,
            proposed_dataset_id=proposed.dataset_id,
            comparisons=tuple(comparisons),
        )
        return self._with_eligibility(state)

    def confirm_existing_baseline(
        self,
        state: SpecificationReviewState,
        *,
        dataset_id: str,
    ) -> SpecificationReviewState:
        if dataset_id != state.existing_dataset_id:
            raise SpecificationReviewError(
                "invalid_existing_baseline",
                "Only the assigned Existing dataset can be confirmed as the baseline.",
            )
        return self._with_eligibility(
            replace(
                state,
                existing_baseline=ExistingBaselineConfirmation(
                    dataset_id=dataset_id,
                    confirmed=True,
                ),
            )
        )

    def accept_candidate(
        self,
        state: SpecificationReviewState,
        *,
        field_key: str,
    ) -> SpecificationReviewState:
        return self._transition(state, field_key, ReviewStatus.ACCEPTED)

    def reject_candidate(
        self,
        state: SpecificationReviewState,
        *,
        field_key: str,
    ) -> SpecificationReviewState:
        return self._transition(state, field_key, ReviewStatus.REJECTED)

    def correct_candidate(
        self,
        state: SpecificationReviewState,
        *,
        field_key: str,
        corrected_value: object,
    ) -> SpecificationReviewState:
        return self._transition(
            state,
            field_key,
            ReviewStatus.CORRECTED,
            corrected_value=corrected_value,
        )

    def evaluate_eligibility(
        self,
        state: SpecificationReviewState,
    ) -> SnapshotEligibilityResult:
        return evaluate_snapshot_eligibility(
            existing_baseline=state.existing_baseline,
            proposed_dataset_id=state.proposed_dataset_id,
            candidates=(comparison.candidate for comparison in state.comparisons),
            has_unresolved_validation_issue=state.has_unresolved_validation_issue,
        )

    def _transition(
        self,
        state: SpecificationReviewState,
        field_key: str,
        status: ReviewStatus,
        *,
        corrected_value: object | None = None,
    ) -> SpecificationReviewState:
        found = False
        updated: list[SpecificationComparison] = []
        for comparison in state.comparisons:
            if comparison.field_key != field_key:
                updated.append(comparison)
                continue
            found = True
            try:
                candidate = comparison.candidate.transition(
                    status,
                    corrected_value=corrected_value,
                )
            except ValueError as error:
                raise SpecificationReviewError(
                    "invalid_review_transition",
                    "The requested review action is not allowed for this candidate.",
                ) from error
            updated.append(replace(comparison, candidate=candidate))

        if not found:
            raise SpecificationReviewError(
                "unknown_review_field",
                "The requested specification field is not part of this review.",
            )
        return self._with_eligibility(replace(state, comparisons=tuple(updated)))

    def _with_eligibility(self, state: SpecificationReviewState) -> SpecificationReviewState:
        return replace(state, eligibility=self.evaluate_eligibility(state))

    @staticmethod
    def _validate_dataset_pair(existing: AssignedDataset, proposed: AssignedDataset) -> None:
        if existing.role is not DatasetRole.EXISTING:
            raise SpecificationReviewError(
                "existing_role_required",
                "The Existing dataset must be assigned the Existing role.",
            )
        if proposed.role is not DatasetRole.PROPOSED:
            raise SpecificationReviewError(
                "proposed_role_required",
                "The Proposed dataset must be assigned the Proposed role.",
            )
        if existing.dataset_id == proposed.dataset_id:
            raise SpecificationReviewError(
                "distinct_datasets_required",
                "Existing and Proposed roles must use distinct datasets.",
            )
        if existing.project_id != proposed.project_id:
            raise SpecificationReviewError(
                "project_mismatch",
                "Existing and Proposed datasets must belong to the same project.",
            )
        if existing.validation_status != "valid" or proposed.validation_status != "valid":
            raise SpecificationReviewError(
                "valid_datasets_required",
                "Only valid datasets can enter specification review.",
            )

    @staticmethod
    def _validate_registry(fields: Sequence[ReviewableField]) -> None:
        keys = [field.field_key for field in fields]
        if len(keys) != len(set(keys)):
            raise SpecificationReviewError(
                "duplicate_review_field",
                "Reviewable field keys must be unique.",
            )

    @staticmethod
    def _read_path(data: Mapping[str, object], path: tuple[str, ...]) -> object:
        current: object = data
        for part in path:
            if not isinstance(current, Mapping) or part not in current:
                return None
            current = current[part]
        return current
