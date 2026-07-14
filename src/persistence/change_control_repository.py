from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.change_control import validate_implementation_control, validate_specification_change
from src.persistence._utils import new_id
from src.persistence.database import Database


class SpecificationChangeRepository:
    """Immutable, project-scoped specification change requests."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        change_code: str,
        change_type: str,
        title: str,
        rationale: str,
        current_specification_version: str,
        proposed_specification_version: str,
        review_status: str,
        approval_status: str,
        requested_by: str,
        evidence_references: Sequence[str],
        content_hash: str,
        requested_effective_date: str | None = None,
        linked_trial_execution_ids: Sequence[str] = (),
        linked_defect_classification_ids: Sequence[str] = (),
        linked_complaint_record_ids: Sequence[str] = (),
        approved_by: str | None = None,
        approval_reference: str | None = None,
        approved_at: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        **prohibited_later_build_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "change_code": change_code,
            "change_type": change_type,
            "title": title,
            "rationale": rationale,
            "current_specification_version": current_specification_version,
            "proposed_specification_version": proposed_specification_version,
            "review_status": review_status,
            "approval_status": approval_status,
            "requested_by": requested_by,
            "requested_effective_date": requested_effective_date,
            "linked_trial_execution_ids": list(linked_trial_execution_ids),
            "linked_defect_classification_ids": list(linked_defect_classification_ids),
            "linked_complaint_record_ids": list(linked_complaint_record_ids),
            "evidence_references": list(evidence_references),
            "approved_by": approved_by,
            "approval_reference": approval_reference,
            "approved_at": approved_at,
            "content_hash": content_hash.lower(),
            **prohibited_later_build_fields,
        }
        validation = validate_specification_change(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))

        identifier = new_id("specification-change")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            self._validate_links(connection, "trial_executions", "trial_execution_id", linked_trial_execution_ids, project_id)
            self._validate_links(connection, "defect_classifications", "defect_classification_id", linked_defect_classification_ids, project_id)
            self._validate_links(connection, "complaint_records", "complaint_record_id", linked_complaint_record_ids, project_id)

            connection.execute(
                """
                INSERT INTO specification_change_requests(
                    specification_change_request_id, project_id, change_code, change_type,
                    title, rationale, current_specification_version,
                    proposed_specification_version, review_status, approval_status,
                    requested_by, requested_effective_date, linked_trial_execution_ids_json,
                    linked_defect_classification_ids_json, linked_complaint_record_ids_json,
                    evidence_references_json, approved_by, approval_reference, approved_at,
                    metadata_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, change_code, change_type, title, rationale,
                    current_specification_version, proposed_specification_version,
                    review_status, approval_status, requested_by, requested_effective_date,
                    json.dumps(list(linked_trial_execution_ids), sort_keys=True),
                    json.dumps(list(linked_defect_classification_ids), sort_keys=True),
                    json.dumps(list(linked_complaint_record_ids), sort_keys=True),
                    json.dumps(list(evidence_references), sort_keys=True),
                    approved_by, approval_reference, approved_at,
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
                raise ValueError("Linked evidence must belong to the same project.")

    def get(self, identifier: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM specification_change_requests WHERE specification_change_request_id = ?",
                (identifier,),
            ).fetchone()
        if row is None:
            raise KeyError(identifier)
        result = dict(row)
        for column, key in (
            ("linked_trial_execution_ids_json", "linked_trial_execution_ids"),
            ("linked_defect_classification_ids_json", "linked_defect_classification_ids"),
            ("linked_complaint_record_ids_json", "linked_complaint_record_ids"),
            ("evidence_references_json", "evidence_references"),
            ("metadata_json", "metadata"),
        ):
            result[key] = json.loads(result.pop(column))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT specification_change_request_id FROM specification_change_requests WHERE project_id = ? ORDER BY created_at, specification_change_request_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Specification change requests are immutable; create a new record.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Specification change requests are immutable.")


class ImplementationControlRepository:
    """Immutable implementation authorization and verification records."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        change_request_id: str,
        implementation_code: str,
        implementation_site: str,
        implementation_owner: str,
        implementation_status: str,
        verification_status: str,
        evidence_references: Sequence[str],
        content_hash: str,
        planned_implementation_date: str | None = None,
        actual_implementation_date: str | None = None,
        authorized_by: str | None = None,
        authorization_reference: str | None = None,
        verified_by: str | None = None,
        verified_at: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        **prohibited_later_build_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "change_request_id": change_request_id,
            "implementation_code": implementation_code,
            "implementation_site": implementation_site,
            "implementation_owner": implementation_owner,
            "implementation_status": implementation_status,
            "verification_status": verification_status,
            "evidence_references": list(evidence_references),
            "planned_implementation_date": planned_implementation_date,
            "actual_implementation_date": actual_implementation_date,
            "authorized_by": authorized_by,
            "authorization_reference": authorization_reference,
            "verified_by": verified_by,
            "verified_at": verified_at,
            "content_hash": content_hash.lower(),
            **prohibited_later_build_fields,
        }
        validation = validate_implementation_control(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))

        identifier = new_id("implementation-control")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            change = connection.execute(
                "SELECT project_id, approval_status FROM specification_change_requests WHERE specification_change_request_id = ?",
                (change_request_id,),
            ).fetchone()
            if change is None:
                raise KeyError(change_request_id)
            if change["project_id"] != project_id:
                raise ValueError("Change request must belong to the same project.")
            if implementation_status in {"authorized", "in_progress", "implemented"} and change["approval_status"] != "approved":
                raise ValueError("Implementation authorization requires an approved change request.")

            connection.execute(
                """
                INSERT INTO implementation_controls(
                    implementation_control_id, project_id, change_request_id,
                    implementation_code, implementation_site, implementation_owner,
                    implementation_status, planned_implementation_date,
                    actual_implementation_date, verification_status,
                    evidence_references_json, authorized_by, authorization_reference,
                    verified_by, verified_at, metadata_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, change_request_id, implementation_code,
                    implementation_site, implementation_owner, implementation_status,
                    planned_implementation_date, actual_implementation_date,
                    verification_status, json.dumps(list(evidence_references), sort_keys=True),
                    authorized_by, authorization_reference, verified_by, verified_at,
                    json.dumps(dict(metadata or {}), sort_keys=True), content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, identifier: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM implementation_controls WHERE implementation_control_id = ?",
                (identifier,),
            ).fetchone()
        if row is None:
            raise KeyError(identifier)
        result = dict(row)
        result["evidence_references"] = json.loads(result.pop("evidence_references_json"))
        result["metadata"] = json.loads(result.pop("metadata_json"))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT implementation_control_id FROM implementation_controls WHERE project_id = ? ORDER BY created_at, implementation_control_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Implementation controls are immutable; create a new record.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Implementation controls are immutable.")
