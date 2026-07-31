from __future__ import annotations

import json
import sqlite3
from typing import Any

from src.domain.approved_specification_consumption import (
    ApprovedSpecificationConsumptionEnvelope,
    ApprovedSpecificationConsumptionValue,
    AuthorizedConsumptionPurpose,
    ConsumptionAuthorization,
    approved_specification_consumption_envelope_hash,
)
from src.persistence.approved_specification_consumption_migration import (
    initialize_approved_specification_consumption_schema,
)
from src.persistence.database import Database


class ApprovedSpecificationConsumptionPersistenceError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ApprovedSpecificationConsumptionRepository:
    def __init__(self, database: Database) -> None:
        self.database = database
        initialize_approved_specification_consumption_schema(database)

    def create_envelope(self, envelope: ApprovedSpecificationConsumptionEnvelope) -> ApprovedSpecificationConsumptionEnvelope:
        self._verify_envelope_hash(envelope)
        try:
            with self.database.transaction() as connection:
                self._validate_envelope_lineage(connection, envelope)
                connection.execute(
                    """INSERT INTO approved_specification_consumption_envelopes(
                    envelope_id, project_id, snapshot_id, review_id, source_review_revision_id,
                    source_review_revision_number, existing_dataset_id, proposed_dataset_id,
                    snapshot_schema_version, consumption_contract_version, approved_values_json,
                    excluded_fields_json, snapshot_content_hash, envelope_content_hash, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        envelope.envelope_id, envelope.project_id, envelope.snapshot_id,
                        envelope.review_id, envelope.source_review_revision_id,
                        envelope.source_review_revision_number, envelope.existing_dataset_id,
                        envelope.proposed_dataset_id, envelope.snapshot_schema_version,
                        envelope.consumption_contract_version,
                        self._approved_values_json(envelope.approved_values),
                        self._excluded_fields_json(envelope.excluded_fields),
                        envelope.snapshot_content_hash, envelope.envelope_content_hash,
                        envelope.created_at,
                    ),
                )
        except sqlite3.IntegrityError as error:
            code = "duplicate_envelope" if "UNIQUE constraint failed" in str(error) else "envelope_integrity_error"
            raise ApprovedSpecificationConsumptionPersistenceError(code, "The governed consumption envelope could not be persisted safely.") from error
        return self.get_envelope(envelope.envelope_id, project_id=envelope.project_id)

    def create_authorization(self, authorization: ConsumptionAuthorization) -> ConsumptionAuthorization:
        try:
            with self.database.transaction() as connection:
                self._validate_authorization_lineage(connection, authorization)
                connection.execute(
                    """INSERT INTO approved_specification_consumption_authorizations(
                    authorization_id, project_id, snapshot_id, envelope_id, purpose,
                    actor_reference, business_reason, snapshot_content_hash,
                    envelope_content_hash, authorization_schema_version, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        authorization.authorization_id, authorization.project_id,
                        authorization.snapshot_id, authorization.envelope_id,
                        authorization.purpose.value, authorization.actor_reference.strip(),
                        authorization.business_reason.strip(), authorization.snapshot_content_hash,
                        authorization.envelope_content_hash,
                        authorization.authorization_schema_version, authorization.created_at,
                    ),
                )
        except sqlite3.IntegrityError as error:
            code = "duplicate_authorization" if "UNIQUE constraint failed" in str(error) else "authorization_integrity_error"
            raise ApprovedSpecificationConsumptionPersistenceError(code, "The governed consumption authorization could not be persisted safely.") from error
        return self.get_authorization(authorization.authorization_id, project_id=authorization.project_id)

    def get_envelope(self, envelope_id: str, *, project_id: str) -> ApprovedSpecificationConsumptionEnvelope:
        self._require_project(project_id)
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM approved_specification_consumption_envelopes WHERE envelope_id = ? AND project_id = ?",
                (envelope_id, project_id),
            ).fetchone()
        if row is None:
            raise ApprovedSpecificationConsumptionPersistenceError("envelope_not_found", "The governed consumption envelope was not found in this project.")
        return self._decode_envelope(dict(row))

    def get_envelope_for_snapshot(self, snapshot_id: str, *, project_id: str, consumption_contract_version: str) -> ApprovedSpecificationConsumptionEnvelope | None:
        self._require_project(project_id)
        with self.database.connect() as connection:
            row = connection.execute(
                """SELECT * FROM approved_specification_consumption_envelopes
                WHERE snapshot_id = ? AND project_id = ? AND consumption_contract_version = ?""",
                (snapshot_id, project_id, consumption_contract_version),
            ).fetchone()
        return None if row is None else self._decode_envelope(dict(row))

    def list_envelopes_for_project(self, project_id: str) -> list[ApprovedSpecificationConsumptionEnvelope]:
        self._require_project(project_id)
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM approved_specification_consumption_envelopes WHERE project_id = ? ORDER BY created_at, envelope_id",
                (project_id,),
            ).fetchall()
        return [self._decode_envelope(dict(row)) for row in rows]

    def get_authorization(self, authorization_id: str, *, project_id: str) -> ConsumptionAuthorization:
        self._require_project(project_id)
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM approved_specification_consumption_authorizations WHERE authorization_id = ? AND project_id = ?",
                (authorization_id, project_id),
            ).fetchone()
        if row is None:
            raise ApprovedSpecificationConsumptionPersistenceError("authorization_not_found", "The governed consumption authorization was not found in this project.")
        return self._decode_authorization(dict(row))

    def list_authorizations_for_snapshot(self, snapshot_id: str, *, project_id: str) -> list[ConsumptionAuthorization]:
        self._require_project(project_id)
        with self.database.connect() as connection:
            rows = connection.execute(
                """SELECT * FROM approved_specification_consumption_authorizations
                WHERE snapshot_id = ? AND project_id = ? ORDER BY created_at, authorization_id""",
                (snapshot_id, project_id),
            ).fetchall()
        return [self._decode_authorization(dict(row)) for row in rows]

    def list_authorizations_for_project(self, project_id: str) -> list[ConsumptionAuthorization]:
        self._require_project(project_id)
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM approved_specification_consumption_authorizations WHERE project_id = ? ORDER BY created_at, authorization_id",
                (project_id,),
            ).fetchall()
        return [self._decode_authorization(dict(row)) for row in rows]

    def update_envelope(self, envelope_id: str, **changes: Any) -> None:
        raise ApprovedSpecificationConsumptionPersistenceError("immutable_envelope", "Governed consumption envelopes cannot be updated.")

    def delete_envelope(self, envelope_id: str) -> None:
        raise ApprovedSpecificationConsumptionPersistenceError("immutable_envelope", "Governed consumption envelopes cannot be deleted.")

    def update_authorization(self, authorization_id: str, **changes: Any) -> None:
        raise ApprovedSpecificationConsumptionPersistenceError("immutable_authorization", "Governed consumption authorizations cannot be updated.")

    def delete_authorization(self, authorization_id: str) -> None:
        raise ApprovedSpecificationConsumptionPersistenceError("immutable_authorization", "Governed consumption authorizations cannot be deleted.")

    def _require_project(self, project_id: str) -> None:
        if not project_id.strip():
            raise ApprovedSpecificationConsumptionPersistenceError("project_required", "A project scope is required.")
        with self.database.connect() as connection:
            row = connection.execute("SELECT project_id FROM projects WHERE project_id = ?", (project_id,)).fetchone()
        if row is None:
            raise ApprovedSpecificationConsumptionPersistenceError("unknown_project", "The project does not exist.")

    @staticmethod
    def _validate_envelope_lineage(connection: sqlite3.Connection, envelope: ApprovedSpecificationConsumptionEnvelope) -> None:
        project = connection.execute("SELECT archived_at FROM projects WHERE project_id = ?", (envelope.project_id,)).fetchone()
        if project is None:
            raise ApprovedSpecificationConsumptionPersistenceError("unknown_project", "The project does not exist.")
        if project["archived_at"] is not None:
            raise ApprovedSpecificationConsumptionPersistenceError("archived_project", "Archived projects are read-only.")
        snapshot = connection.execute("SELECT * FROM approved_specification_snapshots WHERE snapshot_id = ?", (envelope.snapshot_id,)).fetchone()
        if snapshot is None:
            raise ApprovedSpecificationConsumptionPersistenceError("unknown_snapshot", "The approved specification snapshot does not exist.")
        expected = (envelope.project_id, envelope.review_id, envelope.source_review_revision_id,
                    envelope.source_review_revision_number, envelope.existing_dataset_id,
                    envelope.proposed_dataset_id, envelope.snapshot_schema_version,
                    envelope.snapshot_content_hash)
        actual = (snapshot["project_id"], snapshot["review_id"], snapshot["source_review_revision_id"],
                  int(snapshot["source_review_revision_number"]), snapshot["existing_dataset_id"],
                  snapshot["proposed_dataset_id"], snapshot["snapshot_schema_version"], snapshot["content_hash"])
        if actual != expected:
            raise ApprovedSpecificationConsumptionPersistenceError("invalid_snapshot_lineage", "Envelope lineage does not match the approved specification snapshot.")

    @staticmethod
    def _validate_authorization_lineage(connection: sqlite3.Connection, authorization: ConsumptionAuthorization) -> None:
        project = connection.execute("SELECT archived_at FROM projects WHERE project_id = ?", (authorization.project_id,)).fetchone()
        if project is None:
            raise ApprovedSpecificationConsumptionPersistenceError("unknown_project", "The project does not exist.")
        if project["archived_at"] is not None:
            raise ApprovedSpecificationConsumptionPersistenceError("archived_project", "Archived projects are read-only.")
        envelope = connection.execute("SELECT project_id, snapshot_id, snapshot_content_hash, envelope_content_hash FROM approved_specification_consumption_envelopes WHERE envelope_id = ?", (authorization.envelope_id,)).fetchone()
        expected = (authorization.project_id, authorization.snapshot_id, authorization.snapshot_content_hash, authorization.envelope_content_hash)
        actual = None if envelope is None else (envelope["project_id"], envelope["snapshot_id"], envelope["snapshot_content_hash"], envelope["envelope_content_hash"])
        if actual != expected:
            raise ApprovedSpecificationConsumptionPersistenceError("invalid_authorization_lineage", "Authorization lineage does not match the governed consumption envelope.")

    @staticmethod
    def _approved_values_json(values: tuple[ApprovedSpecificationConsumptionValue, ...]) -> str:
        return json.dumps([{"field_key": item.field_key, "value": item.value, "source": item.source} for item in values], sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

    @staticmethod
    def _excluded_fields_json(fields: tuple[str, ...]) -> str:
        return json.dumps(list(fields), sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

    @classmethod
    def _decode_envelope(cls, row: dict[str, Any]) -> ApprovedSpecificationConsumptionEnvelope:
        try:
            values = tuple(ApprovedSpecificationConsumptionValue(item["field_key"], item["value"], item["source"]) for item in json.loads(row["approved_values_json"]))
            envelope = ApprovedSpecificationConsumptionEnvelope(
                envelope_id=row["envelope_id"], project_id=row["project_id"], snapshot_id=row["snapshot_id"],
                review_id=row["review_id"], source_review_revision_id=row["source_review_revision_id"],
                source_review_revision_number=int(row["source_review_revision_number"]),
                existing_dataset_id=row["existing_dataset_id"], proposed_dataset_id=row["proposed_dataset_id"],
                snapshot_schema_version=row["snapshot_schema_version"],
                consumption_contract_version=row["consumption_contract_version"], approved_values=values,
                excluded_fields=tuple(json.loads(row["excluded_fields_json"])),
                snapshot_content_hash=row["snapshot_content_hash"], envelope_content_hash=row["envelope_content_hash"],
                created_at=row["created_at"],
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
            raise ApprovedSpecificationConsumptionPersistenceError("envelope_content_invalid", "Stored governed consumption envelope content is invalid.") from error
        cls._verify_envelope_hash(envelope)
        return envelope

    @staticmethod
    def _decode_authorization(row: dict[str, Any]) -> ConsumptionAuthorization:
        try:
            return ConsumptionAuthorization(
                authorization_id=row["authorization_id"], project_id=row["project_id"],
                snapshot_id=row["snapshot_id"], envelope_id=row["envelope_id"],
                purpose=AuthorizedConsumptionPurpose(row["purpose"]), actor_reference=row["actor_reference"],
                business_reason=row["business_reason"], snapshot_content_hash=row["snapshot_content_hash"],
                envelope_content_hash=row["envelope_content_hash"],
                authorization_schema_version=row["authorization_schema_version"], created_at=row["created_at"],
            )
        except (KeyError, TypeError, ValueError) as error:
            raise ApprovedSpecificationConsumptionPersistenceError("authorization_content_invalid", "Stored governed consumption authorization content is invalid.") from error

    @staticmethod
    def _verify_envelope_hash(envelope: ApprovedSpecificationConsumptionEnvelope) -> None:
        expected = approved_specification_consumption_envelope_hash(
            project_id=envelope.project_id, snapshot_id=envelope.snapshot_id, review_id=envelope.review_id,
            source_review_revision_id=envelope.source_review_revision_id,
            source_review_revision_number=envelope.source_review_revision_number,
            existing_dataset_id=envelope.existing_dataset_id, proposed_dataset_id=envelope.proposed_dataset_id,
            snapshot_schema_version=envelope.snapshot_schema_version, approved_values=envelope.approved_values,
            excluded_fields=envelope.excluded_fields, snapshot_content_hash=envelope.snapshot_content_hash,
            consumption_contract_version=envelope.consumption_contract_version,
        )
        if envelope.envelope_content_hash != expected:
            raise ApprovedSpecificationConsumptionPersistenceError("envelope_hash_mismatch", "Governed consumption envelope failed integrity verification.")
