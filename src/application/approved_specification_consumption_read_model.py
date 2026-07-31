from __future__ import annotations

from src.application.approved_specification_consumption_service import (
    ApprovedSpecificationConsumptionError,
)
from src.domain.approved_specification_consumption import (
    ApprovedSpecificationConsumptionEnvelope,
    ConsumptionAuthorization,
    GovernedConsumptionHandoff,
)
from src.persistence.approved_specification_consumption_repository import (
    ApprovedSpecificationConsumptionPersistenceError,
    ApprovedSpecificationConsumptionRepository,
)


class ApprovedSpecificationConsumptionReadModel:
    """Project-scoped read boundary for immutable consumption records."""

    def __init__(
        self, repository: ApprovedSpecificationConsumptionRepository
    ) -> None:
        self.repository = repository

    def get_envelope(
        self, envelope_id: str, *, project_id: str
    ) -> ApprovedSpecificationConsumptionEnvelope:
        project_id = self._project(project_id)
        envelope_id = self._required(
            envelope_id, "envelope_required", "Select a governed consumption envelope."
        )
        try:
            return self.repository.get_envelope(envelope_id, project_id=project_id)
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._error(error) from error

    def get_envelope_for_snapshot(
        self,
        snapshot_id: str,
        *,
        project_id: str,
        consumption_contract_version: str,
    ) -> ApprovedSpecificationConsumptionEnvelope | None:
        project_id = self._project(project_id)
        snapshot_id = self._required(
            snapshot_id, "snapshot_required", "Select an approved specification snapshot."
        )
        consumption_contract_version = self._required(
            consumption_contract_version,
            "contract_version_required",
            "A consumption contract version is required.",
        )
        try:
            return self.repository.get_envelope_for_snapshot(
                snapshot_id,
                project_id=project_id,
                consumption_contract_version=consumption_contract_version,
            )
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._error(error) from error

    def list_envelopes_for_project(
        self, project_id: str
    ) -> list[ApprovedSpecificationConsumptionEnvelope]:
        project_id = self._project(project_id)
        try:
            return self.repository.list_envelopes_for_project(project_id)
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._error(error) from error

    def get_authorization(
        self, authorization_id: str, *, project_id: str
    ) -> ConsumptionAuthorization:
        project_id = self._project(project_id)
        authorization_id = self._required(
            authorization_id,
            "authorization_required",
            "Select a governed consumption authorization.",
        )
        try:
            return self.repository.get_authorization(
                authorization_id, project_id=project_id
            )
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._error(error) from error

    def list_authorizations_for_snapshot(
        self, snapshot_id: str, *, project_id: str
    ) -> list[ConsumptionAuthorization]:
        project_id = self._project(project_id)
        snapshot_id = self._required(
            snapshot_id, "snapshot_required", "Select an approved specification snapshot."
        )
        try:
            return self.repository.list_authorizations_for_snapshot(
                snapshot_id, project_id=project_id
            )
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._error(error) from error

    def list_authorizations_for_project(
        self, project_id: str
    ) -> list[ConsumptionAuthorization]:
        project_id = self._project(project_id)
        try:
            return self.repository.list_authorizations_for_project(project_id)
        except ApprovedSpecificationConsumptionPersistenceError as error:
            raise self._error(error) from error

    def get_authorized_envelope(
        self, authorization_id: str, *, project_id: str
    ) -> ApprovedSpecificationConsumptionEnvelope:
        authorization = self.get_authorization(
            authorization_id, project_id=project_id
        )
        envelope = self.get_envelope(
            authorization.envelope_id, project_id=project_id
        )
        try:
            GovernedConsumptionHandoff(envelope, authorization)
        except ValueError as error:
            raise ApprovedSpecificationConsumptionError(
                "authorized_handoff_integrity_failure",
                "The authorized governed handoff failed lineage verification.",
            ) from error
        return envelope

    @classmethod
    def _project(cls, project_id: str) -> str:
        return cls._required(
            project_id,
            "project_required",
            "Select a project before loading governed consumption records.",
        )

    @staticmethod
    def _required(value: str, code: str, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ApprovedSpecificationConsumptionError(code, message)
        return normalized

    @staticmethod
    def _error(
        error: ApprovedSpecificationConsumptionPersistenceError,
    ) -> ApprovedSpecificationConsumptionError:
        return ApprovedSpecificationConsumptionError(error.code, error.message)
