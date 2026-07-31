from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Mapping


CONSUMPTION_CONTRACT_VERSION = "1.0"
AUTHORIZATION_SCHEMA_VERSION = "1.0"
APPROVED_VALUE_SOURCES = {
    "accepted_proposed",
    "corrected",
    "retained_existing",
    "unchanged",
}


class ApprovedSpecificationConsumptionError(ValueError):
    """Fail-closed domain error for governed approved-specification consumption."""


class AuthorizedConsumptionPurpose(str, Enum):
    COST_ANALYSIS_INPUT = "cost_analysis_input"
    SCENARIO_ANALYSIS_INPUT = "scenario_analysis_input"
    RISK_ANALYSIS_INPUT = "risk_analysis_input"
    MATERIAL_ANALYSIS_INPUT = "material_analysis_input"
    SOURCING_INPUT_PREPARATION = "sourcing_input_preparation"
    RECOMMENDATION_INPUT_PREPARATION = "recommendation_input_preparation"
    GOVERNANCE_DEMONSTRATION = "governance_demonstration"


@dataclass(frozen=True)
class ApprovedSpecificationConsumptionValue:
    field_key: str
    value: object
    source: str

    def __post_init__(self) -> None:
        if not self.field_key.strip():
            raise ValueError("field_key must not be empty")
        if self.source not in APPROVED_VALUE_SOURCES:
            raise ValueError("invalid approved-value source")
        _canonical_json(self.value, label="consumption value")


@dataclass(frozen=True)
class ApprovedSpecificationConsumptionEnvelope:
    envelope_id: str
    project_id: str
    snapshot_id: str
    review_id: str
    source_review_revision_id: str
    source_review_revision_number: int
    existing_dataset_id: str
    proposed_dataset_id: str
    snapshot_schema_version: str
    consumption_contract_version: str
    approved_values: tuple[ApprovedSpecificationConsumptionValue, ...]
    excluded_fields: tuple[str, ...]
    snapshot_content_hash: str
    envelope_content_hash: str
    created_at: str

    def __post_init__(self) -> None:
        _require_strings(
            envelope_id=self.envelope_id,
            project_id=self.project_id,
            snapshot_id=self.snapshot_id,
            review_id=self.review_id,
            source_review_revision_id=self.source_review_revision_id,
            existing_dataset_id=self.existing_dataset_id,
            proposed_dataset_id=self.proposed_dataset_id,
            snapshot_schema_version=self.snapshot_schema_version,
            consumption_contract_version=self.consumption_contract_version,
            snapshot_content_hash=self.snapshot_content_hash,
            envelope_content_hash=self.envelope_content_hash,
            created_at=self.created_at,
        )
        if self.source_review_revision_number < 1:
            raise ValueError("source_review_revision_number must be positive")
        if self.existing_dataset_id == self.proposed_dataset_id:
            raise ValueError("Existing and Proposed datasets must be distinct")
        _validate_materialization(self.approved_values, self.excluded_fields)
        expected = approved_specification_consumption_envelope_hash(
            project_id=self.project_id,
            snapshot_id=self.snapshot_id,
            review_id=self.review_id,
            source_review_revision_id=self.source_review_revision_id,
            source_review_revision_number=self.source_review_revision_number,
            existing_dataset_id=self.existing_dataset_id,
            proposed_dataset_id=self.proposed_dataset_id,
            snapshot_schema_version=self.snapshot_schema_version,
            approved_values=self.approved_values,
            excluded_fields=self.excluded_fields,
            snapshot_content_hash=self.snapshot_content_hash,
            consumption_contract_version=self.consumption_contract_version,
        )
        if self.envelope_content_hash != expected:
            raise ApprovedSpecificationConsumptionError(
                "envelope content hash does not match governed content"
            )


@dataclass(frozen=True)
class ConsumptionAuthorization:
    authorization_id: str
    project_id: str
    snapshot_id: str
    envelope_id: str
    purpose: AuthorizedConsumptionPurpose
    actor_reference: str
    business_reason: str
    snapshot_content_hash: str
    envelope_content_hash: str
    authorization_schema_version: str
    created_at: str

    def __post_init__(self) -> None:
        _require_strings(
            authorization_id=self.authorization_id,
            project_id=self.project_id,
            snapshot_id=self.snapshot_id,
            envelope_id=self.envelope_id,
            actor_reference=self.actor_reference,
            business_reason=self.business_reason,
            snapshot_content_hash=self.snapshot_content_hash,
            envelope_content_hash=self.envelope_content_hash,
            authorization_schema_version=self.authorization_schema_version,
            created_at=self.created_at,
        )
        if not isinstance(self.purpose, AuthorizedConsumptionPurpose):
            raise ApprovedSpecificationConsumptionError(
                "unsupported consumption purpose"
            )


