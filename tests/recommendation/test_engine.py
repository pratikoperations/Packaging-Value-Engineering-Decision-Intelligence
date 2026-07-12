import json
import unittest
from pathlib import Path

from src.recommendation import recommend_alternatives
from src.risk_engine import RiskIndicator, RiskOutcome, evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.technical_qualification import QualificationOutcome, evaluate_technical_qualification

ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


def base_scenario(data):
    return evaluate_scenario(data, ScenarioInputs(1200000, {}, {}))


def qualified(alternative_id: str, status: str = "qualified") -> QualificationOutcome:
    validation = ("Close technical condition",) if status == "conditionally_qualified" else ()
    return QualificationOutcome(alternative_id, status, (), (), ("EV-006",), validation)


def risk(alternative_id: str, level: str = "low", complete: bool = True) -> RiskOutcome:
    indicators = tuple(
        RiskIndicator(name, level, 10.0, level, ())
        for name in ("quality", "supply", "implementation")
    )
    return RiskOutcome(alternative_id, level, complete, indicators, (), ())


class TestRecommendationEngine(unittest.TestCase):
    def test_demo_is_insufficient_data(self):
        data = load_demo()
        result = recommend_alternatives(
            data,
            base_scenario(data),
            evaluate_technical_qualification(data),
            evaluate_risks(data),
        )
        self.assertEqual(result.alternatives["ALT-B"].status, "insufficient_data")
        self.assertIsNone(result.preferred_alternative_id)

    def test_qualified_low_risk_saving_alternative_recommended(self):
        data = load_demo()
        qualifications = {alt: qualified(alt) for alt in ("ALT-BASE", "ALT-A", "ALT-B", "ALT-C")}
        risks = {alt: risk(alt) for alt in qualifications}
        result = recommend_alternatives(data, base_scenario(data), qualifications, risks)
        self.assertEqual(result.alternatives["ALT-B"].status, "recommended")
        self.assertEqual(result.preferred_alternative_id, "ALT-B")

    def test_failed_qualification_not_recommended(self):
        data = load_demo()
        qualifications = {alt: qualified(alt) for alt in ("ALT-BASE", "ALT-A", "ALT-B", "ALT-C")}
        qualifications["ALT-A"] = qualified("ALT-A", "not_qualified")
        risks = {alt: risk(alt) for alt in qualifications}
        result = recommend_alternatives(data, base_scenario(data), qualifications, risks)
        self.assertEqual(result.alternatives["ALT-A"].status, "not_recommended")

    def test_critical_risk_not_recommended(self):
        data = load_demo()
        qualifications = {alt: qualified(alt) for alt in ("ALT-BASE", "ALT-A", "ALT-B", "ALT-C")}
        risks = {alt: risk(alt) for alt in qualifications}
        risks["ALT-C"] = risk("ALT-C", "critical")
        result = recommend_alternatives(data, base_scenario(data), qualifications, risks)
        self.assertEqual(result.alternatives["ALT-C"].status, "not_recommended")

    def test_conditional_qualification_is_conditional_recommendation(self):
        data = load_demo()
        qualifications = {alt: qualified(alt) for alt in ("ALT-BASE", "ALT-A", "ALT-B", "ALT-C")}
        qualifications["ALT-C"] = qualified("ALT-C", "conditionally_qualified")
        risks = {alt: risk(alt) for alt in qualifications}
        result = recommend_alternatives(data, base_scenario(data), qualifications, risks)
        self.assertEqual(result.alternatives["ALT-C"].status, "conditionally_recommended")
        self.assertTrue(result.alternatives["ALT-C"].validation_required)

    def test_incomplete_risk_data_is_conditional(self):
        data = load_demo()
        qualifications = {alt: qualified(alt) for alt in ("ALT-BASE", "ALT-A", "ALT-B", "ALT-C")}
        risks = {alt: risk(alt) for alt in qualifications}
        risks["ALT-A"] = risk("ALT-A", "low", complete=False)
        result = recommend_alternatives(data, base_scenario(data), qualifications, risks)
        self.assertEqual(result.alternatives["ALT-A"].status, "conditionally_recommended")


if __name__ == "__main__":
    unittest.main()
