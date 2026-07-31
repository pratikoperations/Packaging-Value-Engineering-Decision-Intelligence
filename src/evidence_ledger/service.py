from __future__ import annotations

from collections import Counter

from .domain import EvidenceLedgerError, EvidenceLedgerEvent, ProjectEvidenceLedger
from .repository_context import EvidenceLedgerRepositoryContext


class EvidenceLedgerService:
    def __init__(self, context: EvidenceLedgerRepositoryContext) -> None:
        self.context = context

    def build(self, project_id: str) -> ProjectEvidenceLedger:
        projects = {str(item["project_id"]): item for item in self.context.list_projects()}
        if project_id not in projects:
            raise EvidenceLedgerError("RECORD_NOT_FOUND", "The requested project was not found.")
        project = projects[project_id]
        events = self._ordered(self.context.project_events(project_id))
        self._verify_unique(events)
        integrity_warnings = self._verify_relationships(events)
        blockers = tuple(sorted({item for event in events for item in event.blockers}))
        validation = tuple(sorted({item for event in events for item in event.validation_requirements}))
        latest = events[-1].event_id if events else ""
        archived = project.get("archived_at") is not None
        status = "archived" if archived else "active"
        integrity_status = "warning" if integrity_warnings or any(event.integrity_warning for event in events) else "verified"
        limitations = (
            "The ledger is a read-only projection of persisted records; it does not create an audit event.",
            "Chronology and lineage do not prove production fitness, realized savings, supplier award or autonomous approval.",
        )
        return ProjectEvidenceLedger(
            project_id=project_id,
            project_status=status,
            archived=archived,
            events=events,
            unresolved_blockers=blockers,
            pending_validation=validation,
            latest_event_reference=latest,
            integrity_status=integrity_status,
            claim_limitations=limitations,
        )

    @staticmethod
    def filter_events(
        ledger: ProjectEvidenceLedger,
        *,
        record_types: tuple[str, ...] = (),
        statuses: tuple[str, ...] = (),
        classifications: tuple[str, ...] = (),
    ) -> tuple[EvidenceLedgerEvent, ...]:
        return tuple(
            event for event in ledger.events
            if (not record_types or event.event_type.value in record_types)
            and (not statuses or event.status in statuses)
            and (not classifications or event.source_classification.value in classifications)
        )

    @staticmethod
    def _ordered(events: tuple[EvidenceLedgerEvent, ...]) -> tuple[EvidenceLedgerEvent, ...]:
        return tuple(sorted(events, key=lambda item: item.sequence_key))

    @staticmethod
    def _verify_unique(events: tuple[EvidenceLedgerEvent, ...]) -> None:
        counts = Counter(event.event_id for event in events)
        duplicates = tuple(sorted(key for key, count in counts.items() if count > 1))
        if duplicates:
            raise EvidenceLedgerError("DUPLICATE_EVENT", f"Duplicate ledger events detected: {', '.join(duplicates)}")

    @staticmethod
    def _verify_relationships(events: tuple[EvidenceLedgerEvent, ...]) -> tuple[str, ...]:
        known = {(event.event_type.value, event.record_id) for event in events}
        warnings: list[str] = []
        aliases = {
            "specification_revision": "specification_revision",
            "approved_specification_snapshot": "approved_specification_snapshot",
            "consumption_envelope": "consumption_envelope",
            "scenario": "scenario",
            "dataset": "dataset",
        }
        for event in events:
            for reference in event.parent_references:
                key = (aliases.get(reference.record_type, reference.record_type), reference.record_id)
                if key not in known:
                    warnings.append(f"Unresolved parent {reference.record_type}:{reference.record_id} for {event.event_id}.")
        return tuple(sorted(set(warnings)))
