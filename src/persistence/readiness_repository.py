from __future__ import annotations

import hashlib
import json
from typing import Any

from src.persistence._utils import new_id
from src.persistence.database import Database


class ReadinessRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, *, project_id: str, dataset_id: str | None, assessment: dict[str, Any]) -> dict[str, Any]:
        payload = json.dumps(assessment, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        identifier = new_id("readiness")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")
            if dataset_id is not None:
                dataset = connection.execute(
                    "SELECT project_id FROM project_datasets WHERE dataset_id = ?", (dataset_id,)
                ).fetchone()
                if dataset is None:
                    raise KeyError(dataset_id)
                if dataset["project_id"] != project_id:
                    raise ValueError("Readiness dataset must belong to the same project.")
            connection.execute(
                """
                INSERT INTO readiness_assessments(
                    readiness_assessment_id, project_id, dataset_id, score_percent,
                    stage, assessment_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier,
                    project_id,
                    dataset_id,
                    float(assessment["score_percent"]),
                    str(assessment["stage"]),
                    payload,
                    digest,
                ),
            )
        return self.get(identifier)

    def get(self, readiness_assessment_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM readiness_assessments WHERE readiness_assessment_id = ?",
                (readiness_assessment_id,),
            ).fetchone()
        if row is None:
            raise KeyError(readiness_assessment_id)
        result = dict(row)
        result["assessment"] = json.loads(result.pop("assessment_json"))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT readiness_assessment_id FROM readiness_assessments WHERE project_id = ? ORDER BY created_at, readiness_assessment_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]
