from __future__ import annotations

from dataclasses import dataclass

from src.application.specification_review_service import SpecificationReviewError
from src.domain.specification_review import ReviewStatus
from src.persistence.database import Database
from src.persistence.specification_review_repository import (
    PersistedSpecificationReview,
    SpecificationReviewPersistenceError,
    SpecificationReviewRepository,
)


@dataclass(frozen=True)
class SpecificationReviewSummary:
    review_id: str
    project_id: str
    existing_dataset_id: str
    proposed_dataset_id: str
    latest_revision_number: int
    latest_action_type: str
    latest_actor_reference: str
    latest_created_at: str
    eligible: bool
    pending_candidate_count: int
    terminal_candidate_count: int


class SpecificationReviewReadModel:
    """Project-scoped, read-only discovery and history boundary for E1.5."""

    def __init__(self, database: Database) -> None:
        self.database = database
        self.repository = SpecificationReviewRepository(database)

    def list_reviews_for_project(self, project_id: str) -> list[SpecificationReviewSummary]:
        project_id = str(project_id).strip()
        if not project_id:
            raise SpecificationReviewError("project_required", "Select a project before loading reviews.")
        with self.database.connect() as connection:
            project = connection.execute(
                "SELECT project_id FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise SpecificationReviewError("unknown_project", "The selected project does not exist.")
            rows = connection.execute(
                """
                SELECT review_id
                FROM specification_review_revisions
                WHERE project_id = ?
                GROUP BY review_id
                ORDER BY MAX(created_at) DESC, review_id ASC
                """,
                (project_id,),
            ).fetchall()
        summaries: list[SpecificationReviewSummary] = []
        try:
            for row in rows:
                latest = self.repository.get_latest(str(row["review_id"]), project_id=project_id)
                pending = sum(
                    item.candidate.status is ReviewStatus.PENDING
                    for item in latest.state.comparisons
                )
                summaries.append(
                    SpecificationReviewSummary(
                        review_id=latest.review_id,
                        project_id=latest.state.project_id,
                        existing_dataset_id=latest.state.existing_dataset_id,
                        proposed_dataset_id=latest.state.proposed_dataset_id,
                        latest_revision_number=latest.revision_number,
                        latest_action_type=latest.action_type,
                        latest_actor_reference=latest.actor_reference,
                        latest_created_at=latest.created_at,
                        eligible=bool(latest.state.eligibility and latest.state.eligibility.eligible),
                        pending_candidate_count=pending,
                        terminal_candidate_count=len(latest.state.comparisons) - pending,
                    )
                )
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error
        return summaries

    def load_latest(self, review_id: str, *, project_id: str) -> PersistedSpecificationReview:
        try:
            return self.repository.get_latest(review_id, project_id=project_id)
        except KeyError as error:
            raise SpecificationReviewError("unknown_review", "The selected review no longer exists.") from error
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error

    def list_history(self, review_id: str, *, project_id: str) -> list[PersistedSpecificationReview]:
        try:
            history = self.repository.list_revisions(review_id, project_id=project_id)
        except SpecificationReviewPersistenceError as error:
            raise SpecificationReviewError(error.code, error.message) from error
        if not history:
            raise SpecificationReviewError("unknown_review", "The selected review no longer exists.")
        expected = list(range(1, len(history) + 1))
        if [item.revision_number for item in history] != expected:
            raise SpecificationReviewError("invalid_history", "Review history failed sequential integrity validation.")
        for index, item in enumerate(history):
            expected_parent = None if index == 0 else history[index - 1].review_revision_id
            if item.parent_revision_id != expected_parent:
                raise SpecificationReviewError("invalid_history", "Review history failed lineage integrity validation.")
        return history
