from __future__ import annotations

import json
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
        digest = content_hash(profile)
        existing = self.find_by_content(
            profile_name=profile_name,
            profile=profile,
            project_id=project_id,
        )
        if existing is not None:
            return existing
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
                    digest,
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
        record = dict(row)
        record["profile"] = json.loads(record["profile_json"])
        return record

    def find_by_content(
        self,
        *,
        profile_name: str,
        profile: dict[str, Any],
        project_id: str | None,
    ) -> dict[str, Any] | None:
        digest = content_hash(profile)
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT threshold_profile_id
                FROM threshold_profiles
                WHERE project_id IS ? AND profile_name = ? AND content_hash = ?
                """,
                (project_id, profile_name, digest),
            ).fetchone()
        return self.get(row[0]) if row is not None else None

    def list_available(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT threshold_profile_id
                FROM threshold_profiles
                WHERE project_id IS NULL OR project_id = ?
                ORDER BY CASE WHEN project_id IS NULL THEN 0 ELSE 1 END,
                         profile_name, version_number DESC
                """,
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def latest(self, *, profile_name: str, project_id: str | None) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT threshold_profile_id
                FROM threshold_profiles
                WHERE project_id IS ? AND profile_name = ?
                ORDER BY version_number DESC
                LIMIT 1
                """,
                (project_id, profile_name),
            ).fetchone()
        return self.get(row[0]) if row is not None else None
