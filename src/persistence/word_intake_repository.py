"""Append-only repository for confirmed PVE 2.0 Word-intake snapshots."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from src.intake_mapping.models import ConfirmedIntakeSnapshot
from src.persistence._utils import canonical_json
from src.persistence.database import Database
from src.persistence.word_intake_migration import initialize_word_intake_schema


class WordIntakeRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        initialize_word_intake_schema(database)

    def create(self, snapshot: ConfirmedIntakeSnapshot) -> dict[str, Any]:
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
                INSERT INTO word_intake_snapshots(
                    word_intake_snapshot_id,
                    project_id,
                    existing_filename,
                    existing_document_hash,
                    proposed_filename,
                    proposed_document_hash,
                    parser_version,
                    extraction_schema_version,
                    alias_registry_version,
                    provider_id,
                    confirmed_fields_json,
                    canonical_dataset_draft_json,
                    canonical_validation_issues_json,
                    canonical_validation_valid,
                    content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.snapshot_id,
                    snapshot.project_id,
                    snapshot.existing_filename,
                    snapshot.existing_document_hash,
                    snapshot.proposed_filename,
                    snapshot.proposed_document_hash,
                    snapshot.parser_version,
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
        return self.get(snapshot.snapshot_id)

    def get(self, snapshot_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM word_intake_snapshots WHERE word_intake_snapshot_id = ?",
                (snapshot_id,),
            ).fetchone()
        if row is None:
            raise KeyError(snapshot_id)
        return self._decode(dict(row))

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM word_intake_snapshots
                WHERE project_id = ?
                ORDER BY created_at, word_intake_snapshot_id
                """,
                (project_id,),
            ).fetchall()
        return [self._decode(dict(row)) for row in rows]

    def update(self, snapshot_id: str, **changes: Any) -> None:
        raise ValueError("Word-intake snapshots are append-only and cannot be updated.")

    def delete(self, snapshot_id: str) -> None:
        raise ValueError("Word-intake snapshots are append-only and cannot be deleted.")

    @staticmethod
    def _decode(row: dict[str, Any]) -> dict[str, Any]:
        row["confirmed_fields"] = json.loads(row.pop("confirmed_fields_json"))
        row["canonical_dataset_draft"] = json.loads(row.pop("canonical_dataset_draft_json"))
        row["canonical_validation_issues"] = json.loads(
            row.pop("canonical_validation_issues_json")
        )
        row["canonical_validation_valid"] = bool(row["canonical_validation_valid"])
        return row
