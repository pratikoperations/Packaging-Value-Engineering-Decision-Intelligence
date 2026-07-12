import copy
import json
import unittest
from pathlib import Path

from src.risk_engine import evaluate_risks

ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


class TestRiskEngine(unittest.TestCase):
    def test_demo_quality_risk_is_high(self):
        outcome = evaluate_risks(load_demo())["ALT-B"]
        self.assertEqual(outcome.overall_level, "high")
        self.assertFalse(outcome.data_complete)
        self.assertTrue(any("quality risk is high" in reason.lower() for reason in outcome.reasons))

    def test_missing_categories_are_explicit(self):
        outcome = evaluate_risks(load_demo())["ALT-A"]
        indicator_map = {indicator.risk_type: indicator for indicator in outcome.indicators}
        self.assertEqual(indicator_map["quality"].effective_level, "not_recorded")
        self.assertEqual(indicator_map["supply"].effective_level, "not_recorded")
        self.assertTrue(any("Complete quality risk assessment" == item for item in outcome.validation_required))

    def test_probability_escalates_effective_level(self):
        data = load_demo()
        data["risk_records"] = [
            {"risk_id":"R1","alternative_id":"ALT-A","risk_type":"quality","level":"low","probability_percent":80},
            {"risk_id":"R2","alternative_id":"ALT-A","risk_type":"supply","level":"low","probability_percent":10},
            {"risk_id":"R3","alternative_id":"ALT-A","risk_type":"implementation","level":"low","probability_percent":10},
        ]
        outcome = evaluate_risks(data)["ALT-A"]
        self.assertEqual(outcome.overall_level, "critical")
        self.assertTrue(outcome.data_complete)

    def test_complete_low_risk_record_set(self):
        data = load_demo()
        data["risk_records"] = []
        for alternative in data["packaging_alternatives"]:
            for risk_type in ("quality", "supply", "implementation"):
                data["risk_records"].append({
                    "risk_id": f"R-{alternative['alternative_id']}-{risk_type}",
                    "alternative_id": alternative["alternative_id"],
                    "risk_type": risk_type,
                    "level": "low",
                    "probability_percent": 10,
                })
        outcome = evaluate_risks(data)["ALT-C"]
        self.assertEqual(outcome.overall_level, "low")
        self.assertTrue(outcome.data_complete)
        self.assertFalse(outcome.validation_required)

    def test_out_of_range_probability_rejected(self):
        data = load_demo()
        data["risk_records"][0]["probability_percent"] = 101
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            evaluate_risks(data)

    def test_multiple_records_use_highest_effective_level(self):
        data = load_demo()
        duplicate = copy.deepcopy(data["risk_records"][0])
        duplicate["risk_id"] = "RISK-A-2"
        duplicate["level"] = "high"
        duplicate["probability_percent"] = 60
        data["risk_records"].append(duplicate)
        outcome = evaluate_risks(data)["ALT-A"]
        implementation = next(item for item in outcome.indicators if item.risk_type == "implementation")
        self.assertEqual(implementation.effective_level, "high")


if __name__ == "__main__":
    unittest.main()
