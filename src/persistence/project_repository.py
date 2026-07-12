from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.persistence._utils import new_id, row_to_dict
from src.persistence.database import Database


class ProjectRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_code: str,
        project_name: str,
        category: str,
        currency: str,
        annual_volume: float,
        status: str = "draft",
        project_id: str | None = None,
    ) -> dict[str, Any]:
        identifier = project_id or new_id("project")
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO projects(
                    project_id, project_code, project_name, category,
                    status, currency, annual_volume
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    project_code,
                    project_name,
                    category,
                    status,
                    currency,
                    annual_volume,
                ),
            )
        return self.get(identifier)

    def get(self, project_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
        if row is None:
            raise KeyError(project_id)
        return dict(row)

    def update_metadata(self, project_id: str, **changes: Any) -> dict[str, Any]:
        allowed = {"project_name", "category", "status", "currency", "annual_volume"}
        invalid = set(changes) - allowed
        if invalid:
            raise ValueError(f"Unsupported project fields: {sorted(invalid)}")
        if not changes:
            return self.get(project_id)
        assignments = ", ".join(f"{field} = ?" for field in changes)
        values = list(changes.values())
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with self.database.transaction() as connection:
            cursor = connection.execute(
                f"UPDATE projects SET {assignments}, updated_at = ? WHERE project_id = ?",
                (*values, timestamp, project_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(project_id)
        return self.get(project_id)

    def archive(self, project_id: str) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with self.database.transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE projects
                SET status = 'archived', archived_at = ?, updated_at = ?
                WHERE project_id = ?
                """,
                (timestamp, timestamp, project_id),
            )
            if cursor.rowcount != 1:
                raise KeyError(project_id)
        return self.get(project_id)

    def list(self, *, archived: bool | None = False) -> list[dict[str, Any]]:
        if archived is None:
            query, params = "SELECT * FROM projects ORDER BY created_at, project_code", ()
        elif archived:
            query, params = (
                "SELECT * FROM projects WHERE archived_at IS NOT NULL ORDER BY created_at, project_code",
                (),
            )
        else:
            query, params = (
                "SELECT * FROM projects WHERE archived_at IS NULL ORDER BY created_at, project_code",
                (),
            )
        with self.database.connect() as connection:
            return [dict(row) for row in connection.execute(query, params).fetchall()]
