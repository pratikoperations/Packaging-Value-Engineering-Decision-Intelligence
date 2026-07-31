from __future__ import annotations

import json
import sqlite3
from typing import Any

from src.domain.approved_specification import (
    ApprovedSpecificationMaterialization,
    ApprovedSpecificationSnapshot,
    ApprovedSpecificationValue,
    approved_specification_content_hash,
)
from src.persistence.approved_specification_migration import (
    initialize_approved_specification_schema,
)
from src.persistence.database import Database


class ApprovedSpecificationPersistenceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ApprovedSpecificationSnapshotRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        initialize_approved_specification_schema(database)

    def create(self, snapshot: ApprovedSpecificationSnapshot) -> ApprovedSpecificationSnapshot:
        self._verify_snapshot_hash(snapshot)
        try:
            with self.database.transaction() as connection:
                self._validate_write_lineage(connection, snapshot)
                connection.execute(
                    """
                    INSERT INTO approved_specification_snapshots(
                        snapshot_id, project_id, review_id,
                        source_review_revision_id, source_review_revision_number,
                        existing_dataset_id, proposed_dataset_id,
                        approved_values_json, excluded_fields_json,
                        snapshot_schema_version, actor_reference, approval_reason,
                        content_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot.snapshot_id,
                        snapshot.project_id,
                        snapshot.review_id,
                        snapshot.source_review_revision_id,
                        snapshot.source_review_revision_number,
                        snapshot.existing_dataset_id,
                        snapshot.proposed_dataset_id,
                        self._approved_values_json(snapshot.approved_values),
                        self._excluded_fields_json(snapshot.excluded_fields),
                        snapshot.snapshot_schema_version,
                        snapshot.actor_reference.strip(),
                        snapshot.approval_reason.strip(),
                        snapshot.content_hash,
                        snapshot.created_at,
                    ),
                )
        except sqlite3.IntegrityError as error:
            message = str(error)
            if "source_review_revision_id" in message or "UNIQUE constraint failed" in message:
                raise ApprovedSpecificationPersistenceError(
                    "duplicate_source_revision",
                    "An approved specification snapshot already exists for this review revision.",
                ) from error
            raise ApprovedSpecificationPersistenceError(
                "snapshot_integrity_error",
                "The approved specification snapshot could not be persisted safely.",
            ) from error
        return self.get(snapshot.snapshot_id, project_id=snapshot.project_id)

    def get(self, snapshot_id: str, *, project_id: str) -> ApprovedSpecificationSnapshot:
        self._require_project(project_id)
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM approved_specification_snapshots
                WHERE snapshot_id = ? AND project_id = ?
                """,
                (snapshot_id, project_id),
            ).fetchone()
        if row is None:
            raise ApprovedSpecificationPersistenceError(
                "snapshot_not_found",
                "The approved specification snapshot was not found in this project.",
            )
        return self._decode_and_verify(dict(row))

    def get_for_review(
        self,
        review_id: str,
        *,
        project_id: str,
    ) -> ApprovedSpecificationSnapshot | None:
        self._require_project(project_id)
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM approved_specification_snapshots
                WHERE review_id = ? AND project_id = ?
                ORDER BY created_at DESC, snapshot_id DESC
                LIMIT 1
                """,
                (review_id, project_id),
            ).fetchone()
        return None if row is None else self._decode_and_verify(dict(row))

    def list_for_project(self, project_id: str) -> list[ApprovedSpecificationSnapshot]:
        self._require_project(project_id)
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM approved_specification_snapshots
                WHERE project_id = ?
                ORDER BY created_at, snapshot_id
                """,
                (project_id,),
            ).fetchall()
        return [self._decode_and_verify(dict(row)) for row in rows]

    def update(self, snapshot_id: str, **changes: Any) -> None:
        raise ApprovedSpecificationPersistenceError(
            "immutable_snapshot",
            "Approved specification snapshots cannot be updated.",
        )

    def delete(self, snapshot_id: str) -> None:
        raise ApprovedSpecificationPersistenceError(
            "immutable_snapshot",
            "Approved specification snapshots cannot be deleted.",
        )

    def _require_project(self, project_id: str) -> None:
        if not project_id.strip():
            raise ApprovedSpecificationPersistenceError(
                "project_required",
                "A project scope is required.",
            )
        with self.database.connect() as connection:
            project = connection.execute(
                "SELECT project_id FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        if project is None:
            raise ApprovedSpecificationPersistenceError(
                "unknown_project",
                "The project does not exist.",
            )

    @staticmethod
    def _validate_write_lineage(
        connection: sqlite3.Connection,
        snapshot: ApprovedSpecificationSnapshot,
    ) -> None:
        project = connection.execute(
            "SELECT archived_at FROM projects WHERE project_id = ?",
            (snapshot.project_id,),
        ).fetchone()
        if project is None:
            raise ApprovedSpecificationPersistenceError(
                "unknown_project",
                "The project does not exist.",
            )
        if project["archived_at"] is not None:
            raise ApprovedSpecificationPersistenceError(
                "archived_project",
                "Archived projects are read-only.",
            )

        datasets = connection.execute(
            """
            SELECT dataset_id, project_id
            FROM project_datasets
            WHERE dataset_id IN (?, ?)
            """,
            (snapshot.existing_dataset_id, snapshot.proposed_dataset_id),
        ).fetchall()
        if len(datasets) != 2 or any(
            row["project_id"] != snapshot.project_id for row in datasets
        ):
            raise ApprovedSpecificationPersistenceError(
                "invalid_dataset_lineage",
                "Snapshot datasets must exist in the same project.",
            )

        revision = connection.execute(
            """
            SELECT review_revision_id, review_id, revision_number, project_id,
                   existing_dataset_id, proposed_dataset_id
            FROM specification_review_revisions
            WHERE review_revision_id = ?
            """,
            (snapshot.source_review_revision_id,),
        ).fetchone()
        if revision is None:
            raise ApprovedSpecificationPersistenceError(
                "unknown_source_revision",
                "The source review revision does not exist.",
            )
        expected = (
            snapshot.review_id,
            snapshot.source_review_revision_number,
            snapshot.project_id,
            snapshot.existing_dataset_id,
            snapshot.proposed_dataset_id,
        )
        actual = (
            revision["review_id"],
            int(revision["revision_number"]),
            revision["project_id"],
            revision["existing_dataset_id"],
            revision["proposed_dataset_id"],
        )
        if actual != expected:
            raise ApprovedSpecificationPersistenceError(
                "invalid_review_lineage",
                "Snapshot lineage does not match the source review revision.",
            )

    @staticmethod
    def _approved_values_json(
        values: tuple[ApprovedSpecificationValue, ...],
    ) -> str:
        payload = [
            {"field_key": item.field_key, "value": item.value, "source": item.source}
            for item in values
        ]
        return json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    @staticmethod
    def _excluded_fields_json(fields: tuple[str, ...]) -> str:
        return json.dumps(
            list(fields),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )

    @classmethod
    def _decode_and_verify(
        cls,
        row: dict[str, Any],
    ) -> ApprovedSpecificationSnapshot:
        try:
            approved_values = tuple(
                ApprovedSpecificationValue(
                    field_key=item["field_key"],
                    value=item["value"],
                    source=item["source"],
                )
                for item in json.loads(row["approved_values_json"])
            )
            excluded_fields = tuple(json.loads(row["excluded_fields_json"]))
            snapshot = ApprovedSpecificationSnapshot(
                snapshot_id=row["snapshot_id"],
                project_id=row["project_id"],
                review_id=row["review_id"],
                source_review_revision_id=row["source_review_revision_id"],
                source_review_revision_number=int(row["source_review_revision_number"]),
                existing_dataset_id=row["existing_dataset_id"],
                proposed_dataset_id=row["proposed_dataset_id"],
                approved_values=approved_values,
                excluded_fields=excluded_fields,
                snapshot_schema_version=row["snapshot_schema_version"],
                actor_reference=row["actor_reference"],
                approval_reason=row["approval_reason"],
                content_hash=row["content_hash"],
                created_at=row["created_at"],
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ApprovedSpecificationPersistenceError(
                "snapshot_content_invalid",
                "Stored approved specification content is invalid.",
            ) from error
        cls._verify_snapshot_hash(snapshot)
        return snapshot

    @staticmethod
    def _verify_snapshot_hash(snapshot: ApprovedSpecificationSnapshot) -> None:
        materialization = ApprovedSpecificationMaterialization(
            snapshot.approved_values,
            snapshot.excluded_fields,
        )
        expected = approved_specification_content_hash(
            project_id=snapshot.project_id,
            review_id=snapshot.review_id,
            source_review_revision_id=snapshot.source_review_revision_id,
            source_review_revision_number=snapshot.source_review_revision_number,
            existing_dataset_id=snapshot.existing_dataset_id,
            proposed_dataset_id=snapshot.proposed_dataset_id,
            materialization=materialization,
            snapshot_schema_version=snapshot.snapshot_schema_version,
        )
        if snapshot.content_hash != expected:
            raise ApprovedSpecificationPersistenceError(
                "content_hash_mismatch",
                "Approved specification snapshot failed integrity verification.",
            )
