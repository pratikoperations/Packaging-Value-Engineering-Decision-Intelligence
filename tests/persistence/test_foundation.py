from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.application import ProjectService
from src.persistence import (
    Database,
    DatasetRepository,
    DecisionRepository,
    ExportRepository,
    ProjectRepository,
    ScenarioRepository,
    ThresholdRepository,
)
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database


class PersistenceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "pve-test.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.datasets = DatasetRepository(self.database)
        self.thresholds = ThresholdRepository(self.database)
        self.scenarios = ScenarioRepository(self.database)
        self.decisions = DecisionRepository(self.database)
        self.exports = ExportRepository(self.database)
        self.service = ProjectService(self.projects)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def create_project(self, code: str = "PVE-001") -> dict:
        return self.service.create_project(
            project_code=code,
            project_name="Corrugated optimization",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000,
        )

    def create_dataset(self, project_id: str, value: int) -> dict:
        return self.datasets.create_version(
            project_id=project_id,
            source_type="json",
            canonical_data={"dataset_type": "user_upload", "value": value},
            validation_status="valid",
        )

    def create_threshold(self, project_id: str, value: int) -> dict:
        return self.thresholds.create_version(
            project_id=project_id,
            profile_name="Default",
            profile={"minimum_annual_savings": value},
        )

    def create_scenario(
        self,
        project_id: str,
        dataset_id: str,
        threshold_profile_id: str | None,
        name: str = "Base scenario",
    ) -> dict:
        return self.scenarios.create(
            project_id=project_id,
            dataset_id=dataset_id,
            threshold_profile_id=threshold_profile_id,
            scenario_name=name,
            assumptions={"annual_volume": 1_200_000},
            results={"annual_savings": 1000},
        )

    def build_chain(self) -> tuple[dict, dict, dict, dict, dict]:
        project = self.create_project()
        dataset = self.create_dataset(project["project_id"], 1)
        threshold = self.create_threshold(project["project_id"], 0)
        scenario = self.create_scenario(
            project["project_id"],
            dataset["dataset_id"],
            threshold["threshold_profile_id"],
        )
        decision = self.decisions.create_snapshot(
            project_id=project["project_id"],
            scenario_id=scenario["scenario_id"],
            dataset_id=dataset["dataset_id"],
            threshold_profile_id=threshold["threshold_profile_id"],
            status="conditionally_recommended",
            preferred_alternative_id="ALT-A",
            recommendation={"status": "conditionally_recommended"},
            gate_results={"engineering_validation_required": True},
            engine_version="1.0.1",
            source_commit="TEST",
        )
        return project, dataset, threshold, scenario, decision

    def decision_kwargs(
        self,
        *,
        project_id: str,
        scenario_id: str,
        dataset_id: str,
        threshold_profile_id: str | None,
    ) -> dict:
        return {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "dataset_id": dataset_id,
            "threshold_profile_id": threshold_profile_id,
            "status": "conditionally_recommended",
            "preferred_alternative_id": "ALT-A",
            "recommendation": {"status": "conditionally_recommended"},
            "gate_results": {"engineering_validation_required": True},
            "engine_version": "1.0.1",
            "source_commit": "TEST",
        }

    def test_schema_initialization(self):
        self.assertEqual(current_schema_version(self.database), SCHEMA_VERSION)

    def test_schema_initialization_is_idempotent(self):
        initialize_database(self.database)
        initialize_database(self.database)
        self.assertEqual(current_schema_version(self.database), SCHEMA_VERSION)

    def test_foreign_keys_are_enabled(self):
        self.assertTrue(self.database.foreign_keys_enabled())

    def test_project_create_and_get(self):
        project = self.create_project()
        self.assertEqual(self.projects.get(project["project_id"])["project_code"], "PVE-001")

    def test_project_metadata_update(self):
        project = self.create_project()
        updated = self.service.update_project(project["project_id"], project_name="Updated")
        self.assertEqual(updated["project_name"], "Updated")

    def test_project_update_rejects_unknown_fields(self):
        project = self.create_project()
        with self.assertRaises(ValueError):
            self.service.update_project(project["project_id"], unsupported=True)

    def test_project_archive_separates_active_and_archived(self):
        first = self.create_project("PVE-001")
        self.create_project("PVE-002")
        self.service.archive_project(first["project_id"])
        self.assertEqual(len(self.service.active_projects()), 1)
        self.assertEqual(len(self.service.archived_projects()), 1)

    def test_project_service_validates_required_fields(self):
        with self.assertRaises(ValueError):
            self.service.create_project(
                project_code="",
                project_name="Bad",
                category="corrugated",
                currency="INR",
                annual_volume=1,
            )

    def test_dataset_versions_increment(self):
        project = self.create_project()
        first = self.datasets.create_version(
            project_id=project["project_id"],
            source_type="json",
            canonical_data={"version": 1},
            validation_status="valid",
        )
        second = self.datasets.create_version(
            project_id=project["project_id"],
            source_type="json",
            canonical_data={"version": 2},
            validation_status="valid",
        )
        self.assertEqual((first["version_number"], second["version_number"]), (1, 2))

    def test_duplicate_dataset_content_is_rejected(self):
        project = self.create_project()
        kwargs = dict(
            project_id=project["project_id"],
            source_type="json",
            canonical_data={"same": True},
            validation_status="valid",
        )
        self.datasets.create_version(**kwargs)
        with self.assertRaises(sqlite3.IntegrityError):
            self.datasets.create_version(**kwargs)

    def test_threshold_versions_increment(self):
        project = self.create_project()
        first = self.thresholds.create_version(
            project_id=project["project_id"], profile_name="Default", profile={"min": 0}
        )
        second = self.thresholds.create_version(
            project_id=project["project_id"], profile_name="Default", profile={"min": 1}
        )
        self.assertEqual((first["version_number"], second["version_number"]), (1, 2))

    def test_dataset_is_immutable(self):
        _, dataset, _, _, _ = self.build_chain()
        with self.assertRaises(sqlite3.DatabaseError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE project_datasets SET validation_status = 'invalid' WHERE dataset_id = ?",
                    (dataset["dataset_id"],),
                )

    def test_threshold_is_immutable(self):
        _, _, threshold, _, _ = self.build_chain()
        with self.assertRaises(sqlite3.DatabaseError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM threshold_profiles WHERE threshold_profile_id = ?",
                    (threshold["threshold_profile_id"],),
                )

    def test_scenario_is_immutable(self):
        _, _, _, scenario, _ = self.build_chain()
        with self.assertRaises(sqlite3.DatabaseError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE scenarios SET scenario_name = 'Changed' WHERE scenario_id = ?",
                    (scenario["scenario_id"],),
                )

    def test_decision_snapshot_is_immutable(self):
        project, _, _, _, decision = self.build_chain()
        self.assertEqual(len(self.decisions.list_for_project(project["project_id"])), 1)
        with self.assertRaises(sqlite3.DatabaseError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM decision_snapshots WHERE decision_snapshot_id = ?",
                    (decision["decision_snapshot_id"],),
                )

    def test_foreign_key_rejects_missing_project(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.datasets.create_version(
                project_id="missing",
                source_type="json",
                canonical_data={"value": 1},
                validation_status="valid",
            )

    def test_export_record_links_to_decision(self):
        _, _, _, _, decision = self.build_chain()
        record = self.exports.create(
            decision_snapshot_id=decision["decision_snapshot_id"],
            export_type="json",
            filename="decision.json",
            content_hash="abc123",
        )
        self.assertEqual(record["decision_snapshot_id"], decision["decision_snapshot_id"])

    def test_temporary_databases_are_isolated(self):
        other = Database(Path(self.tempdir.name) / "other.sqlite3")
        initialize_database(other)
        ProjectRepository(other).create(
            project_code="OTHER",
            project_name="Other",
            category="corrugated",
            currency="INR",
            annual_volume=1,
        )
        self.assertEqual(len(self.projects.list(archived=None)), 0)
        self.assertEqual(len(ProjectRepository(other).list(archived=None)), 1)

    def test_scenario_rejects_dataset_from_another_project(self):
        project_a = self.create_project("PVE-A")
        project_b = self.create_project("PVE-B")
        dataset_b = self.create_dataset(project_b["project_id"], 101)
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_scenario(project_a["project_id"], dataset_b["dataset_id"], None)

    def test_scenario_rejects_threshold_from_another_project(self):
        project_a = self.create_project("PVE-A")
        project_b = self.create_project("PVE-B")
        dataset_a = self.create_dataset(project_a["project_id"], 102)
        threshold_b = self.create_threshold(project_b["project_id"], 102)
        with self.assertRaisesRegex(ValueError, "same project"):
            self.create_scenario(
                project_a["project_id"],
                dataset_a["dataset_id"],
                threshold_b["threshold_profile_id"],
            )

    def test_decision_rejects_scenario_from_another_project(self):
        project_a = self.create_project("PVE-A")
        project_b = self.create_project("PVE-B")
        dataset_b = self.create_dataset(project_b["project_id"], 103)
        threshold_b = self.create_threshold(project_b["project_id"], 103)
        scenario_b = self.create_scenario(
            project_b["project_id"], dataset_b["dataset_id"], threshold_b["threshold_profile_id"]
        )
        with self.assertRaisesRegex(ValueError, "scenario must belong"):
            self.decisions.create_snapshot(
                **self.decision_kwargs(
                    project_id=project_a["project_id"],
                    scenario_id=scenario_b["scenario_id"],
                    dataset_id=dataset_b["dataset_id"],
                    threshold_profile_id=threshold_b["threshold_profile_id"],
                )
            )

    def test_decision_rejects_dataset_from_another_project(self):
        project_a = self.create_project("PVE-A")
        project_b = self.create_project("PVE-B")
        dataset_a = self.create_dataset(project_a["project_id"], 104)
        threshold_a = self.create_threshold(project_a["project_id"], 104)
        scenario_a = self.create_scenario(
            project_a["project_id"], dataset_a["dataset_id"], threshold_a["threshold_profile_id"]
        )
        dataset_b = self.create_dataset(project_b["project_id"], 105)
        with self.assertRaisesRegex(ValueError, "dataset must belong"):
            self.decisions.create_snapshot(
                **self.decision_kwargs(
                    project_id=project_a["project_id"],
                    scenario_id=scenario_a["scenario_id"],
                    dataset_id=dataset_b["dataset_id"],
                    threshold_profile_id=threshold_a["threshold_profile_id"],
                )
            )

    def test_decision_rejects_threshold_from_another_project(self):
        project_a = self.create_project("PVE-A")
        project_b = self.create_project("PVE-B")
        dataset_a = self.create_dataset(project_a["project_id"], 106)
        threshold_a = self.create_threshold(project_a["project_id"], 106)
        scenario_a = self.create_scenario(
            project_a["project_id"], dataset_a["dataset_id"], threshold_a["threshold_profile_id"]
        )
        threshold_b = self.create_threshold(project_b["project_id"], 107)
        with self.assertRaisesRegex(ValueError, "threshold profile must be global"):
            self.decisions.create_snapshot(
                **self.decision_kwargs(
                    project_id=project_a["project_id"],
                    scenario_id=scenario_a["scenario_id"],
                    dataset_id=dataset_a["dataset_id"],
                    threshold_profile_id=threshold_b["threshold_profile_id"],
                )
            )

    def test_decision_rejects_dataset_different_from_scenario_dataset(self):
        project = self.create_project("PVE-A")
        dataset_one = self.create_dataset(project["project_id"], 108)
        dataset_two = self.create_dataset(project["project_id"], 109)
        threshold = self.create_threshold(project["project_id"], 108)
        scenario = self.create_scenario(
            project["project_id"], dataset_one["dataset_id"], threshold["threshold_profile_id"]
        )
        with self.assertRaisesRegex(ValueError, "match the scenario dataset"):
            self.decisions.create_snapshot(
                **self.decision_kwargs(
                    project_id=project["project_id"],
                    scenario_id=scenario["scenario_id"],
                    dataset_id=dataset_two["dataset_id"],
                    threshold_profile_id=threshold["threshold_profile_id"],
                )
            )

    def test_decision_rejects_threshold_different_from_scenario_threshold(self):
        project = self.create_project("PVE-A")
        dataset = self.create_dataset(project["project_id"], 110)
        threshold_one = self.create_threshold(project["project_id"], 110)
        threshold_two = self.thresholds.create_version(
            project_id=project["project_id"],
            profile_name="Alternate",
            profile={"minimum_annual_savings": 111},
        )
        scenario = self.create_scenario(
            project["project_id"],
            dataset["dataset_id"],
            threshold_one["threshold_profile_id"],
        )
        with self.assertRaisesRegex(ValueError, "match the scenario threshold"):
            self.decisions.create_snapshot(
                **self.decision_kwargs(
                    project_id=project["project_id"],
                    scenario_id=scenario["scenario_id"],
                    dataset_id=dataset["dataset_id"],
                    threshold_profile_id=threshold_two["threshold_profile_id"],
                )
            )


if __name__ == "__main__":
    unittest.main()
