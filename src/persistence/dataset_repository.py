from __future__ import annotations

from typing import Any

from src.persistence._utils import canonical_json, content_hash, new_id
from src.persistence.database import Database


class DatasetRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_version(
        self,
        *,
        project_id: str,
        source_type: str,
        canonical_data: dict[str, Any],
        validation_status: str,
        validation_issues: list[dict[str, Any]] | None = None,
        original_filename: str | None = None,
    ) -> dict[str, Any]:
        digest = content_hash(canonical_data)
        with self.database.transaction() as connection:
            version = connection.execute(
                "SELECT COALESCE(MAX(version_number), 0) + 1 FROM project_datasets WHERE project_id = ?",
                (project_id,),
            ).fetchone()[0]
            identifier = new_id("dataset")
            connection.execute(
                """
                INSERT INTO project_datasets(
                    dataset_id, project_id, version_number, source_type,
                    original_filename, canonical_json, validation_status,
                    validation_issues_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    project_id,
                    version,
                    source_type,
                    original_filename,
                    canonical_json(canonical_data),
                    validation_status,
                    canonical_json(validation_issues or []),
                    digest,
                ),
            )
        return self.get(identifier)

    def get(self, dataset_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM project_datasets WHERE dataset_id = ?", (dataset_id,)
            ).fetchone()
        if row is None:
            raise KeyError(dataset_id)
        return dict(row)

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM project_datasets WHERE project_id = ? ORDER BY version_number",
                    (project_id,),
                ).fetchall()
            ]
