from __future__ import annotations

import json
from typing import Any, Mapping, Sequence

from src.drawing_evidence import validate_drawing_evidence
from src.persistence._utils import new_id
from src.persistence.database import Database


class DrawingEvidenceRepository:
    """Project-scoped, immutable drawing/CAD evidence records with supersession control."""

    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        project_id: str,
        document_type: str,
        document_number: str,
        title: str,
        revision: str,
        classification: str,
        file_format: str,
        source_reference: str,
        source_classification: str,
        validation_status: str,
        approval_status: str,
        content_hash: str,
        sku: str | None = None,
        supplier: str | None = None,
        manufacturing_site: str | None = None,
        specification_version: str | None = None,
        issue_date: str | None = None,
        effective_date: str | None = None,
        supersedes_id: str | None = None,
        related_document_ids: Sequence[str] = (),
        trial_applicability: Sequence[str] = (),
        metadata: Mapping[str, Any] | None = None,
        geometry_interpreted: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "project_id": project_id,
            "document_type": document_type,
            "document_number": document_number,
            "title": title,
            "revision": revision,
            "classification": classification,
            "file_format": file_format.lower(),
            "source_reference": source_reference,
            "source_classification": source_classification,
            "validation_status": validation_status,
            "approval_status": approval_status,
            "content_hash": content_hash.lower(),
            "issue_date": issue_date,
            "effective_date": effective_date,
            "geometry_interpreted": geometry_interpreted,
        }
        validation = validate_drawing_evidence(payload)
        if not validation.is_valid:
            details = "; ".join(f"{issue.field}: {issue.message}" for issue in validation.issues)
            raise ValueError(details)

        identifier = new_id("drawing-evidence")
        related = list(related_document_ids)
        trials = list(trial_applicability)
        extra = dict(metadata or {})

        with self.database.transaction() as connection:
            project = connection.execute(
                "SELECT archived_at FROM projects WHERE project_id = ?", (project_id,)
            ).fetchone()
            if project is None:
                raise KeyError(project_id)
            if project["archived_at"] is not None:
                raise ValueError("Archived projects are read-only.")

            if supersedes_id is not None:
                superseded = connection.execute(
                    "SELECT project_id, document_number FROM drawing_evidence WHERE drawing_evidence_id = ?",
                    (supersedes_id,),
                ).fetchone()
                if superseded is None:
                    raise KeyError(supersedes_id)
                if superseded["project_id"] != project_id:
                    raise ValueError("Superseded drawing evidence must belong to the same project.")
                if superseded["document_number"] != document_number:
                    raise ValueError("Supersession requires the same document number.")

            for related_id in related:
                row = connection.execute(
                    "SELECT project_id FROM drawing_evidence WHERE drawing_evidence_id = ?", (related_id,)
                ).fetchone()
                if row is None:
                    raise KeyError(related_id)
                if row["project_id"] != project_id:
                    raise ValueError("Related drawing evidence must belong to the same project.")

            connection.execute(
                """
                INSERT INTO drawing_evidence(
                    drawing_evidence_id, project_id, sku, supplier, manufacturing_site,
                    specification_version, document_type, document_number, title, revision,
                    classification, file_format, source_reference, source_classification,
                    validation_status, approval_status, issue_date, effective_date,
                    supersedes_id, related_document_ids_json, trial_applicability_json,
                    metadata_json, content_hash, geometry_interpreted
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    identifier, project_id, sku, supplier, manufacturing_site,
                    specification_version, document_type, document_number, title, revision,
                    classification, file_format.lower(), source_reference, source_classification,
                    validation_status, approval_status, issue_date, effective_date,
                    supersedes_id, json.dumps(related, sort_keys=True), json.dumps(trials, sort_keys=True),
                    json.dumps(extra, sort_keys=True), content_hash.lower(), int(geometry_interpreted),
                ),
            )
        return self.get(identifier)

    def get(self, drawing_evidence_id: str) -> dict[str, Any]:
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM drawing_evidence WHERE drawing_evidence_id = ?", (drawing_evidence_id,)
            ).fetchone()
        if row is None:
            raise KeyError(drawing_evidence_id)
        result = dict(row)
        for field in ("related_document_ids_json", "trial_applicability_json", "metadata_json"):
            result[field.removesuffix("_json")] = json.loads(result.pop(field))
        result["geometry_interpreted"] = bool(result["geometry_interpreted"])
        return result

    def list_for_project(self, project_id: str) -> list[dict[str, Any]]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT drawing_evidence_id FROM drawing_evidence WHERE project_id = ? ORDER BY created_at, drawing_evidence_id",
                (project_id,),
            ).fetchall()
        return [self.get(row[0]) for row in rows]

    def current_revision(self, project_id: str, document_number: str) -> dict[str, Any] | None:
        with self.database.connect() as connection:
            row = connection.execute(
                """
                SELECT d.drawing_evidence_id
                FROM drawing_evidence d
                WHERE d.project_id = ? AND d.document_number = ?
                  AND NOT EXISTS (
                    SELECT 1 FROM drawing_evidence replacement
                    WHERE replacement.supersedes_id = d.drawing_evidence_id
                  )
                ORDER BY d.created_at DESC, d.drawing_evidence_id DESC
                LIMIT 1
                """,
                (project_id, document_number),
            ).fetchone()
        return self.get(row[0]) if row else None

    def update(self, *_: Any, **__: Any) -> None:
        raise ValueError("Drawing evidence is immutable; create a superseding revision.")

    def delete(self, *_: Any, **__: Any) -> None:
        raise ValueError("Drawing evidence is immutable.")
