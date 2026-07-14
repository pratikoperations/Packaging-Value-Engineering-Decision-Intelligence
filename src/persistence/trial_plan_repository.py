from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.persistence._utils import new_id
from src.persistence.database import Database
from src.trial_planning import validate_trial_plan


class TrialPlanRepository:
    """Project-scoped immutable trial plans with governed evidence and authorization."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        trial_code: str,
        title: str,
        objective: str,
        protocol: str,
        owner: str,
        trial_site: str,
        planned_start_date: str,
        planned_end_date: str,
        status: str,
        authorization_status: str,
        acceptance_criteria: Sequence[Mapping[str, Any]],
        content_hash: str,
        drawing_evidence_ids: Sequence[str] = (),
        specification_versions: Sequence[str] = (),
        evidence_requirements: Sequence[Mapping[str, Any]] = (),
        prerequisites: Sequence[str] = (),
        blockers: Sequence[str] = (),
        authorized_by: str | None = None,
        authorization_reference: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        **prohibited_execution_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "trial_code": trial_code,
            "title": title,
            "objective": objective,
            "protocol": protocol,
            "owner": owner,
            "trial_site": trial_site,
            "planned_start_date": planned_start_date,
            "planned_end_date": planned_end_date,
            "status": status,
            "authorization_status": authorization_status,
            "authorized_by": authorized_by,
            "acceptance_criteria": list(acceptance_criteria),
            "content_hash": content_hash.lower(),
            **prohibited_execution_fields,
        }
        validation = validate_trial_plan(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))

        identifier = new_id("trial-plan")
        drawing_ids = list(drawing_evidence_ids)
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            for evidence_id in drawing_ids:
                row = connection.execute(
                    "SELECT project_id FROM drawing_evidence WHERE drawing_evidence_id = ?", (evidence_id,)
                ).fetchone()
                if row is None:
                    raise KeyError(evidence_id)
                if row["project_id"] != project_id:
                    raise ValueError("Drawing evidence must belong to the same project.")

            connection.execute(
                """
                INSERT INTO trial_plans(
                    trial_plan_id, project_id, trial_code, title, objective, protocol,
                    owner, trial_site, planned_start_date, planned_end_date, status,
                    authorization_status, authorized_by, authorization_reference,
                    drawing_evidence_ids_json, specification_versions_json,
                    evidence_requirements_json, acceptance_criteria_json,
                    prerequisites_json, blockers_json, metadata_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, trial_code, title, objective, protocol,
                    owner, trial_site, planned_start_date, planned_end_date, status,
                    authorization_status, authorized_by, authorization_reference,
                    json.dumps(drawing_ids, sort_keys=True),
                    json.dumps(list(specification_versions), sort_keys=True),
                    json.dumps(list(evidence_requirements), sort_keys=True),
                    json.dumps(list(acceptance_criteria), sort_keys=True),
                    json.dumps(list(prerequisites), sort_keys=True),
                    json.dumps(list(blockers), sort_keys=True),
                    json.dumps(dict(metadata or {}), sort_keys=True), content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, trial_plan_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM trial_plans WHERE trial_plan_id = ?", (trial_plan_id,)
            ).fetchone()
        if row is None:
            raise KeyError(trial_plan_id)
        result = dict(row)
        for field in (
            "drawing_evidence_ids_json", "specification_versions_json",
            "evidence_requirements_json", "acceptance_criteria_json",
            "prerequisites_json", "blockers_json", "metadata_json",
        ):
            result[field.removesuffix("_json")] = json.loads(result.pop(field))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT trial_plan_id FROM trial_plans WHERE project_id = ? ORDER BY created_at, trial_plan_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Trial plans are immutable; create a new plan revision.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Trial plans are immutable.")
