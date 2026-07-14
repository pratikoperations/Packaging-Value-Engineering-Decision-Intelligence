from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.persistence._utils import new_id
from src.persistence.database import Database
from src.trial_execution import validate_trial_execution


class TrialExecutionRepository:
    """Project-scoped immutable trial execution snapshots and deviations."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        trial_plan_id: str,
        execution_code: str,
        started_at: str,
        completed_at: str,
        performed_by: str,
        trial_site: str,
        status: str,
        outcome: str,
        measurements: Sequence[Mapping[str, Any]],
        reviewed_by: str,
        content_hash: str,
        evidence_references: Sequence[str] = (),
        deviations: Sequence[Mapping[str, Any]] = (),
        notes: Sequence[str] = (),
        metadata: Mapping[str, Any] | None = None,
        **prohibited_later_build_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "trial_plan_id": trial_plan_id,
            "execution_code": execution_code,
            "started_at": started_at,
            "completed_at": completed_at,
            "performed_by": performed_by,
            "trial_site": trial_site,
            "status": status,
            "outcome": outcome,
            "measurements": list(measurements),
            "reviewed_by": reviewed_by,
            "deviations": list(deviations),
            "content_hash": content_hash.lower(),
            **prohibited_later_build_fields,
        }
        validation = validate_trial_execution(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))

        identifier = new_id("trial-execution")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            plan = connection.execute(
                "SELECT project_id, status, authorization_status FROM trial_plans WHERE trial_plan_id = ?",
                (trial_plan_id,),
            ).fetchone()
            if plan is None:
                raise KeyError(trial_plan_id)
            if plan["project_id"] != project_id:
                raise ValueError("Trial plan must belong to the same project.")
            if plan["status"] != "authorized" or plan["authorization_status"] != "authorized":
                raise ValueError("Trial execution requires an explicitly authorized trial plan.")

            connection.execute(
                """
                INSERT INTO trial_executions(
                    trial_execution_id, project_id, trial_plan_id, execution_code,
                    started_at, completed_at, performed_by, trial_site, status, outcome,
                    measurements_json, evidence_references_json, deviations_json,
                    notes_json, reviewed_by, metadata_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, trial_plan_id, execution_code,
                    started_at, completed_at, performed_by, trial_site, status, outcome,
                    json.dumps(list(measurements), sort_keys=True),
                    json.dumps(list(evidence_references), sort_keys=True),
                    json.dumps(list(deviations), sort_keys=True),
                    json.dumps(list(notes), sort_keys=True), reviewed_by,
                    json.dumps(dict(metadata or {}), sort_keys=True), content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, trial_execution_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM trial_executions WHERE trial_execution_id = ?", (trial_execution_id,)
            ).fetchone()
        if row is None:
            raise KeyError(trial_execution_id)
        result = dict(row)
        for field in (
            "measurements_json", "evidence_references_json", "deviations_json",
            "notes_json", "metadata_json",
        ):
            result[field.removesuffix("_json")] = json.loads(result.pop(field))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT trial_execution_id FROM trial_executions WHERE project_id = ? ORDER BY created_at, trial_execution_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def list_for_plan(self, trial_plan_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT trial_execution_id FROM trial_executions WHERE trial_plan_id = ? ORDER BY created_at, trial_execution_id",
                (trial_plan_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Trial executions are immutable; create a new execution record.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Trial executions are immutable.")
