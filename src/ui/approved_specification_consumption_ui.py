from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, MutableMapping, TypeVar

from src.domain.approved_specification_consumption import (
    ApprovedSpecificationConsumptionEnvelope,
    AuthorizedConsumptionPurpose,
    ConsumptionAuthorization,
    GovernedConsumptionHandoff,
)

T = TypeVar("T")
PENDING_HANDOFF_TOKEN_KEY = "pending_consumption_handoff_token"


@dataclass(frozen=True)
class ConsumptionHandoffActionRequest:
    project_id: str
    snapshot_id: str
    purpose: AuthorizedConsumptionPurpose
    actor_reference: str
    business_reason: str

    @property
    def token(self) -> str:
        return "|".join(
            (
                self.project_id,
                self.snapshot_id,
                self.purpose.value,
                self.actor_reference.strip(),
                self.business_reason.strip(),
            )
        )


def execute_handoff_once(
    state: MutableMapping[str, object],
    request: ConsumptionHandoffActionRequest,
    operation: Callable[[], T],
) -> tuple[bool, T | None]:
    if state.get(PENDING_HANDOFF_TOKEN_KEY) == request.token:
        return False, None
    state[PENDING_HANDOFF_TOKEN_KEY] = request.token
    try:
        result = operation()
    except Exception:
        state.pop(PENDING_HANDOFF_TOKEN_KEY, None)
        raise
    return True, result


def clear_handoff_token(state: MutableMapping[str, object]) -> None:
    state.pop(PENDING_HANDOFF_TOKEN_KEY, None)


def snapshot_identity_rows(snapshot) -> list[dict[str, object]]:
    return [
        {"Attribute": "Snapshot ID", "Value": snapshot.snapshot_id},
        {"Attribute": "Review ID", "Value": snapshot.review_id},
        {"Attribute": "Source revision", "Value": snapshot.source_review_revision_id},
        {"Attribute": "Revision number", "Value": snapshot.source_review_revision_number},
        {"Attribute": "Existing dataset", "Value": snapshot.existing_dataset_id},
        {"Attribute": "Proposed dataset", "Value": snapshot.proposed_dataset_id},
        {"Attribute": "Schema version", "Value": snapshot.snapshot_schema_version},
        {"Attribute": "Approved fields", "Value": len(snapshot.approved_values)},
        {"Attribute": "Excluded fields", "Value": len(snapshot.excluded_fields)},
    ]


def envelope_identity_rows(
    envelope: ApprovedSpecificationConsumptionEnvelope,
) -> list[dict[str, object]]:
    return [
        {"Attribute": "Envelope ID", "Value": envelope.envelope_id},
        {"Attribute": "Snapshot ID", "Value": envelope.snapshot_id},
        {"Attribute": "Review ID", "Value": envelope.review_id},
        {"Attribute": "Source revision", "Value": envelope.source_review_revision_id},
        {"Attribute": "Contract version", "Value": envelope.consumption_contract_version},
        {"Attribute": "Approved fields", "Value": len(envelope.approved_values)},
        {"Attribute": "Excluded fields", "Value": len(envelope.excluded_fields)},
        {"Attribute": "Created at", "Value": envelope.created_at},
    ]


def authorization_identity_rows(
    authorization: ConsumptionAuthorization,
) -> list[dict[str, object]]:
    return [
        {"Attribute": "Authorization ID", "Value": authorization.authorization_id},
        {"Attribute": "Purpose", "Value": authorization.purpose.value},
        {"Attribute": "Actor", "Value": authorization.actor_reference},
        {"Attribute": "Business reason", "Value": authorization.business_reason},
        {"Attribute": "Created at", "Value": authorization.created_at},
    ]


def handoff_audit_rows(handoff: GovernedConsumptionHandoff) -> list[dict[str, object]]:
    return [
        {"Attribute": "Snapshot content hash", "Value": handoff.envelope.snapshot_content_hash},
        {"Attribute": "Envelope content hash", "Value": handoff.envelope.envelope_content_hash},
        {"Attribute": "Authorization schema", "Value": handoff.authorization.authorization_schema_version},
    ]


def purpose_label(purpose: AuthorizedConsumptionPurpose) -> str:
    return purpose.value.replace("_", " ").title()


def business_error_message(code: str, fallback: str) -> str:
    messages = {
        "project_required": "Select a project before creating a governed handoff.",
        "snapshot_required": "Select an approved specification snapshot.",
        "actor_required": "Enter the person or role authorizing this handoff.",
        "business_reason_required": "Enter the business reason for this handoff.",
        "unsupported_consumption_purpose": "Select a supported governed purpose.",
        "unsupported_snapshot_schema": "This approved snapshot version cannot be consumed safely.",
        "archived_project": "Archived projects are read-only and cannot create new handoffs.",
        "conflicting_envelope": "A conflicting governed envelope already exists for this snapshot.",
        "conflicting_authorization": "A conflicting authorization already exists for this handoff.",
    }
    return messages.get(code, fallback)
