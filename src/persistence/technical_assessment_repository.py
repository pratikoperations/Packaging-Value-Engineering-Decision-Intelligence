from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping, Sequence

from src.persistence._utils import new_id
from src.persistence.database import Database


class TechnicalAssessmentRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        readiness_assessment_id: str | None,
        dataset_id: str,
        baseline_specification_version: str,
        proposed_specification_version: str,
        rule_set_version: str,
        threshold_profile_id: str | None,
        threshold_references: Sequence[str],
        evidence_references: Sequence[Mapping[str, Any]],
        formula_inputs: Mapping[str, Any],
        assumptions: Sequence[str],
        technical_outcomes: Mapping[str, Any],
        commercial_outcomes: Mapping[str, Any],
        blockers: Sequence[str],
        required_trials: Sequence[str],
        evidence_confidence_status: str,
        recommendation_outcome: str,
    ) -> dict[str, Any]:
        payload = {
            "threshold_references": list(threshold_references),
            "evidence_references": [dict(item) for item in evidence_references],
            "formula_inputs": dict(formula_inputs),
            "assumptions": list(assumptions),
            "technical_outcomes": dict(technical_outcomes),
            "commercial_outcomes": dict(commercial_outcomes),
            "blockers": list(blockers),
            "required_trials": list(required_trials),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        identifier = new_id("technical-assessment")

        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            dataset = connection.execute(
                "SELECT project_id, version_number FROM project_datasets WHERE dataset_id = ?", (dataset_id,)
            ).fetchone()
            if dataset is None:
                raise KeyError(dataset_id)
            if dataset["project_id"] != project_id:
                raise ValueError("Technical-assessment dataset must belong to the same project.")

            if readiness_assessment_id is not None:
                readiness = connection.execute(
                    "SELECT project_id, dataset_id FROM readiness_assessments WHERE readiness_assessment_id = ?",
                    (readiness_assessment_id,),
                ).fetchone()
                if readiness is None:
                    raise KeyError(readiness_assessment_id)
                if readiness["project_id"] != project_id or readiness["dataset_id"] not in (None, dataset_id):
                    raise ValueError("Readiness assessment must belong to the same project and dataset.")

            if threshold_profile_id is not None:
                threshold = connection.execute(
                    "SELECT project_id FROM threshold_profiles WHERE threshold_profile_id = ?",
                    (threshold_profile_id,),
                ).fetchone()
                if threshold is None:
                    raise KeyError(threshold_profile_id)
                if threshold["project_id"] not in (None, project_id):
                    raise ValueError("Threshold profile must be global or belong to the same project.")

            for evidence in evidence_references:
                if str(evidence.get("project_id") or "") != project_id:
                    raise ValueError("Evidence references must belong to the same project.")

            connection.execute(
                """
                INSERT INTO technical_assessments(
                    technical_assessment_id, project_id, readiness_assessment_id, dataset_id,
                    dataset_version, baseline_specification_version, proposed_specification_version,
                    rule_set_version, threshold_profile_id, threshold_references_json,
                    evidence_references_json, formula_inputs_json, assumptions_json,
                    technical_outcomes_json, commercial_outcomes_json, blockers_json,
                    required_trials_json, evidence_confidence_status, recommendation_outcome,
                    content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, readiness_assessment_id, dataset_id,
                    int(dataset["version_number"]), baseline_specification_version,
                    proposed_specification_version, rule_set_version, threshold_profile_id,
                    json.dumps(list(threshold_references), sort_keys=True),
                    json.dumps([dict(item) for item in evidence_references], sort_keys=True),
                    json.dumps(dict(formula_inputs), sort_keys=True),
                    json.dumps(list(assumptions), sort_keys=True),
                    json.dumps(dict(technical_outcomes), sort_keys=True),
                    json.dumps(dict(commercial_outcomes), sort_keys=True),
                    json.dumps(list(blockers), sort_keys=True),
                    json.dumps(list(required_trials), sort_keys=True),
                    evidence_confidence_status, recommendation_outcome, digest,
                ),
            )
        return self.get(identifier)

    def get(self, technical_assessment_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM technical_assessments WHERE technical_assessment_id = ?",
                (technical_assessment_id,),
            ).fetchone()
        if row is None:
            raise KeyError(technical_assessment_id)
        result = dict(row)
        for field in (
            "threshold_references_json", "evidence_references_json", "formula_inputs_json",
            "assumptions_json", "technical_outcomes_json", "commercial_outcomes_json",
            "blockers_json", "required_trials_json",
        ):
            result[field.removesuffix("_json")] = json.loads(result.pop(field))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT technical_assessment_id FROM technical_assessments WHERE project_id = ? ORDER BY created_at, technical_assessment_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Technical assessments are immutable.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Technical assessments are immutable.")
