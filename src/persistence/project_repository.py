from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.persistence._utils import new_id
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

    def get_by_code(self, project_code: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM projects WHERE project_code = ?", (project_code,)
            ).fetchone()
        if row is None:
            raise KeyError(project_code)
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

    def portfolio_summary(self) -> dict[str, int]:
        with self.database.connect() as connection:
            project_counts = connection.execute(
                """
                SELECT
                    COUNT(*) AS total_projects,
                    SUM(CASE WHEN archived_at IS NULL THEN 1 ELSE 0 END) AS active_projects,
                    SUM(CASE WHEN archived_at IS NOT NULL THEN 1 ELSE 0 END) AS archived_projects
                FROM projects
                """
            ).fetchone()
            dataset_count = connection.execute(
                "SELECT COUNT(*) FROM project_datasets"
            ).fetchone()[0]
            decision_count = connection.execute(
                "SELECT COUNT(*) FROM decision_snapshots"
            ).fetchone()[0]
        return {
            "total_projects": int(project_counts["total_projects"] or 0),
            "active_projects": int(project_counts["active_projects"] or 0),
            "archived_projects": int(project_counts["archived_projects"] or 0),
            "dataset_versions": int(dataset_count or 0),
            "decision_snapshots": int(decision_count or 0),
        }

    def dashboard_rows(self, *, archived: bool = False) -> list[dict[str, Any]]:
        archive_operator = "IS NOT NULL" if archived else "IS NULL"
        query = f"""
            SELECT
                p.project_id,
                p.project_code,
                p.project_name,
                p.category,
                p.status,
                p.currency,
                p.annual_volume,
                p.updated_at,
                p.archived_at,
                (SELECT COUNT(*) FROM project_datasets d WHERE d.project_id = p.project_id) AS dataset_versions,
                (SELECT COUNT(*) FROM scenarios s WHERE s.project_id = p.project_id) AS scenarios,
                (SELECT COUNT(*) FROM decision_snapshots ds WHERE ds.project_id = p.project_id) AS decisions,
                (
                    SELECT ds.status
                    FROM decision_snapshots ds
                    WHERE ds.project_id = p.project_id
                    ORDER BY ds.created_at DESC, ds.decision_snapshot_id DESC
                    LIMIT 1
                ) AS latest_decision_status
            FROM projects p
            WHERE p.archived_at {archive_operator}
            ORDER BY p.updated_at DESC, p.project_code
        """
        with self.database.connect() as connection:
            return [dict(row) for row in connection.execute(query).fetchall()]
