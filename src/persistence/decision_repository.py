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
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects cannot create decision snapshots.")

            scenario = connection.execute(
                """
                SELECT project_id, dataset_id, threshold_profile_id
                FROM scenarios WHERE scenario_id = ?
                """,
                (scenario_id,),
            ).fetchone()
            if scenario is None:
                raise KeyError(scenario_id)
            if scenario["project_id"] != project_id:
                raise ValueError("Decision scenario must belong to the same project.")

            dataset = connection.execute(
                "SELECT project_id FROM project_datasets WHERE dataset_id = ?",
                (dataset_id,),
            ).fetchone()
            if dataset is None:
                raise KeyError(dataset_id)
            if dataset["project_id"] != project_id:
                raise ValueError("Decision dataset must belong to the same project.")
            if scenario["dataset_id"] != dataset_id:
                raise ValueError("Decision dataset must match the scenario dataset.")

            if threshold_profile_id is not None:
                threshold = connection.execute(
                    "SELECT project_id FROM threshold_profiles WHERE threshold_profile_id = ?",
                    (threshold_profile_id,),
                ).fetchone()
                if threshold is None:
                    raise KeyError(threshold_profile_id)
                if threshold["project_id"] not in (None, project_id):
                    raise ValueError(
                        "Decision threshold profile must be global or belong to the same project."
                    )

            if scenario["threshold_profile_id"] != threshold_profile_id:
                raise ValueError(
                    "Decision threshold profile must match the scenario threshold profile."
                )

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
