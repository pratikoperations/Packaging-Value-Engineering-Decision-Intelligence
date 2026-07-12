import json
import unittest
from pathlib import Path

from src.scenario_engine import ScenarioInputs, evaluate_scenario

ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


class TestScenarioEngine(unittest.TestCase):
    def test_base_scenario_matches_existing_outputs(self):
        data = load_demo()
        result = evaluate_scenario(
            data,
            ScenarioInputs(
                annual_volume=1200000,
                cost_adjustment_percent_by_alternative={},
                material_adjustment_percent_by_alternative={},
            ),
        )
        self.assertEqual(result.alternatives["ALT-B"].unit_cost, 43.5)
        self.assertEqual(result.alternatives["ALT-B"].annual_savings_vs_baseline, 10680000.0)

    def test_volume_changes_annual_savings_not_unit_cost(self):
        data = load_demo()
        result = evaluate_scenario(
            data,
            ScenarioInputs(annual_volume=600000, cost_adjustment_percent_by_alternative={}, material_adjustment_percent_by_alternative={}),
        )
        self.assertEqual(result.alternatives["ALT-B"].unit_cost, 43.5)
        self.assertEqual(result.alternatives["ALT-B"].annual_savings_vs_baseline, 5340000.0)

    def test_alternative_cost_adjustment_is_explicit(self):
        data = load_demo()
        result = evaluate_scenario(
            data,
            ScenarioInputs(
                annual_volume=1200000,
                cost_adjustment_percent_by_alternative={"ALT-B": 10},
                material_adjustment_percent_by_alternative={},
            ),
        )
        self.assertEqual(result.alternatives["ALT-B"].unit_cost, 47.85)
        self.assertIn("Unit-cost adjustment: 10%.", result.alternatives["ALT-B"].assumptions)

    def test_material_adjustment_changes_case_weight(self):
        data = load_demo()
        result = evaluate_scenario(
            data,
            ScenarioInputs(
                annual_volume=1200000,
                cost_adjustment_percent_by_alternative={},
                material_adjustment_percent_by_alternative={"ALT-A": -10},
            ),
        )
        self.assertEqual(result.alternatives["ALT-A"].case_weight_g, 792.0)

    def test_unknown_alternative_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown cost adjustment alternatives"):
            evaluate_scenario(
                load_demo(),
                ScenarioInputs(1200000, {"UNKNOWN": 5}, {}),
            )

    def test_adjustment_out_of_range_rejected(self):
        with self.assertRaisesRegex(ValueError, "between -50 and 100"):
            evaluate_scenario(
                load_demo(),
                ScenarioInputs(1200000, {"ALT-A": 101}, {}),
            )


if __name__ == "__main__":
    unittest.main()
