from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from src.application import ProjectService
from src.decision_snapshots import DecisionSnapshotError, DecisionSnapshotService
from src.persistence import (
    Database,
    DatasetRepository,
    DecisionRepository,
    ProjectRepository,
    ScenarioRepository,
    ThresholdRepository,
)
from src.persistence.migrations import initialize_database
from src.thresholds import DEFAULT_CONTROLLED_PROFILE

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "pages" / "05_Decision_History.py"
INTERVIEW_GUIDE = ROOT / "docs" / "interview" / "PVE_1.0_FINAL_INTERVIEW_DEMO.md"
RELEASE_CHECKLIST = ROOT / "docs" / "release" / "PVE_1.0_FINAL_RELEASE_CHECKLIST.md"


class DecisionSnapshotTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "decisions.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project_service = ProjectService(self.projects)
        self.datasets = DatasetRepository(self.database)
        self.thresholds = ThresholdRepository(self.database)
        self.scenarios = ScenarioRepository(self.database)
        self.decisions = DecisionRepository(self.database)
        self.service = DecisionSnapshotService(self.scenarios, self.decisions)
        self.project = self.project_service.create_project(
            project_code="PVE-DECISION-001",
            project_name="Decision project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100000,
        )
        self.dataset = self.datasets.create_version(
            project_id=self.project["project_id"],
            source_type="json",
            canonical_data={"dataset_type": "user_upload", "packaging_alternatives": []},
            validation_status="valid",
        )
        self.threshold = self.thresholds.create_version(
            project_id=None,
            profile_name="PVE Controlled Default",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def result_record(
        self,
        *,
        status: str,
        savings: float,
        material_change: float = -1.0,
        technical_status: str = "qualified",
        risk_level: str = "low",
        threshold_passed: bool = True,
    ) -> dict:
        return {
            "alternative_id": "ALT-A",
            "alternative_name": "Alternative A",
            "annual_savings_vs_baseline": savings,
            "material_change_percent_vs_baseline": material_change,
            "technical_status": technical_status,
            "technical_reasons": [],
            "technical_validation_required": [],
            "risk_level": risk_level,
            "risk_data_complete": True,
            "risk_reasons": [],
            "risk_validation_required": [],
            "business_thresholds_passed": threshold_passed,
            "business_threshold_reasons": [] if threshold_passed else ["Savings gate failed."],
            "control_status": status,
            "control_reasons": [],
            "engineering_validation_required": True,
            "autonomous_approval_allowed": False,
        }

    def create_scenario(self, alternatives: dict | None = None, *, project_id: str | None = None):
        project_id = project_id or self.project["project_id"]
        results = {
            "threshold_profile": {
                "threshold_profile_id": self.threshold["threshold_profile_id"],
                "profile_name": "PVE Controlled Default",
                "version_number": 1,
                "profile": DEFAULT_CONTROLLED_PROFILE,
            },
            "mandatory_engineering_controls": {
                "engineering_validation_required": True,
                "autonomous_approval_allowed": False,
                "critical_risk_blocked": True,
                "not_qualified_blocked": True,
                "insufficient_data_cannot_be_recommended": True,
            },
            "alternatives": alternatives
            or {
                "ALT-BASE": self.result_record(status="eligible_for_engineering_review", savings=0),
                "ALT-A": self.result_record(status="eligible_for_engineering_review", savings=50000),
            },
        }
        return self.scenarios.create(
            project_id=project_id,
            dataset_id=self.dataset["dataset_id"],
            threshold_profile_id=self.threshold["threshold_profile_id"],
            scenario_name="Saved controlled scenario",
            assumptions={"annual_volume": 100000},
            results=results,
        )

    def test_available_scenarios_are_project_scoped(self):
        scenario = self.create_scenario()
        records = self.service.available_scenarios(self.project["project_id"])
        self.assertEqual([record["scenario_id"] for record in records], [scenario["scenario_id"]])

    def test_prepare_preserves_exact_references(self):
        scenario = self.create_scenario()
        prepared = self.service.prepare(
            project_id=self.project["project_id"],
            scenario_id=scenario["scenario_id"],
        )
        self.assertEqual(prepared.project_id, self.project["project_id"])
        self.assertEqual(prepared.scenario_id, scenario["scenario_id"])
        self.assertEqual(prepared.dataset_id, self.dataset["dataset_id"])
        self.assertEqual(prepared.threshold_profile_id, self.threshold["threshold_profile_id"])

    def test_prepare_rejects_cross_project_scenario(self):
        other = self.project_service.create_project(
            project_code="PVE-DECISION-002",
            project_name="Other project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1,
        )
        scenario = self.create_scenario()
        with self.assertRaisesRegex(DecisionSnapshotError, "active project"):
            self.service.prepare(project_id=other["project_id"], scenario_id=scenario["scenario_id"])

    def test_eligible_alternative_is_recommended_for_engineering_review(self):
        prepared = self.service.prepare(
            project_id=self.project["project_id"],
            scenario_id=self.create_scenario()["scenario_id"],
        )
        self.assertEqual(prepared.status, "recommended_for_engineering_review")
        self.assertEqual(prepared.preferred_alternative_id, "ALT-A")

    def test_conditional_alternative_is_not_approved(self):
        scenario = self.create_scenario(
            {"ALT-A": self.result_record(status="conditionally_eligible_for_review", savings=50000)}
        )
        prepared = self.service.prepare(
            project_id=self.project["project_id"], scenario_id=scenario["scenario_id"]
        )
        self.assertEqual(prepared.status, "conditionally_recommended_for_engineering_review")
        self.assertFalse(prepared.recommendation["autonomous_approval"])
        self.assertTrue(prepared.recommendation["human_approval_required"])

    def test_insufficient_data_has_no_preferred_alternative(self):
        scenario = self.create_scenario(
            {"ALT-A": self.result_record(status="insufficient_data", savings=50000, technical_status="insufficient_data")}
        )
        prepared = self.service.prepare(
            project_id=self.project["project_id"], scenario_id=scenario["scenario_id"]
        )
        self.assertEqual(prepared.status, "insufficient_data")
        self.assertIsNone(prepared.preferred_alternative_id)

    def test_blocked_result_has_no_preferred_alternative(self):
        scenario = self.create_scenario(
            {"ALT-A": self.result_record(status="blocked", savings=50000, technical_status="not_qualified")}
        )
        prepared = self.service.prepare(
            project_id=self.project["project_id"], scenario_id=scenario["scenario_id"]
        )
        self.assertEqual(prepared.status, "blocked")
        self.assertIsNone(prepared.preferred_alternative_id)

    def test_business_threshold_failure_is_explainable(self):
        scenario = self.create_scenario(
            {"ALT-A": self.result_record(status="business_threshold_failed", savings=100, threshold_passed=False)}
        )
        prepared = self.service.prepare(
            project_id=self.project["project_id"], scenario_id=scenario["scenario_id"]
        )
        self.assertEqual(prepared.status, "not_recommended_business_threshold_failed")
        self.assertEqual(prepared.gate_results["selected_business_threshold_reasons"], ["Savings gate failed."])

    def test_baseline_is_never_selected_as_preferred_alternative(self):
        alternatives = {
            "ALT-BASE": self.result_record(status="eligible_for_engineering_review", savings=999999),
            "ALT-A": self.result_record(status="eligible_for_engineering_review", savings=1000),
        }
        prepared = self.service.prepare(
            project_id=self.project["project_id"],
            scenario_id=self.create_scenario(alternatives)["scenario_id"],
        )
        self.assertEqual(prepared.preferred_alternative_id, "ALT-A")

    def test_saved_snapshot_preserves_exact_references(self):
        scenario = self.create_scenario()
        prepared = self.service.prepare(
            project_id=self.project["project_id"], scenario_id=scenario["scenario_id"]
        )
        saved = self.service.save(prepared)
        self.assertEqual(saved["project_id"], self.project["project_id"])
        self.assertEqual(saved["scenario_id"], scenario["scenario_id"])
        self.assertEqual(saved["dataset_id"], self.dataset["dataset_id"])
        self.assertEqual(saved["threshold_profile_id"], self.threshold["threshold_profile_id"])

    def test_repository_revalidates_scenario_dataset_and_threshold_links(self):
        scenario = self.create_scenario()
        prepared = self.service.prepare(
            project_id=self.project["project_id"], scenario_id=scenario["scenario_id"]
        )
        tampered = replace(prepared, dataset_id="dataset-missing")
        with self.assertRaises(KeyError):
            self.service.save(tampered)

    def test_decision_snapshot_is_immutable(self):
        prepared = self.service.prepare(
            project_id=self.project["project_id"],
            scenario_id=self.create_scenario()["scenario_id"],
        )
        saved = self.service.save(prepared)
        with self.assertRaises(Exception):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE decision_snapshots SET status = 'approved' WHERE decision_snapshot_id = ?",
                    (saved["decision_snapshot_id"],),
                )

    def test_history_is_project_scoped_and_decoded(self):
        prepared = self.service.prepare(
            project_id=self.project["project_id"],
            scenario_id=self.create_scenario()["scenario_id"],
        )
        self.service.save(prepared)
        records = self.service.history(self.project["project_id"])
        self.assertEqual(len(records), 1)
        self.assertIsInstance(records[0]["recommendation"], dict)
        self.assertIsInstance(records[0]["gate_results"], dict)

    def test_snapshot_records_no_autonomous_approval(self):
        prepared = self.service.prepare(
            project_id=self.project["project_id"],
            scenario_id=self.create_scenario()["scenario_id"],
        )
        self.assertFalse(prepared.recommendation["autonomous_approval"])
        self.assertTrue(prepared.recommendation["engineering_validation_required"])
        self.assertTrue(prepared.recommendation["human_approval_required"])

    def test_page_static_contract(self):
        page = PAGE.read_text(encoding="utf-8")
        for marker in (
            "Decision Snapshot and History",
            "Prepare controlled decision snapshot",
            "Save immutable decision snapshot",
            "Controlled Decision History",
            "Technical, risk, threshold, and control evidence",
            "autonomous approval is prohibited",
            "Archived projects are read-only",
        ):
            self.assertIn(marker, page)

    def test_page_excludes_unapproved_scope(self):
        page = PAGE.read_text(encoding="utf-8")
        for prohibited in (
            "Approve packaging",
            "Supplier allocation",
            "Authentication",
            "st.file_uploader",
            "External database",
        ):
            self.assertNotIn(prohibited, page)

    def test_final_release_documents_exist_and_preserve_boundaries(self):
        interview = INTERVIEW_GUIDE.read_text(encoding="utf-8")
        release = RELEASE_CHECKLIST.read_text(encoding="utf-8")
        self.assertIn("PVE 1.0 Final Interview Demonstration", interview)
        self.assertIn("engineering validation", interview.lower())
        self.assertIn("Final Release Checklist", release)
        self.assertIn("no autonomous approval", release.lower())


if __name__ == "__main__":
    unittest.main()
