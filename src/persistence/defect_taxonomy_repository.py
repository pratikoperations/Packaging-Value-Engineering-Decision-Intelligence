from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.defect_taxonomy import validate_complaint_record, validate_defect_classification
from src.persistence._utils import new_id
from src.persistence.database import Database


class DefectClassificationRepository:
    """Immutable, project-scoped packaging defect classifications."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        taxonomy_version: str,
        defect_code: str,
        packaging_level: str,
        material_family: str,
        defect_family: str,
        defect_mode: str,
        description: str,
        severity: str,
        occurrence_stage: str,
        review_status: str,
        reviewed_by: str,
        content_hash: str,
        evidence_references: Sequence[str] = (),
        trial_execution_id: str | None = None,
        sku: str | None = None,
        supplier: str | None = None,
        manufacturing_site: str | None = None,
        batch_or_shipment: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        **prohibited_later_build_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "taxonomy_version": taxonomy_version,
            "defect_code": defect_code,
            "packaging_level": packaging_level,
            "material_family": material_family,
            "defect_family": defect_family,
            "defect_mode": defect_mode,
            "description": description,
            "severity": severity,
            "occurrence_stage": occurrence_stage,
            "review_status": review_status,
            "reviewed_by": reviewed_by,
            "evidence_references": list(evidence_references),
            "content_hash": content_hash.lower(),
            **prohibited_later_build_fields,
        }
        validation = validate_defect_classification(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))

        identifier = new_id("defect-classification")
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            if trial_execution_id:
                execution = connection.execute(
                    "SELECT project_id FROM trial_executions WHERE trial_execution_id = ?",
                    (trial_execution_id,),
                ).fetchone()
                if execution is None:
                    raise KeyError(trial_execution_id)
                if execution["project_id"] != project_id:
                    raise ValueError("Trial execution must belong to the same project.")

            connection.execute(
                """
                INSERT INTO defect_classifications(
                    defect_classification_id, project_id, trial_execution_id,
                    taxonomy_version, defect_code, packaging_level, material_family,
                    defect_family, defect_mode, description, severity, occurrence_stage,
                    sku, supplier, manufacturing_site, batch_or_shipment,
                    evidence_references_json, review_status, reviewed_by, metadata_json,
                    content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, trial_execution_id, taxonomy_version, defect_code,
                    packaging_level, material_family, defect_family, defect_mode, description,
                    severity, occurrence_stage, sku, supplier, manufacturing_site,
                    batch_or_shipment, json.dumps(list(evidence_references), sort_keys=True),
                    review_status, reviewed_by, json.dumps(dict(metadata or {}), sort_keys=True),
                    content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, defect_classification_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM defect_classifications WHERE defect_classification_id = ?",
                (defect_classification_id,),
            ).fetchone()
        if row is None:
            raise KeyError(defect_classification_id)
        result = dict(row)
        result["evidence_references"] = json.loads(result.pop("evidence_references_json"))
        result["metadata"] = json.loads(result.pop("metadata_json"))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT defect_classification_id FROM defect_classifications WHERE project_id = ? ORDER BY created_at, defect_classification_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Defect classifications are immutable; create a new record.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Defect classifications are immutable.")


class ComplaintRecordRepository:
    """Immutable, project-scoped complaint intake and classification records."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        complaint_reference: str,
        complaint_source: str,
        received_date: str,
        description: str,
        containment_status: str,
        review_status: str,
        reviewed_by: str,
        content_hash: str,
        taxonomy_version: str,
        linked_defect_classification_ids: Sequence[str] = (),
        evidence_references: Sequence[str] = (),
        complaint_channel: str | None = None,
        affected_quantity: float | None = None,
        quantity_unit: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        **prohibited_later_build_fields: Any,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "complaint_reference": complaint_reference,
            "complaint_source": complaint_source,
            "received_date": received_date,
            "description": description,
            "containment_status": containment_status,
            "review_status": review_status,
            "reviewed_by": reviewed_by,
            "linked_defect_codes": list(linked_defect_classification_ids),
            "evidence_references": list(evidence_references),
            "affected_quantity": affected_quantity,
            "quantity_unit": quantity_unit,
            "content_hash": content_hash.lower(),
            **prohibited_later_build_fields,
        }
        validation = validate_complaint_record(payload)
        if not validation.is_valid:
            raise ValueError("; ".join(f"{i.field}: {i.message}" for i in validation.issues))

        identifier = new_id("complaint-record")
        linked_ids = list(linked_defect_classification_ids)
        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            for defect_id in linked_ids:
                defect = connection.execute(
                    "SELECT project_id FROM defect_classifications WHERE defect_classification_id = ?",
                    (defect_id,),
                ).fetchone()
                if defect is None:
                    raise KeyError(defect_id)
                if defect["project_id"] != project_id:
                    raise ValueError("Linked defect classification must belong to the same project.")

            connection.execute(
                """
                INSERT INTO complaint_records(
                    complaint_record_id, project_id, complaint_reference, complaint_source,
                    complaint_channel, received_date, description, taxonomy_version,
                    linked_defect_classification_ids_json, affected_quantity, quantity_unit,
                    containment_status, evidence_references_json, review_status, reviewed_by,
                    metadata_json, content_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, complaint_reference, complaint_source,
                    complaint_channel, received_date, description, taxonomy_version,
                    json.dumps(linked_ids, sort_keys=True), affected_quantity, quantity_unit,
                    containment_status, json.dumps(list(evidence_references), sort_keys=True),
                    review_status, reviewed_by, json.dumps(dict(metadata or {}), sort_keys=True),
                    content_hash.lower(),
                ),
            )
        return self.get(identifier)

    def get(self, complaint_record_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM complaint_records WHERE complaint_record_id = ?",
                (complaint_record_id,),
            ).fetchone()
        if row is None:
            raise KeyError(complaint_record_id)
        result = dict(row)
        result["linked_defect_classification_ids"] = json.loads(
            result.pop("linked_defect_classification_ids_json")
        )
        result["evidence_references"] = json.loads(result.pop("evidence_references_json"))
        result["metadata"] = json.loads(result.pop("metadata_json"))
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT complaint_record_id FROM complaint_records WHERE project_id = ? ORDER BY created_at, complaint_record_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Complaint records are immutable; create a new record.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Complaint records are immutable.")
