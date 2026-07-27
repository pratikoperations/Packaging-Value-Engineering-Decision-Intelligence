from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from typing import Any

from src.persistence._utils import canonical_json
from src.persistence.database import Database
from src.persistence.specification_snapshot_migration import initialize_specification_snapshot_schema
from src.specification_intake.snapshot import UnifiedSpecificationSnapshot


class DuplicateSpecificationSnapshotError(ValueError):
    pass


class SpecificationSnapshotRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        initialize_specification_snapshot_schema(database)

    def create(self, snapshot: UnifiedSpecificationSnapshot) -> dict[str, Any]:
        try:
            with self.database.transaction() as connection:
                project = connection.execute(
                    "SELECT project_id, archived_at FROM projects WHERE project_id = ?",
                    (snapshot.project_id,),
                ).fetchone()
                if project is None:
                    raise KeyError(snapshot.project_id)
                if project["archived_at"] is not None:
                    raise ValueError("Archived projects are read-only.")
                connection.execute(
                    """
                    INSERT INTO unified_specification_snapshots(
                        specification_snapshot_id, project_id, pair_format,
                        existing_document_json, proposed_document_json,
                        extraction_schema_version, alias_registry_version, provider_id,
                        confirmed_fields_json, canonical_dataset_draft_json,
                        canonical_validation_issues_json, canonical_validation_valid,
                        content_hash
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        snapshot.snapshot_id,
                        snapshot.project_id,
                        snapshot.pair_format,
                        canonical_json(asdict(snapshot.existing_document)),
                        canonical_json(asdict(snapshot.proposed_document)),
                        snapshot.extraction_schema_version,
                        snapshot.alias_registry_version,
                        snapshot.provider_id,
                        canonical_json([asdict(field) for field in snapshot.confirmed_fields]),
                        canonical_json(snapshot.canonical_dataset_draft),
                        canonical_json(list(snapshot.canonical_validation_issues)),
                        int(snapshot.canonical_validation_valid),
                        snapshot.content_hash,
                    ),
                )
        except sqlite3.IntegrityError as exc:
            if "content_hash" in str(exc) or "UNIQUE constraint failed" in str(exc):
                raise DuplicateSpecificationSnapshotError(
                    "An identical unified specification snapshot already exists for this project."
                ) from exc
            raise
        return self.get(snapshot.snapshot_id, project_id=snapshot.project_id)

    def get(self, snapshot_id: str, *, project_id: str | None = None) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM unified_specification_snapshots WHERE specification_snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
        if row is None:
            raise KeyError(snapshot_id)
        decoded = self._decode(dict(row))
        if project_id is not None and decoded["project_id"] != project_id:
            raise PermissionError("Snapshot belongs to a different project.")
        return decoded

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM unified_specification_snapshots
                WHERE project_id = ?
                ORDER BY created_at, specification_snapshot_id
                """,
                (project_id,),
            ).fetchall()
        return [self._decode(dict(row)) for row in rows]

    def update(self, snapshot_id: str, **changes: Any) -> None:
        raise ValueError("Unified specification snapshots are append-only and cannot be updated.")

    def delete(self, snapshot_id: str) -> None:
        raise ValueError("Unified specification snapshots are append-only and cannot be deleted.")

    @staticmethod
    def _decode(row: dict[str, Any]) -> dict[str, Any]:
        row["existing_document"] = json.loads(row.pop("existing_document_json"))
        row["proposed_document"] = json.loads(row.pop("proposed_document_json"))
        row["confirmed_fields"] = json.loads(row.pop("confirmed_fields_json"))
        row["canonical_dataset_draft"] = json.loads(row.pop("canonical_dataset_draft_json"))
        row["canonical_validation_issues"] = json.loads(row.pop("canonical_validation_issues_json"))
        row["canonical_validation_valid"] = bool(row["canonical_validation_valid"])
        return row
