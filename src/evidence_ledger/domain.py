from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from src.sourcemate.domain import SourceClassification


class EvidenceLedgerError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


class EvidenceEventType(str, Enum):
    PROJECT = "project"
    DATASET = "dataset"
    SPECIFICATION_REVIEW = "specification_review"
    SPECIFICATION_REVISION = "specification_revision"
    APPROVED_SNAPSHOT = "approved_specification_snapshot"
    CONSUMPTION_ENVELOPE = "consumption_envelope"
    CONSUMPTION_AUTHORIZATION = "consumption_authorization"
    SCENARIO = "scenario"
    DECISION = "decision_snapshot"


@dataclass(frozen=True)
class EvidenceReference:
    record_type: str
    record_id: str
    revision_reference: str = ""

    def __post_init__(self) -> None:
        if not self.record_type.strip() or not self.record_id.strip():
            raise EvidenceLedgerError("INVALID_REFERENCE", "Evidence references require record type and identity.")


@dataclass(frozen=True)
class EvidenceLedgerEvent:
    project_id: str
    event_id: str
    event_type: EvidenceEventType
    record_id: str
    title: str
    summary: str
    sequence_key: str
    occurred_at: str = ""
    status: str = "recorded"
    revision_reference: str = ""
    actor_reference: str = ""
    source_classification: SourceClassification = SourceClassification.OBSERVED
    source_hash: str = ""
    parent_references: tuple[EvidenceReference, ...] = ()
    related_references: tuple[EvidenceReference, ...] = ()
    blockers: tuple[str, ...] = ()
    validation_requirements: tuple[str, ...] = ()
    claim_limitations: tuple[str, ...] = ()
    archived: bool = False
    integrity_warning: str = ""

    def __post_init__(self) -> None:
        required = (self.project_id, self.event_id, self.record_id, self.title, self.sequence_key)
        if any(not value.strip() for value in required):
            raise EvidenceLedgerError("INVALID_EVENT", "Ledger events require project, event, record, title and sequence identity.")


@dataclass(frozen=True)
class ProjectEvidenceLedger:
    project_id: str
    project_status: str
    archived: bool
    events: tuple[EvidenceLedgerEvent, ...]
    unresolved_blockers: tuple[str, ...]
    pending_validation: tuple[str, ...]
    latest_event_reference: str
    integrity_status: str
    claim_limitations: tuple[str, ...]
    schema_version: str = "1.0"

    def canonical_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["events"] = [
            {
                **asdict(event),
                "event_type": event.event_type.value,
                "source_classification": event.source_classification.value,
            }
            for event in self.events
        ]
        return payload

    def canonical_json(self) -> str:
        return json.dumps(self.canonical_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
