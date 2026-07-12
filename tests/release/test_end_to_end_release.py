import json
import unittest
from pathlib import Path

from src.data_models import validate_dataset
from src.exports import (
    assemble_decision_package,
    render_decision_package_json,
    render_decision_package_markdown,
)
from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.technical_qualification import evaluate_technical_qualification

ROOT = Path(__file__).resolve().parents[2]
DEMO_PATH = ROOT / "data" / "demo" / "corrugated_shipping_cases.json"
APP_PATH = ROOT / "app.py"
README_PATH = ROOT / "README.md"
CHECKLIST_PATH = ROOT / "docs" / "FINAL_RELEASE_CHECKLIST.md"
DEMO_GUIDE_PATH = ROOT / "docs" / "INTERVIEW_DEMO_GUIDE.md"


def load_demo():
    return json.loads(DEMO_PATH.read_text(encoding="utf-8"))


def build_release_package():
    dataset = load_demo()
    validation = validate_dataset(dataset)
    if not validation.is_valid:
        raise AssertionError(f"Synthetic demo data failed validation: {validation.issues}")
    scenario = evaluate_scenario(dataset, ScenarioInputs(1200000, {}, {}))
    qualifications = evaluate_technical_qualification(dataset)
    risks = evaluate_risks(dataset)
    recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
    package = assemble_decision_package(
        dataset,
        scenario,
        qualifications,
        risks,
        recommendation,
        source_commit="PVE-0.7-RELEASE-TEST",
        generated_at="2026-07-12T08:00:00Z",
    )
    return dataset, scenario, qualifications, risks, recommendation, package


class TestFinalRelease(unittest.TestCase):
    def test_end_to_end_decision_flow(self):
        dataset, scenario, qualifications, risks, recommendation, package = build_release_package()
        alternative_ids = {item["alternative_id"] for item in dataset["packaging_alternatives"]}
        self.assertEqual(set(scenario.alternatives), alternative_ids)
        self.assertEqual(set(qualifications), alternative_ids)
        self.assertEqual(set(risks), alternative_ids)
        proposed_ids = {
            item["alternative_id"]
            for item in dataset["packaging_alternatives"]
            if item["status"] == "proposed"
        }
        self.assertEqual(set(recommendation.alternatives), proposed_ids)
        self.assertEqual(
            {item["alternative_id"] for item in package["alternatives"]},
            proposed_ids,
        )

    def test_release_exports_are_deterministic_and_readable(self):
        first = build_release_package()[-1]
        second = build_release_package()[-1]
        self.assertEqual(first, second)
        rendered_json = render_decision_package_json(first)
        rendered_markdown = render_decision_package_markdown(first)
        self.assertEqual(json.loads(rendered_json), first)
        self.assertIn("## Executive Summary", rendered_markdown)
        self.assertIn("## Decision Controls", rendered_markdown)

    def test_decision_controls_preserve_human_approval(self):
        controls = build_release_package()[-1]["decision_controls"]
        self.assertTrue(controls["read_only"])
        self.assertTrue(controls["engineering_validation_required"])
        self.assertFalse(controls["autonomous_technical_approval"])
        self.assertFalse(controls["supplier_allocation"])
        self.assertFalse(controls["external_system_integration"])
        self.assertFalse(controls["integration_contract_finalized"])

    def test_ui_smoke_contract(self):
        app = APP_PATH.read_text(encoding="utf-8")
        required_markers = (
            'st.title("Packaging Value Engineering Decision Intelligence")',
            'st.sidebar.header("Scenario Inputs")',
            'st.subheader("Scenario Comparison")',
            'st.subheader("Preferred Alternative")',
            'st.subheader("Explainable Recommendation Detail")',
            'st.subheader("Decision Package Export")',
            '"Download machine-readable JSON"',
            '"Download human-readable report"',
            "does not approve packaging designs autonomously",
        )
        for marker in required_markers:
            self.assertIn(marker, app)

    def test_ui_discloses_synthetic_demonstration_data(self):
        app = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("This application uses synthetic demonstration data only.", app)
        self.assertIn(
            "It must not be treated as validated supplier, laboratory, production,",
            app,
        )
        self.assertIn("engineering-trial, or commercial data.", app)

    def test_release_documentation_is_complete(self):
        readme = README_PATH.read_text(encoding="utf-8")
        demo_guide = DEMO_GUIDE_PATH.read_text(encoding="utf-8")
        checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
        for marker in (
            "## Quick Start",
            "## Decision Flow",
            "## Interview Demonstration",
            "## Scope and Limitations",
            "streamlit run app.py",
        ):
            self.assertIn(marker, readme)
        self.assertIn("## Demo Flow", demo_guide)
        self.assertIn("## Acceptance Criteria", checklist)

    def test_integration_contract_remains_draft(self):
        contract = (
            ROOT / "integration" / "contracts" / "PVE_CONTRACT_V1_DRAFT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("draft", contract.lower())


if __name__ == "__main__":
    unittest.main()
