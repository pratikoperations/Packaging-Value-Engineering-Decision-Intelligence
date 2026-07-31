from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.application.approved_specification_consumption_service import (
    ApprovedSpecificationConsumptionError,
)
from src.application.runtime import (
    build_approved_specification_consumption_read_model,
    build_approved_specification_consumption_repository,
    build_approved_specification_consumption_service,
    build_approved_specification_snapshot_service,
    build_dataset_repository,
    build_persistent_specification_review_service,
    build_project_repository,
)
from src.application.specification_review_service import AssignedDataset, ReviewableField
from src.domain.approved_specification_consumption import AuthorizedConsumptionPurpose
from src.domain.specification_review import DatasetRole
from src.persistence.database import Database


class ApprovedSpecificationConsumptionFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp.name) / "approved-consumption-flow.sqlite3"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_full_governed_consumption_flow(self) -> None:
        projects = build_project_repository(self.database_path)
        project = projects.create(
            project_id="project-e1-7",
            project_code="E1-7-INTEGRATION",
            project_name="Approved consumption integration",
            category="corrugated",
            currency="INR",
            annual_volume=100000,
            status="active",
        )
        project_id = str(project["project_id"])
        other_project = projects.create(
            project_id="project-e1-7-other",
            project_code="E1-7-OTHER",
            project_name="Other project",
            category="corrugated",
            currency="INR",
            annual_volume=1000,
            status="active",
        )
        other_project_id = str(other_project["project_id"])

        datasets = build_dataset_repository(self.database_path)
        existing_data = {
            "gsm": 120,
            "caliper": 1.0,
            "burst_strength": 8.0,
            "flute": "B",
            "coating": None,
        }
        proposed_data = {
            "gsm": 140,
            "caliper": 0.8,
            "burst_strength": 7.0,
            "flute": "B",
            "coating": None,
        }
        existing_record = datasets.create_version(
            project_id=project_id,
            source_type="integration-existing",
            canonical_data=existing_data,
            validation_status="valid",
        )
        proposed_record = datasets.create_version(
            project_id=project_id,
            source_type="integration-proposed",
            canonical_data=proposed_data,
            validation_status="valid",
        )
        existing = AssignedDataset(
            dataset_id=str(existing_record["dataset_id"]),
            project_id=project_id,
            role=DatasetRole.EXISTING,
            canonical_data=existing_data,
        )
        proposed = AssignedDataset(
            dataset_id=str(proposed_record["dataset_id"]),
            project_id=project_id,
            role=DatasetRole.PROPOSED,
            canonical_data=proposed_data,
        )
        fields = (
            ReviewableField("burst_strength", ("burst_strength",)),
            ReviewableField("caliper", ("caliper",)),
            ReviewableField("coating", ("coating",), mandatory=False),
            ReviewableField("flute", ("flute",)),
            ReviewableField("gsm", ("gsm",)),
        )

        review_service = build_persistent_specification_review_service(self.database_path)
        review = review_service.initialize_and_save(
            existing=existing,
            proposed=proposed,
            fields=fields,
            actor_reference="integration-reviewer",
        )
        review = review_service.confirm_and_save(
            review.review_id,
            dataset_id=existing.dataset_id,
            actor_reference="integration-reviewer",
        )
        review = review_service.accept_and_save(
            review.review_id,
            field_key="gsm",
            actor_reference="integration-reviewer",
        )
        review = review_service.correct_and_save(
            review.review_id,
            field_key="caliper",
            corrected_value=0.9,
            actor_reference="integration-reviewer",
            action_reason="Use the validated intermediate caliper.",
        )
        review = review_service.reject_and_save(
            review.review_id,
            field_key="burst_strength",
            actor_reference="integration-reviewer",
            action_reason="Retain the governed Existing baseline strength.",
        )
        self.assertIsNotNone(review.state.eligibility)
        self.assertTrue(review.state.eligibility.eligible)

        snapshot = build_approved_specification_snapshot_service(
            self.database_path
        ).create_snapshot(
            project_id=project_id,
            review_id=review.review_id,
            source_review_revision_id=review.review_revision_id,
            actor_reference="integration-approver",
            approval_reason="Freeze the reviewed specification for governed consumption.",
            fields=fields,
            optional_exclusions=("coating",),
        )

        service = build_approved_specification_consumption_service(self.database_path)
        first = service.create_handoff(
            project_id=project_id,
            snapshot_id=snapshot.snapshot_id,
            purpose=AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            actor_reference="integration-buyer",
            business_reason="Prepare the approved specification for controlled cost analysis.",
        )

        recreated_service = build_approved_specification_consumption_service(
            self.database_path
        )
        recreated_read_model = build_approved_specification_consumption_read_model(
            self.database_path
        )
        reloaded_envelope = recreated_read_model.get_envelope(
            first.envelope.envelope_id,
            project_id=project_id,
        )
        reloaded_authorization = recreated_read_model.get_authorization(
            first.authorization.authorization_id,
            project_id=project_id,
        )

        self.assertEqual(reloaded_envelope.project_id, project_id)
        self.assertEqual(reloaded_envelope.snapshot_id, snapshot.snapshot_id)
        self.assertEqual(reloaded_envelope.review_id, review.review_id)
        self.assertEqual(
            reloaded_envelope.source_review_revision_id,
            review.review_revision_id,
        )
        self.assertEqual(
            reloaded_envelope.source_review_revision_number,
            review.revision_number,
        )
        self.assertEqual(reloaded_envelope.existing_dataset_id, existing.dataset_id)
        self.assertEqual(reloaded_envelope.proposed_dataset_id, proposed.dataset_id)
        self.assertEqual(reloaded_envelope.snapshot_content_hash, snapshot.content_hash)
        self.assertEqual(
            reloaded_authorization.envelope_content_hash,
            reloaded_envelope.envelope_content_hash,
        )
        self.assertEqual(
            recreated_read_model.get_authorized_envelope(
                first.authorization.authorization_id,
                project_id=project_id,
            ),
            reloaded_envelope,
        )

        identical_retry = recreated_service.create_handoff(
            project_id=project_id,
            snapshot_id=snapshot.snapshot_id,
            purpose=AuthorizedConsumptionPurpose.COST_ANALYSIS_INPUT,
            actor_reference="integration-buyer",
            business_reason="Prepare the approved specification for controlled cost analysis.",
        )
        self.assertEqual(identical_retry.envelope.envelope_id, first.envelope.envelope_id)
        self.assertEqual(
            identical_retry.authorization.authorization_id,
            first.authorization.authorization_id,
        )

        repository = build_approved_specification_consumption_repository(
            self.database_path
        )
        self.assertEqual(len(repository.list_envelopes_for_project(project_id)), 1)
        self.assertEqual(
            len(repository.list_authorizations_for_snapshot(
                snapshot.snapshot_id,
                project_id=project_id,
            )),
            1,
        )

        second = recreated_service.create_handoff(
            project_id=project_id,
            snapshot_id=snapshot.snapshot_id,
            purpose=AuthorizedConsumptionPurpose.RISK_ANALYSIS_INPUT,
            actor_reference="integration-buyer",
            business_reason="Prepare the approved specification for controlled risk analysis.",
        )
        self.assertEqual(second.envelope.envelope_id, first.envelope.envelope_id)
        self.assertNotEqual(
            second.authorization.authorization_id,
            first.authorization.authorization_id,
        )
        self.assertEqual(len(repository.list_envelopes_for_project(project_id)), 1)
        self.assertEqual(
            len(repository.list_authorizations_for_snapshot(
                snapshot.snapshot_id,
                project_id=project_id,
            )),
            2,
        )

        with self.assertRaises(ApprovedSpecificationConsumptionError):
            recreated_read_model.get_envelope(
                first.envelope.envelope_id,
                project_id=other_project_id,
            )
        with self.assertRaises(ApprovedSpecificationConsumptionError):
            recreated_read_model.get_authorization(
                first.authorization.authorization_id,
                project_id=other_project_id,
            )

        database = Database(self.database_path)
        with database.transaction() as connection:
            connection.execute(
                "UPDATE projects SET archived_at = ? WHERE project_id = ?",
                ("2026-07-31T00:00:00+00:00", project_id),
            )

        with self.assertRaises(ApprovedSpecificationConsumptionError) as archived:
            recreated_service.create_handoff(
                project_id=project_id,
                snapshot_id=snapshot.snapshot_id,
                purpose=AuthorizedConsumptionPurpose.MATERIAL_ANALYSIS_INPUT,
                actor_reference="integration-buyer",
                business_reason="This must be rejected because the project is archived.",
            )
        self.assertEqual(archived.exception.code, "archived_project")

        with database.connect() as connection:
            existing_tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }
            analytical_tables = {
                "scenarios",
                "scenario_runs",
                "decision_snapshots",
                "decisions",
                "recommendations",
            }.intersection(existing_tables)
            analytical_rows = sum(
                int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in analytical_tables
            )
        self.assertEqual(analytical_rows, 0)


if __name__ == "__main__":
    unittest.main()
