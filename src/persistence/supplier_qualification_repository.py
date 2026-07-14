from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.persistence._utils import new_id
from src.persistence.database import Database
from src.supplier_qualification import validate_supplier_qualification


class SupplierQualificationRepository:
    """Immutable, project-scoped supplier qualification evidence assessments."""

    _LINKS = (
        ("trial_executions", "trial_execution_id", "linked_trial_execution_ids"),
        ("defect_classifications", "defect_classification_id", "linked_defect_classification_ids"),
        ("complaint_records", "complaint_record_id", "linked_complaint_record_ids"),
        ("specification_change_requests", "specification_change_request_id", "linked_specification_change_request_ids"),
        ("implementation_controls", "implementation_control_id", "linked_implementation_control_ids"),
    )

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        qualification_code: str,
        supplier_name: str,
        supplier_site: str,
        qualification_scope: str,
        assessment_type: str,
        assessment_date: str,
        qualification_status: str,
        assessed_by: str,
        evidence_references: Sequence[str],
        content_hash: str,
        valid_from: str | None = None,
        valid_until: str | None = None,
        review_date: str | None = None,
        conditions: Sequence[str] = (),
        open_actions: Sequence[str] = (),
        linked_trial_execution_ids: Sequence[str] = (),
        linked_defect_classification_ids: Sequence[str] = (),
        linked_complaint_record_ids: Sequence[str] = (),
        linked_specification_change_request_ids: Sequence[str] = (),
        linked_implementation_control_ids: Sequence[str] = (),
        approved_by: str | None = None,
        approval_reference: str | None = None,
        approved_at: str | None = None,
        decision_rationale: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        **prohibited_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "qualification_code": qualification_code,
            "supplier_name": supplier_name,
            "supplier_site": supplier_site,
            "qualification_scope": qualification_scope,
            "assessment_type": assessment_type,
            "assessment_date": assessment_date,
            "qualification_status": qualification_status,
            "assessed_by": assessed_by,
            "evidence_references": list(evidence_references),
            "valid_from": valid_from,
            "valid_until": valid_until,
            "review_date": review_date,
            "conditions": list(conditions),
            "open_actions": list(open_actions),
            "linked_trial_execution_ids": list(linked_trial_execution_ids),
            "linked_defect_classification_ids": list(linked_defect_classification_ids),
            "linked_complaint_record_ids": list(linked_complaint_record_ids),
            "linked_specification_change_request_ids": list(linked_specification_change_request_ids),
            "linked_implementation_control_ids": list(linked_implementation_control_ids),
            "approved_by": approved_by,
            "approval_reference": approval_reference,
            "approved_at": approved_at,
            "decision_rationale": decision_rationale,
            "content_hash": content_hash.lower(),
            **prohibited_fields,
        }
        validation = validate_supplier_qualification(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{issue.field}: {issue.message}" for issue in validation.issues))

        identifier = new_id("supplier-qualification")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            values = {
                "linked_trial_execution_ids": linked_trial_execution_ids,
                "linked_defect_classification_ids": linked_defect_classification_ids,
                "linked_complaint_record_ids": linked_complaint_record_ids,
                "linked_specification_change_request_ids": linked_specification_change_request_ids,
                "linked_implementation_control_ids": linked_implementation_control_ids,
            }
            for table, id_column, key in self._LINKS:
                self._validate_links(connection, table, id_column, values[key], project_id)

            connection.execute(
                """
                INSERT INTO supplier_qualification_assessments(
                    supplier_qualification_assessment_id, project_id, qualification_code,
                    supplier_name, supplier_site, qualification_scope, assessment_type,
                    assessment_date, qualification_status, valid_from, valid_until,
                    review_date, conditions_json, open_actions_json,
                    linked_trial_execution_ids_json, linked_defect_classification_ids_json,
                    linked_complaint_record_ids_json,
                    linked_specification_change_request_ids_json,
                    linked_implementation_control_ids_json, evidence_references_json,
                    assessed_by, approved_by, approval_reference, approved_at,
                    decision_rationale, metadata_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, qualification_code, supplier_name, supplier_site,
                    qualification_scope, assessment_type, assessment_date, qualification_status,
                    valid_from, valid_until, review_date,
                    json.dumps(list(conditions), sort_keys=True),
                    json.dumps(list(open_actions), sort_keys=True),
                    json.dumps(list(linked_trial_execution_ids), sort_keys=True),
                    json.dumps(list(linked_defect_classification_ids), sort_keys=True),
                    json.dumps(list(linked_complaint_record_ids), sort_keys=True),
                    json.dumps(list(linked_specification_change_request_ids), sort_keys=True),
                    json.dumps(list(linked_implementation_control_ids), sort_keys=True),
                    json.dumps(list(evidence_references), sort_keys=True), assessed_by,
                    approved_by, approval_reference, approved_at, decision_rationale,
                    json.dumps(dict(metadata or {}), sort_keys=True), content_hash.lower(),
                ),
            )
        return self.get(identifier)

    @staticmethod
    def _validate_links(connection: Any, table: str, id_column: str, identifiers: Sequence[str], project_id: str) -> None:
        for identifier in identifiers:
            row = connection.execute(
                f"SELECT project_id FROM {table} WHERE {id_column} = ?", (identifier,)
            ).fetchone()
            if row is None:
                raise KeyError(identifier)
            if row["project_id"] != project_id:
                raise ValueError("Linked qualification evidence must belong to the same project.")

    def get(self, identifier: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM supplier_qualification_assessments WHERE supplier_qualification_assessment_id = ?",
                (identifier,),
            ).fetchone()
        if row is None:
            raise KeyError(identifier)
        result = dict(row)
        for column, key in (
            ("conditions_json", "conditions"),
            ("open_actions_json", "open_actions"),
            ("linked_trial_execution_ids_json", "linked_trial_execution_ids"),
            ("linked_defect_classification_ids_json", "linked_defect_classification_ids"),
            ("linked_complaint_record_ids_json", "linked_complaint_record_ids"),
            ("linked_specification_change_request_ids_json", "linked_specification_change_request_ids"),
            ("linked_implementation_control_ids_json", "linked_implementation_control_ids"),
            ("evidence_references_json", "evidence_references"),
            ("metadata_json", "metadata"),
        ):
            result[key] = json.loads(result.pop(column))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT supplier_qualification_assessment_id FROM supplier_qualification_assessments WHERE project_id = ? ORDER BY created_at, supplier_qualification_assessment_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Supplier qualification assessments are immutable; create a new assessment.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Supplier qualification assessments are immutable.")
