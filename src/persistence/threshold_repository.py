from __future__ import annotations

from typing import Any

from src.persistence._utils import canonical_json, content_hash, new_id
from src.persistence.database import Database


class ThresholdRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_version(
        self,
        *,
        profile_name: str,
        profile: dict[str, Any],
        project_id: str | None = None,
    ) -> dict[str, Any]:
        with self.database.transaction() as connection:
            version = connection.execute(
                """
                SELECT COALESCE(MAX(version_number), 0) + 1
                FROM threshold_profiles
                WHERE project_id IS ? AND profile_name = ?
                """,
                (project_id, profile_name),
            ).fetchone()[0]
            identifier = new_id("threshold")
            connection.execute(
                """
                INSERT INTO threshold_profiles(
                    threshold_profile_id, project_id, profile_name,
                    version_number, profile_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    project_id,
                    profile_name,
                    version,
                    canonical_json(profile),
                    content_hash(profile),
                ),
            )
        return self.get(identifier)

    def get(self, threshold_profile_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM threshold_profiles WHERE threshold_profile_id = ?",
                (threshold_profile_id,),
            ).fetchone()
        if row is None:
            raise KeyError(threshold_profile_id)
        return dict(row)
