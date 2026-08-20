from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.application import ProjectService
from src.persistence import (
    Database,
    DatasetRepository,
    ProjectRepository,
    ScenarioRepository,
    ThresholdRepository,
)
from src.persistence.migrations import initialize_database
from src.scenario_execution import ControlledScenarioService, ScenarioExecutionError
from src.thresholds import DEFAULT_CONTROLLED_PROFILE

ROOT = Path(__file__).resolve().parents[2]
DEMO = ROOT / "data" / "demo" / "corrugated_shipping_cases.json"
PAGE = ROOT / "pages" / "04_Controlled_Scenarios.py"


class ControlledScenarioTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "scenario.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project_service = ProjectService(self.projects)
        self.datasets = DatasetRepository(self.database)
        self.thresholds = ThresholdRepository(self.database)
        self.scenarios = ScenarioRepository(self.database)
        self.service = ControlledScenarioService(
            self.datasets,
            self.thresholds,
            self.scenarios,
        )
        self.project = self.project_service.create_project(
            project_code="PVE-SCENARIO-001",
            project_name="Scenario project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1200000,
        )
        self.dataset = self.datasets.create_version(
            project_id=self.project["project_id"],
            source_type="json",
            canonical_data=json.loads(DEMO.read_text(encoding="utf-8")),
            validation_status="valid",
        )
        self.threshold = self.thresholds.create_version(
            project_id=None,
            profile_name="PVE Controlled Default",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def evaluate(self, **overrides):
        values = {
            "project_id": self.project["project_id"],
            "dataset_id": self.dataset["dataset_id"],
            "threshold_profile_id": self.threshold["threshold_profile_id"],
            "scenario_name": "Base scenario",
            "annual_volume": 1200000,
            "cost_adjustments": {},
            "material_adjustments": {},
        }
        values.update(overrides)
        return self.service.evaluate(**values)

    def test_available_datasets_are_project_scoped(self):
        records = self.service.available_datasets(self.project["project_id"])
        self.assertEqual([record["dataset_id"] for record in records], [self.dataset["dataset_id"]])

    def test_available_thresholds_include_global_profile(self):
        records = self.service.available_thresholds(self.project["project_id"])
        self.assertIn(self.threshold["threshold_profile_id"], {record["threshold_profile_id"] for record in records})

    def test_rejects_cross_project_dataset(self):
        other = self.project_service.create_project(
            project_code="PVE-SCENARIO-002",
            project_name="Other",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1,
        )
        with self.assertRaisesRegex(ScenarioExecutionError, "Dataset must belong"):
            self.evaluate(project_id=other["project_id"])

    def test_rejects_cross_project_threshold(self):
        other = self.project_service.create_project(
            project_code="PVE-SCENARIO-002",
            project_name="Other",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1,
        )
        other_threshold = self.thresholds.create_version(
            project_id=other["project_id"],
            profile_name="Other",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        with self.assertRaisesRegex(ScenarioExecutionError, "Threshold profile"):
            self.evaluate(threshold_profile_id=other_threshold["threshold_profile_id"])

    def test_requires_scenario_name(self):
        with self.assertRaisesRegex(ScenarioExecutionError, "Scenario name"):
            self.evaluate(scenario_name="   ")

    def test_runs_existing_deterministic_scenario_engine(self):
        result = self.evaluate(
            annual_volume=1000000,
            cost_adjustments={"ALT-A": 5},
            material_adjustments={"ALT-A": -5},
        )
        self.assertEqual(result.results["annual_volume"], 1000000.0)
        self.assertIn("ALT-A", result.results["alternatives"])

    def test_results_include_business_threshold_explanation(self):
        result = self.evaluate()
        record = result.results["alternatives"]["ALT-A"]
        self.assertIn("business_thresholds_passed", record)
        self.assertIn("business_threshold_reasons", record)

    def test_results_include_mandatory_controls(self):
        result = self.evaluate()
        controls = result.results["mandatory_engineering_controls"]
        self.assertTrue(controls["engineering_validation_required"])
        self.assertFalse(controls["autonomous_approval_allowed"])
        self.assertTrue(controls["critical_risk_blocked"])
        self.assertTrue(controls["not_qualified_blocked"])

    def test_insufficient_technical_data_cannot_be_eligible(self):
        result = self.evaluate()
        self.assertEqual(
            result.results["alternatives"]["ALT-A"]["control_status"],
            "insufficient_data",
        )

    def test_critical_risk_is_blocked(self):
        data = json.loads(DEMO.read_text(encoding="utf-8"))
        data["risk_records"].append(
            {
                "risk_id": "RISK-A-CRITICAL",
                "alternative_id": "ALT-A",
                "risk_type": "quality",
                "level": "critical",
                "probability_percent": 80,
            }
        )
        dataset = self.datasets.create_version(
            project_id=self.project["project_id"],
            source_type="json",
            canonical_data=data,
            validation_status="valid",
        )
        result = self.evaluate(dataset_id=dataset["dataset_id"])
        self.assertEqual(result.results["alternatives"]["ALT-A"]["control_status"], "blocked")

    def test_decision_boundary_prohibits_approval(self):
        result = self.evaluate()
        self.assertIn("human approval remain mandatory", result.results["decision_boundary"])

    def test_save_creates_immutable_scenario_record(self):
        evaluated = self.evaluate()
        saved = self.service.save(evaluated)
        self.assertEqual(saved["dataset_id"], self.dataset["dataset_id"])
        with self.assertRaises(Exception):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE scenarios SET scenario_name = 'Changed' WHERE scenario_id = ?",
                    (saved["scenario_id"],),
                )

    def test_saved_record_references_exact_threshold_version(self):
        evaluated = self.evaluate()
        saved = self.service.save(evaluated)
        self.assertEqual(saved["threshold_profile_id"], self.threshold["threshold_profile_id"])

    def test_saved_assumptions_are_explicit(self):
        evaluated = self.evaluate(
            cost_adjustments={"ALT-B": 3.5},
            material_adjustments={"ALT-B": -4.0},
        )
        saved = self.service.save(evaluated)
        assumptions = json.loads(saved["assumptions_json"])
        self.assertEqual(assumptions["cost_adjustment_percent_by_alternative"]["ALT-B"], 3.5)
        self.assertEqual(assumptions["material_adjustment_percent_by_alternative"]["ALT-B"], -4.0)

    def test_repository_revalidates_cross_project_integrity_on_save(self):
        other = self.project_service.create_project(
            project_code="PVE-SCENARIO-002",
            project_name="Other",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1,
        )
        evaluated = self.evaluate()
        tampered = type(evaluated)(
            project_id=other["project_id"],
            dataset_id=evaluated.dataset_id,
            threshold_profile_id=evaluated.threshold_profile_id,
            scenario_name=evaluated.scenario_name,
            assumptions=evaluated.assumptions,
            results=evaluated.results,
        )
        with self.assertRaisesRegex(ValueError, "same project"):
            self.service.save(tampered)

    def test_page_static_contract(self):
        page = PAGE.read_text(encoding="utf-8")
        for marker in (
            "Controlled Scenario Execution",
            "Immutable dataset version",
            "Immutable threshold profile version",
            "Run deterministic scenario",
            "Save immutable scenario record",
            "Refresh complete demonstration dataset",
            "seed_portfolio_demo(DATABASE_PATH)",
            "Engineering validation",
            "autonomous approval is prohibited",
        ):
            self.assertIn(marker, page)

    def test_page_excludes_unapproved_scope(self):
        page = PAGE.read_text(encoding="utf-8")
        for prohibited in (
            "Decision history",
            "Approve packaging",
            "Supplier allocation",
            "st.file_uploader",
            "Authentication",
        ):
            self.assertNotIn(prohibited, page)


if __name__ == "__main__":
    unittest.main()
