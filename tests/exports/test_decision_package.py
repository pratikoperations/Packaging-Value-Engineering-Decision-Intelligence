import copy
import json
import unittest
from pathlib import Path

from src.exports import (
    assemble_decision_package,
    render_decision_package_json,
    render_decision_package_markdown,
    validate_decision_package,
)
from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.technical_qualification import evaluate_technical_qualification

ROOT = Path(__file__).resolve().parents[2]
SOURCE_COMMIT = "TEST-COMMIT-123"
GENERATED_AT = "2026-07-12T07:00:00Z"


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


def build_package(data=None):
    dataset = data or load_demo()
    scenario = evaluate_scenario(dataset, ScenarioInputs(1200000, {}, {}))
    qualifications = evaluate_technical_qualification(dataset)
    risks = evaluate_risks(dataset)
    recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
    return assemble_decision_package(
        dataset,
        scenario,
        qualifications,
        risks,
        recommendation,
        source_commit=SOURCE_COMMIT,
        generated_at=GENERATED_AT,
    )


class TestDecisionPackageExport(unittest.TestCase):
    def test_package_contains_required_sections(self):
        package = build_package()
        self.assertEqual(
            set(package),
            {
                "metadata",
                "executive_summary",
                "project",
                "scenario",
                "baseline",
                "alternatives",
                "decision_controls",
            },
        )
        self.assertEqual(len(package["alternatives"]), 3)

    def test_package_is_deterministic_for_same_inputs(self):
        self.assertEqual(build_package(), build_package())
        self.assertEqual(
            render_decision_package_json(build_package()),
            render_decision_package_json(build_package()),
        )

    def test_package_contains_full_decision_basis(self):
        package = build_package()
        alt_b = next(item for item in package["alternatives"] if item["alternative_id"] == "ALT-B")
        self.assertIn("cost_and_material", alt_b)
        self.assertIn("technical_qualification", alt_b)
        self.assertIn("risk", alt_b)
        self.assertIn("recommendation", alt_b)
        self.assertTrue(alt_b["scenario_assumptions"])

    def test_controls_prevent_autonomous_or_allocation_claims(self):
        controls = build_package()["decision_controls"]
        self.assertFalse(controls["autonomous_technical_approval"])
        self.assertFalse(controls["supplier_allocation"])
        self.assertFalse(controls["integration_contract_finalized"])
        self.assertTrue(controls["engineering_validation_required"])

    def test_json_export_is_machine_readable_and_sorted(self):
        rendered = render_decision_package_json(build_package())
        parsed = json.loads(rendered)
        self.assertEqual(parsed["metadata"]["source_commit"], SOURCE_COMMIT)
        self.assertLess(rendered.index('"alternatives"'), rendered.index('"baseline"'))

    def test_markdown_export_is_human_readable(self):
        rendered = render_decision_package_markdown(build_package())
        self.assertIn("# Packaging Value Engineering Decision Package", rendered)
        self.assertIn("## Executive Summary", rendered)
        self.assertIn("## Alternative Comparison", rendered)
        self.assertIn("Autonomous technical approval: No", rendered)

    def test_validation_rejects_missing_section(self):
        package = build_package()
        del package["executive_summary"]
        with self.assertRaisesRegex(ValueError, "missing top-level sections"):
            validate_decision_package(package)

    def test_validation_rejects_control_tampering(self):
        package = build_package()
        package["decision_controls"]["autonomous_technical_approval"] = True
        with self.assertRaisesRegex(ValueError, "autonomous_technical_approval"):
            validate_decision_package(package)

    def test_assembly_rejects_missing_scenario_alternative(self):
        dataset = load_demo()
        scenario = evaluate_scenario(dataset, ScenarioInputs(1200000, {}, {}))
        qualifications = evaluate_technical_qualification(dataset)
        risks = evaluate_risks(dataset)
        recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
        damaged = copy.deepcopy(scenario.alternatives)
        del damaged["ALT-C"]
        broken_scenario = type(scenario)(annual_volume=scenario.annual_volume, alternatives=damaged)
        with self.assertRaisesRegex(ValueError, "scenario missing alternatives"):
            assemble_decision_package(
                dataset,
                broken_scenario,
                qualifications,
                risks,
                recommendation,
                source_commit=SOURCE_COMMIT,
                generated_at=GENERATED_AT,
            )

    def test_source_commit_and_generated_at_are_required(self):
        dataset = load_demo()
        scenario = evaluate_scenario(dataset, ScenarioInputs(1200000, {}, {}))
        qualifications = evaluate_technical_qualification(dataset)
        risks = evaluate_risks(dataset)
        recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
        with self.assertRaisesRegex(ValueError, "source_commit"):
            assemble_decision_package(
                dataset,
                scenario,
                qualifications,
                risks,
                recommendation,
                source_commit="",
                generated_at=GENERATED_AT,
            )


if __name__ == "__main__":
    unittest.main()