@dataclass(frozen=True)
class GovernedConsumptionHandoff:
    envelope: ApprovedSpecificationConsumptionEnvelope
    authorization: ConsumptionAuthorization

    def __post_init__(self) -> None:
        if self.envelope.project_id != self.authorization.project_id:
            raise ApprovedSpecificationConsumptionError(
                "handoff project lineage does not match"
            )
        if self.envelope.snapshot_id != self.authorization.snapshot_id:
            raise ApprovedSpecificationConsumptionError(
                "handoff snapshot lineage does not match"
            )
        if self.envelope.envelope_id != self.authorization.envelope_id:
            raise ApprovedSpecificationConsumptionError(
                "handoff envelope identity does not match"
            )
        if self.envelope.snapshot_content_hash != self.authorization.snapshot_content_hash:
            raise ApprovedSpecificationConsumptionError(
                "handoff snapshot hash does not match"
            )
        if self.envelope.envelope_content_hash != self.authorization.envelope_content_hash:
            raise ApprovedSpecificationConsumptionError(
                "handoff envelope hash does not match"
            )


def approved_specification_consumption_envelope_hash(
    *,
    project_id: str,
    snapshot_id: str,
    review_id: str,
    source_review_revision_id: str,
    source_review_revision_number: int,
    existing_dataset_id: str,
    proposed_dataset_id: str,
    snapshot_schema_version: str,
    approved_values: tuple[ApprovedSpecificationConsumptionValue, ...],
    excluded_fields: tuple[str, ...],
    snapshot_content_hash: str,
    consumption_contract_version: str = CONSUMPTION_CONTRACT_VERSION,
) -> str:
    _require_strings(
        project_id=project_id,
        snapshot_id=snapshot_id,
        review_id=review_id,
        source_review_revision_id=source_review_revision_id,
        existing_dataset_id=existing_dataset_id,
        proposed_dataset_id=proposed_dataset_id,
        snapshot_schema_version=snapshot_schema_version,
        snapshot_content_hash=snapshot_content_hash,
        consumption_contract_version=consumption_contract_version,
    )
    if source_review_revision_number < 1:
        raise ValueError("source_review_revision_number must be positive")
    if existing_dataset_id == proposed_dataset_id:
        raise ValueError("Existing and Proposed datasets must be distinct")
    _validate_materialization(approved_values, excluded_fields)
    payload: Mapping[str, object] = {
        "project_id": project_id,
        "snapshot_id": snapshot_id,
        "review_id": review_id,
        "source_review_revision_id": source_review_revision_id,
        "source_review_revision_number": source_review_revision_number,
        "existing_dataset_id": existing_dataset_id,
        "proposed_dataset_id": proposed_dataset_id,
        "snapshot_schema_version": snapshot_schema_version,
        "consumption_contract_version": consumption_contract_version,
        "approved_values": [
            {"field_key": item.field_key, "value": item.value, "source": item.source}
            for item in approved_values
        ],
        "excluded_fields": list(excluded_fields),
        "snapshot_content_hash": snapshot_content_hash,
    }
    canonical = _canonical_json(payload, label="consumption envelope")
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_materialization(
    approved_values: tuple[ApprovedSpecificationConsumptionValue, ...],
    excluded_fields: tuple[str, ...],
) -> None:
    value_keys = tuple(item.field_key for item in approved_values)
    if value_keys != tuple(sorted(value_keys)):
        raise ValueError("approved values must use deterministic field ordering")
    if len(value_keys) != len(set(value_keys)):
        raise ValueError("approved values must not contain duplicate fields")
    if excluded_fields != tuple(sorted(excluded_fields)):
        raise ValueError("excluded fields must use deterministic ordering")
    if len(excluded_fields) != len(set(excluded_fields)):
        raise ValueError("excluded fields must not contain duplicates")
    if any(not field.strip() for field in excluded_fields):
        raise ValueError("excluded fields must not contain empty keys")
    if set(value_keys).intersection(excluded_fields):
        raise ValueError("a field cannot be both approved and excluded")


def _require_strings(**values: str) -> None:
    for name, value in values.items():
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must not be empty")


def _canonical_json(value: object, *, label: str) -> str:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} must be canonical JSON-compatible") from error
