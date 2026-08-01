from __future__ import annotations

import json
import unittest

from src.evidence_ledger.domain import (
    EvidenceEventType,
    EvidenceLedgerError,
    EvidenceLedgerEvent,
    EvidenceReference,
)
from src.evidence_ledger.service import EvidenceLedgerService
from src.sourcemate.domain import SourceClassification


class FakeContext:
    def __init__(self, events=(), projects=None):
        self._events = tuple(events)
        self._projects = projects or ({"project_id": "project-1", "name": "Demo", "archived_at": None},)

    def list_projects(self):
        return tuple(self._projects)

    def project_events(self, project_id):
        if project_id != "project-1":
            raise EvidenceLedgerError("RECORD_NOT_FOUND", "missing")
        return self._events


def event(record_id: str, *, event_type=EvidenceEventType.DATASET, when="2026-01-01T00:00:00Z", **kwargs):
    return EvidenceLedgerEvent(
        project_id="project-1",
        event_id=f"{event_type.value}:{record_id}:{record_id}",
        event_type=event_type,
        record_id=record_id,
        title=record_id,
        summary="summary",
        sequence_key=f"{when}|{event_type.value}|{record_id}|{record_id}",
        occurred_at=when,
        source_classification=SourceClassification.OBSERVED,
        **kwargs,
    )


class EvidenceLedgerTests(unittest.TestCase):
    def test_reference_requires_identity(self):
        with self.assertRaises(EvidenceLedgerError):
            EvidenceReference("dataset", "")

    def test_event_is_immutable(self):
        item = event("d1")
        with self.assertRaises(Exception):
            item.status = "changed"

    def test_service_orders_events_deterministically(self):
        ledger = EvidenceLedgerService(FakeContext((event("d2", when="2026-02-01T00:00:00Z"), event("d1")))).build("project-1")
        self.assertEqual([item.record_id for item in ledger.events], ["d1", "d2"])

    def test_duplicate_event_fails_closed(self):
        item = event("d1")
        with self.assertRaisesRegex(EvidenceLedgerError, "Duplicate"):
            EvidenceLedgerService(FakeContext((item, item))).build("project-1")

    def test_unknown_project_fails_closed(self):
        with self.assertRaises(EvidenceLedgerError):
            EvidenceLedgerService(FakeContext()).build("other")

    def test_blockers_and_validation_are_aggregated(self):
        item = event("d1", blockers=("B",), validation_requirements=("V",))
        ledger = EvidenceLedgerService(FakeContext((item,))).build("project-1")
        self.assertEqual(ledger.unresolved_blockers, ("B",))
        self.assertEqual(ledger.pending_validation, ("V",))

    def test_missing_hash_sets_integrity_warning(self):
        ledger = EvidenceLedgerService(FakeContext((event("d1", integrity_warning="missing hash"),))).build("project-1")
        self.assertEqual(ledger.integrity_status, "warning")

    def test_filtering_is_controlled(self):
        first = event("d1", status="valid")
        second = event("s1", event_type=EvidenceEventType.SCENARIO, status="recorded")
        ledger = EvidenceLedgerService(FakeContext((first, second))).build("project-1")
        selected = EvidenceLedgerService.filter_events(ledger, record_types=("scenario",))
        self.assertEqual(selected, (second,))

    def test_canonical_json_is_deterministic(self):
        service = EvidenceLedgerService(FakeContext((event("d1"),)))
        first = service.build("project-1").canonical_json()
        second = service.build("project-1").canonical_json()
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["schema_version"], "1.0")

    def test_archived_project_remains_read_only(self):
        projects = ({"project_id": "project-1", "archived_at": "2026-01-01"},)
        ledger = EvidenceLedgerService(FakeContext((event("d1", archived=True),), projects)).build("project-1")
        self.assertTrue(ledger.archived)
        self.assertEqual(ledger.project_status, "archived")

    def test_unresolved_parent_marks_integrity_warning(self):
        child = event("s1", event_type=EvidenceEventType.SCENARIO, parent_references=(EvidenceReference("dataset", "missing"),))
        ledger = EvidenceLedgerService(FakeContext((child,))).build("project-1")
        self.assertEqual(ledger.integrity_status, "warning")


if __name__ == "__main__":
    unittest.main()
