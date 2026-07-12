from __future__ import annotations

from typing import Any

from src.persistence._utils import canonical_json, content_hash, new_id
from src.persistence.database import Database


class DecisionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create_snapshot(
        self,
        *,
        project_id: str,
        scenario_id: str,
        dataset_id: str,
        status: str,
        recommendation: dict[str, Any],
        gate_results: dict[str, Any],
        engine_version: str,
        source_commit: str,
        preferred_alternative_id: str | None = None,
        threshold_profile_id: str | None = None,
    ) -> dict[str, Any]:
        identifier = new_id("decision")
        payload = {
            "recommendation": recommendation,
            "gate_results": gate_results,
            "status": status,
            "preferred_alternative_id": preferred_alternative_id,
        }
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO decision_snapshots(
                    decision_snapshot_id, project_id, scenario_id, dataset_id,
                    threshold_profile_id, status, preferred_alternative_id,
                    recommendation_json, gate_results_json, engine_version,
                    source_commit, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    project_id,
                    scenario_id,
                    dataset_id,
                    threshold_profile_id,
                    status,
                    preferred_alternative_id,
                    canonical_json(recommendation),
                    canonical_json(gate_results),
                    engine_version,
                    source_commit,
                    content_hash(payload),
                ),
            )
        return self.get(identifier)

    def get(self, decision_snapshot_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM decision_snapshots WHERE decision_snapshot_id = ?",
                (decision_snapshot_id,),
            ).fetchone()
        if row is None:
            raise KeyError(decision_snapshot_id)
        return dict(row)

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM decision_snapshots WHERE project_id = ? ORDER BY created_at",
                    (project_id,),
                ).fetchall()
            ]
