from __future__ import annotations

from typing import Any

from src.persistence._utils import canonical_json, content_hash, new_id
from src.persistence.database import Database


class ScenarioRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        dataset_id: str,
        scenario_name: str,
        assumptions: dict[str, Any],
        results: dict[str, Any],
        threshold_profile_id: str | None = None,
    ) -> dict[str, Any]:
        identifier = new_id("scenario")
        payload = {"assumptions": assumptions, "results": results}
        with self.database.transaction() as connection:
            connection.execute(
                """
                INSERT INTO scenarios(
                    scenario_id, project_id, dataset_id, threshold_profile_id,
                    scenario_name, assumptions_json, results_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    project_id,
                    dataset_id,
                    threshold_profile_id,
                    scenario_name,
                    canonical_json(assumptions),
                    canonical_json(results),
                    content_hash(payload),
                ),
            )
        return self.get(identifier)

    def get(self, scenario_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM scenarios WHERE scenario_id = ?", (scenario_id,)
            ).fetchone()
        if row is None:
            raise KeyError(scenario_id)
        return dict(row)
