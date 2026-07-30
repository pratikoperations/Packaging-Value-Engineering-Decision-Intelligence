from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any

from src.application.specification_review_service import (
    SpecificationComparison,
    SpecificationReviewState,
)
from src.domain.specification_review import (
    ExistingBaselineConfirmation,
    ReviewStatus,
    SnapshotEligibilityResult,
    SpecificationCandidate,
    evaluate_snapshot_eligibility,
)
from src.persistence._utils import canonical_json, content_hash, new_id
from src.persistence.database import Database
from src.persistence.specification_review_migration import initialize_specification_review_schema


class SpecificationReviewPersistenceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class PersistedSpecificationReview:
    review_revision_id: str
    review_id: str
    revision_number: int
    state: SpecificationReviewState
    action_type: str
    action_field_key: str | None
    actor_reference: str
    action_reason: str | None
    parent_revision_id: str | None
    content_hash: str
    created_at: str


class SpecificationReviewRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        initialize_specification_review_schema(database)

    def create_initial(
        self,
        state: SpecificationReviewState,
        *,
        actor_reference: str,
        review_id: str | None = None,
        review_revision_id: str | None = None,
        action_reason: str | None = None,
    ) -> PersistedSpecificationReview:
        return self._append(
            state,
            review_id=review_id or new_id("review"),
            review_revision_id=review_revision_id or new_id("review-revision"),
            revision_number=1,
            action_type="initialize",
            action_field_key=None,
            actor_reference=actor_reference,
            action_reason=action_reason,
            parent_revision_id=None,
        )

    def append_revision(
        self,
        state: SpecificationReviewState,
        *,
        review_id: str,
        action_type: str,
        actor_reference: str,
        action_field_key: str | None = None,
        action_reason: str | None = None,
        review_revision_id: str | None = None,
    ) -> PersistedSpecificationReview:
        latest = self.get_latest(review_id, project_id=state.project_id)
        return self._append(
            state,
            review_id=review_id,
            review_revision_id=review_revision_id or new_id("review-revision"),
            revision_number=latest.revision_number + 1,
            action_type=action_type,
            action_field_key=action_field_key,
            actor_reference=actor_reference,
            action_reason=action_reason,
            parent_revision_id=latest.review_revision_id,
        )

    def get_revision(self, review_revision_id: str, *, project_id: str | None = None) -> PersistedSpecificationReview:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM specification_review_revisions WHERE review_revision_id = ?",
                (review_revision_id,),
            ).fetchone()
        if row is None:
            raise KeyError(review_revision_id)
        record = self._decode(dict(row))
        if project_id is not None and record.state.project_id != project_id:
            raise SpecificationReviewPersistenceError("project_scope_violation", "Review belongs to a different project.")
        return record

    def get_latest(self, review_id: str, *, project_id: str | None = None) -> PersistedSpecificationReview:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM specification_review_revisions WHERE review_id = ? ORDER BY revision_number DESC LIMIT 1",
                (review_id,),
            ).fetchone()
        if row is None:
            raise KeyError(review_id)
        record = self._decode(dict(row))
        if project_id is not None and record.state.project_id != project_id:
            raise SpecificationReviewPersistenceError("project_scope_violation", "Review belongs to a different project.")
        return record

    def list_revisions(self, review_id: str, *, project_id: str | None = None) -> list[PersistedSpecificationReview]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM specification_review_revisions WHERE review_id = ? ORDER BY revision_number",
                (review_id,),
            ).fetchall()
        records = [self._decode(dict(row)) for row in rows]
        if project_id is not None and any(record.state.project_id != project_id for record in records):
            raise SpecificationReviewPersistenceError("project_scope_violation", "Review belongs to a different project.")
        return records

    def update(self, review_revision_id: str, **changes: Any) -> None:
        raise SpecificationReviewPersistenceError("immutable_review", "Specification review revisions cannot be updated.")

    def delete(self, review_revision_id: str) -> None:
        raise SpecificationReviewPersistenceError("immutable_review", "Specification review revisions cannot be deleted.")

    def _append(self, state: SpecificationReviewState, **metadata: Any) -> PersistedSpecificationReview:
        actor_reference = str(metadata["actor_reference"]).strip()
        action_type = str(metadata["action_type"])
        action_reason = metadata.get("action_reason")
        if not actor_reference:
            raise SpecificationReviewPersistenceError("actor_required", "A non-empty actor reference is required.")
        if action_type in {"reject", "correct"} and not str(action_reason or "").strip():
            raise SpecificationReviewPersistenceError("reason_required", "Reject and Correct actions require a reason.")
        eligibility = evaluate_snapshot_eligibility(
            existing_baseline=state.existing_baseline,
            proposed_dataset_id=state.proposed_dataset_id,
            candidates=(item.candidate for item in state.comparisons),
            has_unresolved_validation_issue=state.has_unresolved_validation_issue,
        )
        if state.eligibility is not None and state.eligibility != eligibility:
            raise SpecificationReviewPersistenceError("eligibility_mismatch", "Review eligibility is inconsistent with domain rules.")
        state = SpecificationReviewState(
            project_id=state.project_id,
            existing_dataset_id=state.existing_dataset_id,
            proposed_dataset_id=state.proposed_dataset_id,
            comparisons=state.comparisons,
            existing_baseline=state.existing_baseline,
            has_unresolved_validation_issue=state.has_unresolved_validation_issue,
            eligibility=eligibility,
        )
        payload = self._state_payload(state)
        digest_payload = {**payload, **{k: metadata.get(k) for k in ("review_id", "revision_number", "action_type", "action_field_key", "actor_reference", "action_reason", "parent_revision_id")}}
        digest = content_hash(digest_payload)
        try:
            with self.database.transaction() as connection:
                self._validate_lineage(connection, state, metadata)
                connection.execute(
                    """INSERT INTO specification_review_revisions(
                    review_revision_id, review_id, revision_number, state_schema_version, project_id,
                    existing_dataset_id, proposed_dataset_id, existing_baseline_confirmed,
                    existing_baseline_dataset_id, comparisons_json, has_unresolved_validation_issue,
                    eligibility_json, action_type, action_field_key, actor_reference, action_reason,
                    parent_revision_id, content_hash) VALUES (?, ?, ?, '1', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        metadata["review_revision_id"], metadata["review_id"], metadata["revision_number"],
                        state.project_id, state.existing_dataset_id, state.proposed_dataset_id,
                        int(bool(state.existing_baseline and state.existing_baseline.confirmed)),
                        state.existing_baseline.dataset_id if state.existing_baseline else None,
                        canonical_json(payload["comparisons"]), int(state.has_unresolved_validation_issue),
                        canonical_json(payload["eligibility"]), action_type, metadata.get("action_field_key"),
                        actor_reference, action_reason, metadata.get("parent_revision_id"), digest,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise SpecificationReviewPersistenceError("review_integrity_error", "The review revision could not be persisted safely.") from error
        return self.get_revision(metadata["review_revision_id"], project_id=state.project_id)

    @staticmethod
    def _validate_lineage(connection: sqlite3.Connection, state: SpecificationReviewState, metadata: dict[str, Any]) -> None:
        project = connection.execute("SELECT archived_at FROM projects WHERE project_id = ?", (state.project_id,)).fetchone()
        if project is None:
            raise SpecificationReviewPersistenceError("unknown_project", "The project does not exist.")
        if project["archived_at"] is not None:
            raise SpecificationReviewPersistenceError("archived_project", "Archived projects are read-only.")
        rows = connection.execute(
            "SELECT dataset_id, project_id FROM project_datasets WHERE dataset_id IN (?, ?)",
            (state.existing_dataset_id, state.proposed_dataset_id),
        ).fetchall()
        if len(rows) != 2 or any(row["project_id"] != state.project_id for row in rows):
            raise SpecificationReviewPersistenceError("invalid_dataset_lineage", "Review datasets must exist in the same project.")
        parent_id = metadata.get("parent_revision_id")
        if parent_id:
            parent = connection.execute("SELECT * FROM specification_review_revisions WHERE review_revision_id = ?", (parent_id,)).fetchone()
            if parent is None or parent["review_id"] != metadata["review_id"]:
                raise SpecificationReviewPersistenceError("invalid_parent_revision", "Parent revision does not belong to this review.")
            if parent["project_id"] != state.project_id or parent["existing_dataset_id"] != state.existing_dataset_id or parent["proposed_dataset_id"] != state.proposed_dataset_id:
                raise SpecificationReviewPersistenceError("lineage_changed", "Project and dataset lineage cannot change across revisions.")

    @staticmethod
    def _state_payload(state: SpecificationReviewState) -> dict[str, Any]:
        return {
            "comparisons": [
                {"field_key": item.field_key, "existing_value": item.existing_value,
                 "candidate": {"field_key": item.candidate.field_key, "original_value": item.candidate.original_value,
                 "mandatory": item.candidate.mandatory, "status": item.candidate.status.value,
                 "corrected_value": item.candidate.corrected_value}}
                for item in state.comparisons
            ],
            "eligibility": {"eligible": bool(state.eligibility and state.eligibility.eligible), "blockers": list(state.eligibility.blockers if state.eligibility else ())},
        }

    @staticmethod
    def _decode(row: dict[str, Any]) -> PersistedSpecificationReview:
        comparisons_data = json.loads(row["comparisons_json"])
        comparisons = tuple(
            SpecificationComparison(
                field_key=item["field_key"], existing_value=item["existing_value"],
                candidate=SpecificationCandidate(
                    field_key=item["candidate"]["field_key"], original_value=item["candidate"]["original_value"],
                    mandatory=bool(item["candidate"]["mandatory"]), status=ReviewStatus(item["candidate"]["status"]),
                    corrected_value=item["candidate"]["corrected_value"],
                ),
            ) for item in comparisons_data
        )
        baseline = None
        if row["existing_baseline_dataset_id"] is not None:
            baseline = ExistingBaselineConfirmation(dataset_id=row["existing_baseline_dataset_id"], confirmed=bool(row["existing_baseline_confirmed"]))
        stored = json.loads(row["eligibility_json"])
        eligibility = evaluate_snapshot_eligibility(
            existing_baseline=baseline, proposed_dataset_id=row["proposed_dataset_id"],
            candidates=(item.candidate for item in comparisons),
            has_unresolved_validation_issue=bool(row["has_unresolved_validation_issue"]),
        )
        if stored != {"eligible": eligibility.eligible, "blockers": list(eligibility.blockers)}:
            raise SpecificationReviewPersistenceError("eligibility_tampering", "Stored review eligibility failed integrity verification.")
        state = SpecificationReviewState(
            project_id=row["project_id"], existing_dataset_id=row["existing_dataset_id"],
            proposed_dataset_id=row["proposed_dataset_id"], comparisons=comparisons,
            existing_baseline=baseline, has_unresolved_validation_issue=bool(row["has_unresolved_validation_issue"]),
            eligibility=eligibility,
        )
        return PersistedSpecificationReview(
            review_revision_id=row["review_revision_id"], review_id=row["review_id"],
            revision_number=int(row["revision_number"]), state=state, action_type=row["action_type"],
            action_field_key=row["action_field_key"], actor_reference=row["actor_reference"],
            action_reason=row["action_reason"], parent_revision_id=row["parent_revision_id"],
            content_hash=row["content_hash"], created_at=row["created_at"],
        )
