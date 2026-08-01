from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from src.application.runtime import (
    build_approved_specification_consumption_read_model,
    build_approved_specification_read_model,
    build_dataset_repository,
    build_project_repository,
    build_specification_review_read_model,
)
from src.persistence.database import Database
from src.persistence.decision_repository import DecisionRepository
from src.persistence.migrations import initialize_database
from src.persistence.scenario_repository import ScenarioRepository
from src.sourcemate.domain import SourceClassification

from .domain import EvidenceEventType, EvidenceLedgerError, EvidenceLedgerEvent, EvidenceReference


class EvidenceLedgerRepositoryContext:
    """Read-only project-scoped projection over existing governed records."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        database = Database(self.database_path)
        initialize_database(database)
        self.projects = build_project_repository(self.database_path)
        self.datasets = build_dataset_repository(self.database_path)
        self.reviews = build_specification_review_read_model(self.database_path)
        self.snapshots = build_approved_specification_read_model(self.database_path)
        self.consumption = build_approved_specification_consumption_read_model(self.database_path)
        self.scenarios = ScenarioRepository(database)
        self.decisions = DecisionRepository(database)

    def list_projects(self) -> tuple[dict[str, Any], ...]:
        return tuple(self.projects.list(archived=None))

    def project_events(self, project_id: str) -> tuple[EvidenceLedgerEvent, ...]:
        project = self._project(project_id)
        archived = project.get("archived_at") is not None
        events: list[EvidenceLedgerEvent] = [self._project_event(project, archived)]
        events.extend(self._dataset_events(project_id, archived))
        events.extend(self._review_events(project_id, archived))
        events.extend(self._snapshot_events(project_id, archived))
        events.extend(self._consumption_events(project_id, archived))
        events.extend(self._scenario_events(project_id, archived))
        events.extend(self._decision_events(project_id, archived))
        return tuple(events)

    def _project(self, project_id: str) -> dict[str, Any]:
        for project in self.projects.list(archived=None):
            if str(project.get("project_id")) == project_id:
                return project
        raise EvidenceLedgerError("RECORD_NOT_FOUND", "The requested project was not found.")

    def _project_event(self, row: dict[str, Any], archived: bool) -> EvidenceLedgerEvent:
        record_id = str(row["project_id"])
        return self._event(
            project_id=record_id,
            event_type=EvidenceEventType.PROJECT,
            record_id=record_id,
            title="Project record",
            summary=str(row.get("name") or row.get("project_name") or record_id),
            status="archived" if archived else "active",
            occurred_at=str(row.get("created_at") or ""),
            source_hash=str(row.get("content_hash") or ""),
            archived=archived,
            limitations=("Project state does not prove engineering, commercial or production approval.",),
        )

    def _dataset_events(self, project_id: str, archived: bool) -> list[EvidenceLedgerEvent]:
        events = []
        for row in self.datasets.list_for_project(project_id):
            record_id = str(row["dataset_id"])
            events.append(self._event(
                project_id=project_id,
                event_type=EvidenceEventType.DATASET,
                record_id=record_id,
                title=f"Dataset version {row.get('version_number', '')}",
                summary=f"{row.get('source_type', 'dataset')} — {row.get('validation_status', 'recorded')}",
                status=str(row.get("validation_status") or "recorded"),
                occurred_at=str(row.get("created_at") or ""),
                revision=str(row.get("version_number") or ""),
                source_hash=str(row.get("content_hash") or ""),
                archived=archived,
                limitations=("Dataset presence does not prove supplier, laboratory or production validation.",),
            ))
        return events

    def _review_events(self, project_id: str, archived: bool) -> list[EvidenceLedgerEvent]:
        events: list[EvidenceLedgerEvent] = []
        for summary in self.reviews.list_reviews_for_project(project_id):
            review_id = str(summary.review_id)
            events.append(self._event(
                project_id=project_id,
                event_type=EvidenceEventType.SPECIFICATION_REVIEW,
                record_id=review_id,
                title="Specification review",
                summary="Persisted governed specification review.",
                status=str(getattr(summary, "status", "recorded")),
                occurred_at=str(getattr(summary, "created_at", "")),
                archived=archived,
                limitations=("A review record does not constitute approved specification or production release.",),
            ))
            for revision in self.reviews.list_history(review_id, project_id=project_id):
                data = _record(revision)
                state = _record(data.get("state"))
                eligibility = _record(state.get("eligibility"))
                revision_id = str(data.get("review_revision_id") or f"{review_id}:{data.get('revision_number', '')}")
                blockers = _strings(eligibility.get("blockers"))
                pending = tuple(sorted(
                    str(_record(item).get("field_key") or _record(_record(item).get("candidate")).get("field_key") or "field")
                    for item in state.get("comparisons", ())
                    if str(_record(_record(item).get("candidate")).get("status", "")).lower().endswith("pending")
                ))
                events.append(self._event(
                    project_id=project_id,
                    event_type=EvidenceEventType.SPECIFICATION_REVISION,
                    record_id=revision_id,
                    title=f"Specification review revision {data.get('revision_number', '')}",
                    summary="Immutable governed review revision.",
                    status="eligible" if eligibility.get("eligible") else "blocked",
                    occurred_at=str(data.get("created_at") or ""),
                    revision=str(data.get("revision_number") or revision_id),
                    actor=str(data.get("actor_reference") or ""),
                    source_hash=str(data.get("content_hash") or data.get("state_hash") or ""),
                    parents=(EvidenceReference("specification_review", review_id),),
                    blockers=blockers,
                    validation=tuple(f"Complete governed review for {item}." for item in pending),
                    archived=archived,
                    limitations=("Eligibility does not constitute autonomous engineering approval.",),
                ))
        return events

    def _snapshot_events(self, project_id: str, archived: bool) -> list[EvidenceLedgerEvent]:
        events = []
        for row in self.snapshots.list_snapshots_for_project(project_id):
            events.append(self._event(
                project_id=project_id,
                event_type=EvidenceEventType.APPROVED_SNAPSHOT,
                record_id=row.snapshot_id,
                title="Approved specification snapshot",
                summary="Immutable human-authorized specification snapshot.",
                status="approved_snapshot",
                occurred_at=str(getattr(row, "created_at", "")),
                revision=row.source_review_revision_id,
                actor=str(getattr(row, "actor_reference", "")),
                source_hash=row.content_hash,
                parents=(EvidenceReference("specification_revision", row.source_review_revision_id),),
                classification=SourceClassification.APPROVED_SNAPSHOT,
                archived=archived,
                limitations=("Snapshot approval does not approve production, supplier award or regulatory compliance.",),
            ))
        return events

    def _consumption_events(self, project_id: str, archived: bool) -> list[EvidenceLedgerEvent]:
        events = []
        for envelope in self.consumption.list_envelopes_for_project(project_id):
            events.append(self._event(
                project_id=project_id,
                event_type=EvidenceEventType.CONSUMPTION_ENVELOPE,
                record_id=envelope.envelope_id,
                title="Governed consumption envelope",
                summary="Read-only downstream input package from an approved snapshot.",
                status="prepared",
                occurred_at=str(getattr(envelope, "created_at", "")),
                revision=envelope.source_review_revision_id,
                source_hash=envelope.envelope_content_hash,
                parents=(EvidenceReference("approved_specification_snapshot", envelope.snapshot_id),),
                classification=SourceClassification.AUTHORIZED_HANDOFF,
                archived=archived,
                limitations=("Envelope preparation does not execute analysis or approve a business decision.",),
            ))
            for auth in self.consumption.list_authorizations_for_snapshot(envelope.snapshot_id, project_id=project_id):
                if auth.envelope_id != envelope.envelope_id:
                    continue
                auth_id = str(getattr(auth, "authorization_id", ""))
                events.append(self._event(
                    project_id=project_id,
                    event_type=EvidenceEventType.CONSUMPTION_AUTHORIZATION,
                    record_id=auth_id,
                    title="Consumption authorization",
                    summary=f"Purpose: {auth.purpose.value}",
                    status="authorized",
                    occurred_at=str(getattr(auth, "created_at", "")),
                    actor=str(getattr(auth, "actor_reference", "")),
                    source_hash=str(getattr(auth, "content_hash", "")),
                    parents=(EvidenceReference("consumption_envelope", envelope.envelope_id),),
                    classification=SourceClassification.AUTHORIZED_HANDOFF,
                    archived=archived,
                    limitations=("Purpose authorization does not execute an engine, approve a recommendation or award business.",),
                ))
        return events

    def _scenario_events(self, project_id: str, archived: bool) -> list[EvidenceLedgerEvent]:
        return [self._event(
            project_id=project_id,
            event_type=EvidenceEventType.SCENARIO,
            record_id=str(row["scenario_id"]),
            title="Persisted scenario",
            summary="Stored deterministic scenario result.",
            status=str(row.get("status") or "recorded"),
            occurred_at=str(row.get("created_at") or ""),
            source_hash=str(row.get("content_hash") or ""),
            related=(EvidenceReference("dataset", str(row.get("dataset_id"))),) if row.get("dataset_id") else (),
            archived=archived,
            limitations=("Scenario outputs do not prove realized savings, production fitness or commercial approval.",),
        ) for row in self.scenarios.list_for_project(project_id)]

    def _decision_events(self, project_id: str, archived: bool) -> list[EvidenceLedgerEvent]:
        events = []
        for row in self.decisions.list_for_project(project_id):
            gates = _json_mapping(row.get("gate_results_json"))
            events.append(self._event(
                project_id=project_id,
                event_type=EvidenceEventType.DECISION,
                record_id=str(row["decision_snapshot_id"]),
                title="Decision snapshot",
                summary=f"Recorded status: {row.get('status', 'recorded')}",
                status=str(row.get("status") or "recorded"),
                occurred_at=str(row.get("created_at") or ""),
                source_hash=str(row.get("content_hash") or ""),
                parents=(EvidenceReference("scenario", str(row.get("scenario_id"))),) if row.get("scenario_id") else (),
                related=(EvidenceReference("dataset", str(row.get("dataset_id"))),) if row.get("dataset_id") else (),
                blockers=_strings(gates.get("blockers") or gates.get("blocking_controls")),
                validation=_strings(gates.get("required_validation") or gates.get("validation_actions")),
                classification=SourceClassification.DERIVED,
                archived=archived,
                limitations=("Decision snapshot is recommendation-for-review evidence, not autonomous approval or supplier award.",),
            ))
        return events

    def _event(self, *, project_id: str, event_type: EvidenceEventType, record_id: str, title: str,
               summary: str, status: str, occurred_at: str = "", revision: str = "", actor: str = "",
               source_hash: str = "", parents: tuple[EvidenceReference, ...] = (),
               related: tuple[EvidenceReference, ...] = (), blockers: tuple[str, ...] = (),
               validation: tuple[str, ...] = (), classification: SourceClassification = SourceClassification.OBSERVED,
               archived: bool = False, limitations: tuple[str, ...] = ()) -> EvidenceLedgerEvent:
        if not record_id:
            raise EvidenceLedgerError("MISSING_IDENTITY", f"{event_type.value} record identity is missing.")
        revision_part = revision or record_id
        event_id = f"{event_type.value}:{record_id}:{revision_part}"
        sequence_key = f"{occurred_at or '9999-12-31T23:59:59Z'}|{event_type.value}|{record_id}|{revision_part}"
        warning = "" if source_hash else "Source record does not expose a content hash; identity and lineage remain visible."
        return EvidenceLedgerEvent(
            project_id=project_id, event_id=event_id, event_type=event_type, record_id=record_id,
            title=title, summary=summary, sequence_key=sequence_key, occurred_at=occurred_at,
            status=status, revision_reference=revision, actor_reference=actor,
            source_classification=classification, source_hash=source_hash,
            parent_references=parents, related_references=related, blockers=tuple(sorted(set(blockers))),
            validation_requirements=tuple(sorted(set(validation))), claim_limitations=limitations,
            archived=archived, integrity_warning=warning,
        )


def _record(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if is_dataclass(value):
        return asdict(value)
    return dict(vars(value)) if hasattr(value, "__dict__") else {}


def _strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value.strip(),) if value.strip() else ()
    if isinstance(value, dict):
        return tuple(sorted(str(key) for key, enabled in value.items() if enabled))
    try:
        return tuple(sorted({str(item).strip() for item in value if str(item).strip()}))
    except TypeError:
        return (str(value),)


def _json_mapping(value: Any) -> dict[str, Any]:
    import json
    if isinstance(value, dict):
        return value
    if not value:
        return {}
    try:
        parsed = json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}
