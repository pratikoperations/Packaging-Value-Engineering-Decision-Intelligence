import json
import unittest
from pathlib import Path

from src.cost_engine import analyze_costs

ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


class TestCostEngine(unittest.TestCase):
    def test_baseline_cost_metrics(self):
        result = analyze_costs(load_demo())["ALT-BASE"]
        self.assertEqual(result.currency, "INR")
        self.assertEqual(result.unit_cost, 52.4)
        self.assertEqual(result.annual_cost, 62880000.0)
        self.assertEqual(result.annual_savings_vs_baseline, 0.0)

    def test_alternative_savings(self):
        result = analyze_costs(load_demo())["ALT-B"]
        self.assertEqual(result.unit_savings_vs_baseline, 8.9)
        self.assertEqual(result.annual_savings_vs_baseline, 10680000.0)
        self.assertAlmostEqual(result.cost_change_percent_vs_baseline, -16.984733, places=6)

    def test_currency_mismatch_rejected(self):
        data = load_demo()
        data["cost_inputs"][0]["currency"] = "USD"
        with self.assertRaisesRegex(ValueError, "must match project currency"):
            analyze_costs(data)

    def test_missing_cost_input_rejected(self):
        data = load_demo()
        data["cost_inputs"] = [r for r in data["cost_inputs"] if r["alternative_id"] != "ALT-C"]
        with self.assertRaisesRegex(ValueError, "Missing cost inputs"):
            analyze_costs(data)


if __name__ == "__main__":
    unittest.main()
