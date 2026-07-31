from __future__ import annotations

import unittest
from dataclasses import replace

from src.application.approved_specification_consumption_read_model import (
    ApprovedSpecificationConsumptionReadModel,
)
from src.application.approved_specification_consumption_service import (
    ApprovedSpecificationConsumptionError,
    ApprovedSpecificationConsumptionService,
)
from src.application.approved_specification_snapshot_service import (
    ApprovedSpecificationSnapshotError,
)
from src.domain.approved_specification import (
    APPROVED_SPECIFICATION_SCHEMA_VERSION,
    ApprovedSpecificationSnapshot,
    ApprovedSpecificationValue,
)
from src.domain.approved_specification_consumption import (
    ApprovedSpecificationConsumptionEnvelope,
    AuthorizedConsumptionPurpose,
)
from src.persistence.approved_specification_consumption_repository import (
    ApprovedSpecificationConsumptionPersistenceError,
)


class FakeSnapshotReadModel:
    def __init__(self, snapshot: ApprovedSpecificationSnapshot) -> None:
        self.snapshot = snapshot
        self.calls: list[tuple[str, str]] = []

    def get_snapshot(
        self, snapshot_id: str, *, project_id: str
    ) -> ApprovedSpecificationSnapshot:
        self.calls.append((snapshot_id, project_id))
        if snapshot_id != self.snapshot.snapshot_id or project_id != self.snapshot.project_id:
            raise ApprovedSpecificationSnapshotError(
                "snapshot_not_found", "The approved specification snapshot was not found."
            )
        return self.snapshot


class InMemoryConsumptionRepository:
    def __init__(self) -> None:
        self.envelopes: dict[str, ApprovedSpecificationConsumptionEnvelope] = {}
        self.authorizations = {}
        self.raise_duplicate_envelope_once = False
        self.hide_envelope_once = False

    def create_envelope(self, envelope):
        if self.raise_duplicate_envelope_once:
            self.raise_duplicate_envelope_once = False
            raise ApprovedSpecificationConsumptionPersistenceError(
                "duplicate_envelope", "duplicate"
            )
        self.envelopes[envelope.envelope_id] = envelope
        return envelope

    def create_authorization(self, authorization):
        self.authorizations[authorization.authorization_id] = authorization
        return authorization

    def get_envelope_for_snapshot(
        self, snapshot_id: str, *, project_id: str, consumption_contract_version: str
    ):
        if self.hide_envelope_once:
            self.hide_envelope_once = False
            return None
        for envelope in self.envelopes.values():
            if (
                envelope.snapshot_id == snapshot_id
                and envelope.project_id == project_id
                and envelope.consumption_contract_version == consumption_contract_version
            ):
                return envelope
        return None

    def get_envelope(self, envelope_id: str, *, project_id: str):
        envelope = self.envelopes.get(envelope_id)
        if envelope is None or envelope.project_id != project_id:
            raise ApprovedSpecificationConsumptionPersistenceError(
                "envelope_not_found", "not found"
            )
        return envelope

    def list_envelopes_for_project(self, project_id: str):
        return [item for item in self.envelopes.values() if item.project_id == project_id]

    def get_authorization(self, authorization_id: str, *, project_id: str):
        item = self.authorizations.get(authorization_id)
        if item is None or item.project_id != project_id:
            raise ApprovedSpecificationConsumptionPersistenceError(
                "authorization_not_found", "not found"
            )
        return item

    def list_authorizations_for_snapshot(self, snapshot_id: str, *, project_id: str):
        return [
            item
            for item in self.authorizations.values()
            if item.snapshot_id == snapshot_id and item.project_id == project_id
        ]

    def list_authorizations_for_project(self, project_id: str):
        return [item for item in self.authorizations.values() if item.project_id == project_id]


class ConsumptionApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.snapshot = ApprovedSpecificationSnapshot(
            snapshot_id="s1",
            project_id="p1",
            review_id="r1",
            source_review_revision_id="rr1",
            source_review_revision_number=2,
            existing_dataset_id="d1",
            proposed_dataset_id="d2",
            approved_values=(
                ApprovedSpecificationValue("a", 1, "unchanged"),
                ApprovedSpecificationValue("b", 2, "accepted_proposed"),
            ),
            excluded_fields=("optional",),
            snapshot_schema_version=APPROVED_SPECIFICATION_SCHEMA_VERSION,
            actor_reference="approver",
            approval_reason="approved specification",
            content_hash="snapshot-hash",
            created_at="2026-01-01T00:00:00+00:00",
        )
        self.snapshot_read_model = FakeSnapshotReadModel(self.snapshot)
        self.repository = InMemoryConsumptionRepository()
        self.service = ApprovedSpecificationConsumptionService(
            self.snapshot_read_model, self.repository
        )

    def create(self, **changes):
        data = dict(
            project_id="p1",
            snapshot_id="s1",
            purpose=AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            actor_reference="buyer",
            business_reason="prepare governed cost input",
        )
        data.update(changes)
        return self.service.create_handoff(**data)

    def test_creates_handoff_from_approved_snapshot_only(self) -> None:
        handoff = self.create()
        self.assertEqual(self.snapshot_read_model.calls, [("s1", "p1")])
        self.assertEqual(handoff.envelope.snapshot_id, "s1")
        self.assertEqual(
            tuple(item.field_key for item in handoff.envelope.approved_values),
            ("a", "b"),
        )
        self.assertEqual(handoff.envelope.excluded_fields, ("optional",))
        self.assertEqual(handoff.envelope.snapshot_content_hash, "snapshot-hash")

    def test_accepts_controlled_string_purpose(self) -> None:
        handoff = self.create(purpose="risk_analysis_input")
        self.assertEqual(
            handoff.authorization.purpose,
            AuthorizedConsumptionPurpose.RISK_ANALYSIS_INPUT,
        )

    def test_rejects_unsupported_purpose(self) -> None:
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            self.create(purpose="supplier_approved")
        self.assertEqual(captured.exception.code, "unsupported_consumption_purpose")

    def test_requires_actor_and_business_reason(self) -> None:
        for field in ("actor_reference", "business_reason"):
            with self.subTest(field=field):
                with self.assertRaises(ApprovedSpecificationConsumptionError):
                    self.create(**{field: " "})

    def test_rejects_unsupported_snapshot_schema(self) -> None:
        self.snapshot_read_model.snapshot = replace(
            self.snapshot, snapshot_schema_version="9.9"
        )
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            self.create()
        self.assertEqual(captured.exception.code, "unsupported_snapshot_schema")

    def test_identical_retry_reuses_envelope_and_authorization(self) -> None:
        first = self.create()
        second = self.create()
        self.assertEqual(first.envelope.envelope_id, second.envelope.envelope_id)
        self.assertEqual(first.authorization.authorization_id, second.authorization.authorization_id)
        self.assertEqual(len(self.repository.envelopes), 1)
        self.assertEqual(len(self.repository.authorizations), 1)

    def test_different_purpose_creates_new_authorization(self) -> None:
        first = self.create()
        second = self.create(purpose=AuthorizedConsumptionPurpose.RISK_ANALYSIS_INPUT)
        self.assertEqual(first.envelope.envelope_id, second.envelope.envelope_id)
        self.assertNotEqual(first.authorization.authorization_id, second.authorization.authorization_id)
        self.assertEqual(len(self.repository.authorizations), 2)

    def test_different_reason_creates_new_authorization(self) -> None:
        self.create()
        self.create(business_reason="prepare a second governed cost review")
        self.assertEqual(len(self.repository.authorizations), 2)

    def test_conflicting_existing_envelope_fails_closed(self) -> None:
        first = self.create()
        object.__setattr__(first.envelope, "snapshot_content_hash", "different")
        self.repository.envelopes = {"existing": first.envelope}
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            self.create()
        self.assertEqual(captured.exception.code, "conflicting_envelope")

    def test_concurrent_duplicate_envelope_reloads_identical_record(self) -> None:
        first = self.create()
        self.repository.authorizations.clear()
        self.repository.hide_envelope_once = True
        self.repository.raise_duplicate_envelope_once = True
        second = self.create(purpose=AuthorizedConsumptionPurpose.RISK_ANALYSIS_INPUT)
        self.assertEqual(first.envelope.envelope_id, second.envelope.envelope_id)

    def test_snapshot_errors_are_presentation_safe(self) -> None:
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            self.create(project_id="p2")
        self.assertEqual(captured.exception.code, "snapshot_not_found")

    def test_read_model_operations_are_project_scoped(self) -> None:
        handoff = self.create()
        read_model = ApprovedSpecificationConsumptionReadModel(self.repository)
        self.assertEqual(
            read_model.get_envelope(handoff.envelope.envelope_id, project_id="p1"),
            handoff.envelope,
        )
        self.assertEqual(
            read_model.get_authorization(handoff.authorization.authorization_id, project_id="p1"),
            handoff.authorization,
        )
        self.assertEqual(len(read_model.list_envelopes_for_project("p1")), 1)
        self.assertEqual(len(read_model.list_authorizations_for_snapshot("s1", project_id="p1")), 1)
        self.assertEqual(len(read_model.list_authorizations_for_project("p1")), 1)

    def test_get_authorized_envelope_verifies_handoff(self) -> None:
        handoff = self.create()
        read_model = ApprovedSpecificationConsumptionReadModel(self.repository)
        envelope = read_model.get_authorized_envelope(
            handoff.authorization.authorization_id, project_id="p1"
        )
        self.assertEqual(envelope, handoff.envelope)

    def test_get_authorized_envelope_rejects_mismatched_authorization(self) -> None:
        handoff = self.create()
        object.__setattr__(handoff.authorization, "envelope_content_hash", "tampered")
        read_model = ApprovedSpecificationConsumptionReadModel(self.repository)
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            read_model.get_authorized_envelope(
                handoff.authorization.authorization_id, project_id="p1"
            )
        self.assertEqual(captured.exception.code, "authorized_handoff_integrity_failure")

    def test_read_model_requires_project_scope(self) -> None:
        read_model = ApprovedSpecificationConsumptionReadModel(self.repository)
        with self.assertRaises(ApprovedSpecificationConsumptionError) as captured:
            read_model.list_envelopes_for_project(" ")
        self.assertEqual(captured.exception.code, "project_required")


if __name__ == "__main__":
    unittest.main()
