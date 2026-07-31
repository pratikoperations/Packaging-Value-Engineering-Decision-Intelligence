from __future__ import annotations

from datetime import datetime, timezone

from src.application.approved_specification_read_model import ApprovedSpecificationReadModel
from src.application.approved_specification_snapshot_service import (
    ApprovedSpecificationSnapshotError,
)
from src.domain.approved_specification import APPROVED_SPECIFICATION_SCHEMA_VERSION
from src.domain.approved_specification_consumption import (
    AUTHORIZATION_SCHEMA_VERSION,
    CONSUMPTION_CONTRACT_VERSION,
    ApprovedSpecificationConsumptionEnvelope,
    ApprovedSpecificationConsumptionValue,
    AuthorizedConsumptionPurpose,
    ConsumptionAuthorization,
    GovernedConsumptionHandoff,
    approved_specification_consumption_envelope_hash,
)
from src.persistence._utils import new_id
from src.persistence.approved_specification_consumption_repository import (
    ApprovedSpecificationConsumptionPersistenceError,
    ApprovedSpecificationConsumptionRepository,
)


class ApprovedSpecificationConsumptionError(ValueError):
    """Presentation-safe application error for governed snapshot consumption."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class ApprovedSpecificationConsumptionService:
    """Create immutable governed handoffs from approved snapshots only."""

    def __init__(
        self,
        snapshot_read_model: ApprovedSpecificationReadModel,
        repository: ApprovedSpecificationConsumptionRepository,
    ) -> None:
        self.snapshot_read_model = snapshot_read_model
        self.repository = repository

    def create_handoff(
        self,
        *,
        project_id: str,
        snapshot_id: str,
        purpose: AuthorizedConsumptionPurpose | str,
        actor_reference: str,
        business_reason: str,
    ) -> GovernedConsumptionHandoff:
        project_id = self._required(
            project_id, "project_required", "Select a project before creating a handoff."
        )
        snapshot_id = self._required(
            snapshot_id, "snapshot_required", "Select an approved specification snapshot."
        )
        actor_reference = self._required(
            actor_reference, "actor_required", "A non-empty actor reference is required."
        )
        business_reason = self._required(
            business_reason,
            "business_reason_required",
            "A non-empty business reason is required.",
        )
        purpose = self._purpose(purpose)

        try:
            snapshot = self.snapshot_read_model.get_snapshot(
                snapshot_id, project_id=project_id
            )
        except ApprovedSpecificationSnapshotError as error:
            raise ApprovedSpecificationConsumptionError(
                error.code, error.message
            ) from error

        if snapshot.snapshot_schema_version != APPROVED_SPECIFICATION_SCHEMA_VERSION:
            raise ApprovedSpecificationConsumptionError(
                "unsupported_snapshot_schema",
                "The approved specification snapshot schema is not supported for consumption.",
            )

        values = tuple(
            ApprovedSpecificationConsumptionValue(
                field_key=item.field_key,
                value=item.value,
                source=item.source,
            )
            for item in snapshot.approved_values
        )
        digest = approved_specification_consumption_envelope_hash(
            project_id=snapshot.project_id,
            snapshot_id=snapshot.snapshot_id,
            review_id=snapshot.review_id,
            source_review_revision_id=snapshot.source_review_revision_id,
            source_review_revision_number=snapshot.source_review_revision_number,
            existing_dataset_id=snapshot.existing_dataset_id,
            proposed_dataset_id=snapshot.proposed_dataset_id,
            snapshot_schema_version=snapshot.snapshot_schema_version,
            approved_values=values,
            excluded_fields=snapshot.excluded_fields,
            snapshot_content_hash=snapshot.content_hash,
            consumption_contract_version=CONSUMPTION_CONTRACT_VERSION,
        )
        envelope_candidate = ApprovedSpecificationConsumptionEnvelope(
            envelope_id=new_id("approved-specification-consumption"),
            project_id=snapshot.project_id,
            snapshot_id=snapshot.snapshot_id,
            review_id=snapshot.review_id,
            source_review_revision_id=snapshot.source_review_revision_id,
            source_review_revision_number=snapshot.source_review_revision_number,
            existing_dataset_id=snapshot.existing_dataset_id,
            proposed_dataset_id=snapshot.proposed_dataset_id,
            snapshot_schema_version=snapshot.snapshot_schema_version,
            consumption_contract_version=CONSUMPTION_CONTRACT_VERSION,
            approved_values=values,
            excluded_fields=snapshot.excluded_fields,
            snapshot_content_hash=snapshot.content_hash,
            envelope_content_hash=digest,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        envelope = self._load_or_create_envelope(envelope_candidate)

        authorization_candidate = ConsumptionAuthorization(
            authorization_id=new_id("consumption-authorization"),
            project_id=envelope.project_id,
            snapshot_id=envelope.snapshot_id,
            envelope_id=envelope.envelope_id,
            purpose=purpose,
            actor_reference=actor_reference,
            business_reason=business_reason,
            snapshot_content_hash=envelope.snapshot_content_hash,
            envelope_content_hash=envelope.envelope_content_hash,
            authorization_schema_version=AUTHORIZATION_SCHEMA_VERSION,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        authorization = self._load_or_create_authorization(
            authorization_candidate
        )
        try:
            return GovernedConsumptionHandoff(envelope, authorization)
        except ValueError as error:
            raise ApprovedSpecificationConsumptionError(
                "handoff_integrity_failure",
                "The governed consumption handoff failed lineage verification.",
            ) from error

    def _load_or_create_envelope(
        self,
        candidate: ApprovedSpecificationConsumptionEnvelope,
    ) -> ApprovedSpecificationConsumptionEnvelope:
        try:
            existing = self.repository.get_envelope_for_snapshot(
                candidate.snapshot_id,
                project_id=candidate.project_id,
                consumption_contract_version=candidate.consumption_contract_version,
            )
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._persistence_error(error) from error
        if existing is not None:
            return self._resolve_envelope_retry(existing, candidate)
        try:
            return self.repository.create_envelope(candidate)
        except ApprovedSpecificationConsumptionPersistenceError as error:
            if error.code == "duplicate_envelope":
                try:
                    existing = self.repository.get_envelope_for_snapshot(
                        candidate.snapshot_id,
                        project_id=candidate.project_id,
                        consumption_contract_version=candidate.consumption_contract_version,
                    )
                except ApprovedSpecificationConsumptionPersistenceError as reload_error:
                    raise self._persistence_error(reload_error) from reload_error
                if existing is not None:
                    return self._resolve_envelope_retry(existing, candidate)
            raise self._persistence_error(error) from error

    def _load_or_create_authorization(
        self,
        candidate: ConsumptionAuthorization,
    ) -> ConsumptionAuthorization:
        try:
            existing_items = self.repository.list_authorizations_for_snapshot(
                candidate.snapshot_id, project_id=candidate.project_id
            )
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._persistence_error(error) from error
        existing = self._matching_authorization(existing_items, candidate)
        if existing is not None:
            return self._resolve_authorization_retry(existing, candidate)
        try:
            return self.repository.create_authorization(candidate)
        except ApprovedSpecificationConsumptionPersistenceError as error:
            if error.code == "duplicate_authorization":
                try:
                    existing_items = self.repository.list_authorizations_for_snapshot(
                        candidate.snapshot_id, project_id=candidate.project_id
                    )
                except ApprovedSpecificationConsumptionPersistenceError as reload_error:
                    raise self._persistence_error(reload_error) from reload_error
                existing = self._matching_authorization(existing_items, candidate)
                if existing is not None:
                    return self._resolve_authorization_retry(existing, candidate)
            raise self._persistence_error(error) from error

    @staticmethod
    def _resolve_envelope_retry(
        existing: ApprovedSpecificationConsumptionEnvelope,
        candidate: ApprovedSpecificationConsumptionEnvelope,
    ) -> ApprovedSpecificationConsumptionEnvelope:
        identical = (
            existing.project_id == candidate.project_id
            and existing.snapshot_id == candidate.snapshot_id
            and existing.review_id == candidate.review_id
            and existing.source_review_revision_id
            == candidate.source_review_revision_id
            and existing.source_review_revision_number
            == candidate.source_review_revision_number
            and existing.existing_dataset_id == candidate.existing_dataset_id
            and existing.proposed_dataset_id == candidate.proposed_dataset_id
            and existing.snapshot_schema_version
            == candidate.snapshot_schema_version
            and existing.consumption_contract_version
            == candidate.consumption_contract_version
            and existing.approved_values == candidate.approved_values
            and existing.excluded_fields == candidate.excluded_fields
            and existing.snapshot_content_hash == candidate.snapshot_content_hash
            and existing.envelope_content_hash == candidate.envelope_content_hash
        )
        if identical:
            return existing
        raise ApprovedSpecificationConsumptionError(
            "conflicting_envelope",
            "A governed consumption envelope already exists with conflicting content or lineage.",
        )

    @staticmethod
    def _matching_authorization(
        existing_items: list[ConsumptionAuthorization],
        candidate: ConsumptionAuthorization,
    ) -> ConsumptionAuthorization | None:
        for item in existing_items:
            if (
                item.purpose == candidate.purpose
                and item.actor_reference == candidate.actor_reference
                and item.business_reason == candidate.business_reason
                and item.envelope_id == candidate.envelope_id
                and item.envelope_content_hash == candidate.envelope_content_hash
            ):
                return item
        return None

    @staticmethod
    def _resolve_authorization_retry(
        existing: ConsumptionAuthorization,
        candidate: ConsumptionAuthorization,
    ) -> ConsumptionAuthorization:
        identical = (
            existing.project_id == candidate.project_id
            and existing.snapshot_id == candidate.snapshot_id
            and existing.envelope_id == candidate.envelope_id
            and existing.purpose == candidate.purpose
            and existing.actor_reference == candidate.actor_reference
            and existing.business_reason == candidate.business_reason
            and existing.snapshot_content_hash == candidate.snapshot_content_hash
            and existing.envelope_content_hash == candidate.envelope_content_hash
            and existing.authorization_schema_version
            == candidate.authorization_schema_version
        )
        if identical:
            return existing
        raise ApprovedSpecificationConsumptionError(
            "conflicting_authorization",
            "A governed consumption authorization already exists with conflicting content.",
        )

    @staticmethod
    def _purpose(
        purpose: AuthorizedConsumptionPurpose | str,
    ) -> AuthorizedConsumptionPurpose:
        if isinstance(purpose, AuthorizedConsumptionPurpose):
            return purpose
        try:
            return AuthorizedConsumptionPurpose(str(purpose).strip())
        except ValueError as error:
            raise ApprovedSpecificationConsumptionError(
                "unsupported_consumption_purpose",
                "Select a supported governed consumption purpose.",
            ) from error

    @staticmethod
    def _required(value: str, code: str, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ApprovedSpecificationConsumptionError(code, message)
        return normalized

    @staticmethod
    def _persistence_error(
        error: ApprovedSpecificationConsumptionPersistenceError,
    ) -> ApprovedSpecificationConsumptionError:
        return ApprovedSpecificationConsumptionError(error.code, error.message)
