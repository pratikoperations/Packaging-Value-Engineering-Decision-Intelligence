from __future__ import annotations

from src.application.approved_specification_snapshot_service import (
    ApprovedSpecificationSnapshotError,
)
from src.domain.approved_specification import ApprovedSpecificationSnapshot
from src.persistence.approved_specification_repository import (
    ApprovedSpecificationPersistenceError,
    ApprovedSpecificationSnapshotRepository,
)


class ApprovedSpecificationReadModel:
    """Project-scoped, read-only approved specification boundary."""

    def __init__(self, repository: ApprovedSpecificationSnapshotRepository) -> None:
        self.repository = repository

    def get_snapshot(
        self, snapshot_id: str, *, project_id: str
    ) -> ApprovedSpecificationSnapshot:
        project_id = self._project(project_id)
        snapshot_id = self._required(snapshot_id, "snapshot_required", "Select a snapshot.")
        try:
            return self.repository.get(snapshot_id, project_id=project_id)
        except ApprovedSpecificationPersistenceError as error:
            raise ApprovedSpecificationSnapshotError(error.code, error.message) from error

    def get_snapshot_for_review(
        self, review_id: str, *, project_id: str
    ) -> ApprovedSpecificationSnapshot | None:
        project_id = self._project(project_id)
        review_id = self._required(review_id, "review_required", "Select a review.")
        try:
            return self.repository.get_for_review(review_id, project_id=project_id)
        except ApprovedSpecificationPersistenceError as error:
            raise ApprovedSpecificationSnapshotError(error.code, error.message) from error

    def list_snapshots_for_project(
        self, project_id: str
    ) -> list[ApprovedSpecificationSnapshot]:
        project_id = self._project(project_id)
        try:
            return self.repository.list_for_project(project_id)
        except ApprovedSpecificationPersistenceError as error:
            raise ApprovedSpecificationSnapshotError(error.code, error.message) from error

    @classmethod
    def _project(cls, project_id: str) -> str:
        return cls._required(
            project_id, "project_required", "Select a project before loading snapshots."
        )

    @staticmethod
    def _required(value: str, code: str, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ApprovedSpecificationSnapshotError(code, message)
        return normalized
