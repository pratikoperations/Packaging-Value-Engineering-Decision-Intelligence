from __future__ import annotations

from src.application.specification_review_service import (
    AssignedDataset,
    ReviewableField,
    SpecificationReviewError,
    SpecificationReviewService,
)
from src.persistence.specification_review_repository import (
    PersistedSpecificationReview,
    SpecificationReviewPersistenceError,
    SpecificationReviewRepository,
)


class PersistentSpecificationReviewService:
    """Transaction boundary around the pure E1.2 review service and E1.3 repository."""

    def __init__(
        self,
        review_service: SpecificationReviewService,
        repository: SpecificationReviewRepository,
    ) -> None:
        self.review_service = review_service
        self.repository = repository

    def initialize_and_save(
        self,
        *,
        existing: AssignedDataset,
        proposed: AssignedDataset,
        fields: tuple[ReviewableField, ...],
        actor_reference: str,
        action_reason: str | None = None,
    ) -> PersistedSpecificationReview:
        try:
            state = self.review_service.initialize_review(
                existing=existing,
                proposed=proposed,
                fields=fields,
            )
            return self.repository.create_initial(
                state,
                actor_reference=actor_reference,
                action_reason=action_reason,
            )
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error

    def confirm_and_save(
        self,
        review_id: str,
        *,
        dataset_id: str,
        actor_reference: str,
        action_reason: str | None = None,
    ) -> PersistedSpecificationReview:
        return self._apply_and_save(
            review_id,
            action_type="confirm_baseline",
            actor_reference=actor_reference,
            action_reason=action_reason,
            transition=lambda state: self.review_service.confirm_existing_baseline(
                state,
                dataset_id=dataset_id,
            ),
        )

    def accept_and_save(
        self,
        review_id: str,
        *,
        field_key: str,
        actor_reference: str,
        action_reason: str | None = None,
    ) -> PersistedSpecificationReview:
        return self._apply_and_save(
            review_id,
            action_type="accept",
            action_field_key=field_key,
            actor_reference=actor_reference,
            action_reason=action_reason,
            transition=lambda state: self.review_service.accept_candidate(
                state,
                field_key=field_key,
            ),
        )

    def reject_and_save(
        self,
        review_id: str,
        *,
        field_key: str,
        actor_reference: str,
        action_reason: str,
    ) -> PersistedSpecificationReview:
        return self._apply_and_save(
            review_id,
            action_type="reject",
            action_field_key=field_key,
            actor_reference=actor_reference,
            action_reason=action_reason,
            transition=lambda state: self.review_service.reject_candidate(
                state,
                field_key=field_key,
            ),
        )

    def correct_and_save(
        self,
        review_id: str,
        *,
        field_key: str,
        corrected_value: object,
        actor_reference: str,
        action_reason: str,
    ) -> PersistedSpecificationReview:
        return self._apply_and_save(
            review_id,
            action_type="correct",
            action_field_key=field_key,
            actor_reference=actor_reference,
            action_reason=action_reason,
            transition=lambda state: self.review_service.correct_candidate(
                state,
                field_key=field_key,
                corrected_value=corrected_value,
            ),
        )

    def load_latest(self, review_id: str, *, project_id: str | None = None) -> PersistedSpecificationReview:
        try:
            return self.repository.get_latest(review_id, project_id=project_id)
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error

    def list_history(self, review_id: str, *, project_id: str | None = None) -> list[PersistedSpecificationReview]:
        try:
            return self.repository.list_revisions(review_id, project_id=project_id)
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error

    def _apply_and_save(
        self,
        review_id: str,
        *,
        action_type: str,
        actor_reference: str,
        transition,
        action_field_key: str | None = None,
        action_reason: str | None = None,
    ) -> PersistedSpecificationReview:
        try:
            latest = self.repository.get_latest(review_id)
            state = transition(latest.state)
            return self.repository.append_revision(
                state,
                review_id=review_id,
                action_type=action_type,
                action_field_key=action_field_key,
                actor_reference=actor_reference,
                action_reason=action_reason,
            )
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error
