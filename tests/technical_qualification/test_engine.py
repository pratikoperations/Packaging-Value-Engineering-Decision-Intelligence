import copy
import json
import unittest
from pathlib import Path

from src.technical_qualification import evaluate_technical_qualification

ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


class TestTechnicalQualificationEngine(unittest.TestCase):
    def test_demo_reports_insufficient_data(self):
        outcomes = evaluate_technical_qualification(load_demo())
        self.assertEqual(outcomes["ALT-A"].status, "insufficient_data")
        self.assertIn("REQ-STACK", outcomes["ALT-A"].missing_requirement_ids)
        self.assertTrue(outcomes["ALT-A"].validation_required)

    def test_all_qualified_with_evidence(self):
        data = load_demo()
        data["technical_qualification_results"] = []
        for alt in data["packaging_alternatives"]:
            for req in data["technical_requirements"]:
                data["technical_qualification_results"].append({
                    "qualification_id": f"Q-{alt['alternative_id']}-{req['requirement_id']}",
                    "alternative_id": alt["alternative_id"],
                    "requirement_id": req["requirement_id"],
                    "status": "qualified",
                    "evidence_id": "EV-006",
                })
        self.assertEqual(evaluate_technical_qualification(data)["ALT-B"].status, "qualified")

    def test_conditional_status_is_preserved(self):
        data = load_demo()
        data["technical_qualification_results"] = []
        for alt in data["packaging_alternatives"]:
            for req in data["technical_requirements"]:
                status = "conditionally_qualified" if alt["alternative_id"] == "ALT-C" and req["requirement_id"] == "REQ-BCT" else "qualified"
                data["technical_qualification_results"].append({
                    "qualification_id": f"Q-{alt['alternative_id']}-{req['requirement_id']}",
                    "alternative_id": alt["alternative_id"],
                    "requirement_id": req["requirement_id"],
                    "status": status,
                    "evidence_id": "EV-006",
                })
        outcome = evaluate_technical_qualification(data)["ALT-C"]
        self.assertEqual(outcome.status, "conditionally_qualified")
        self.assertTrue(any("Close conditions" in item for item in outcome.validation_required))

    def test_not_qualified_overrides_other_statuses(self):
        data = load_demo()
        data["technical_qualification_results"] = [
            {"qualification_id":"Q1","alternative_id":"ALT-A","requirement_id":"REQ-BCT","status":"not_qualified","evidence_id":"EV-006"},
            {"qualification_id":"Q2","alternative_id":"ALT-A","requirement_id":"REQ-STACK","status":"qualified","evidence_id":"EV-006"},
        ]
        self.assertEqual(evaluate_technical_qualification(data)["ALT-A"].status, "not_qualified")

    def test_missing_evidence_for_qualified_becomes_insufficient(self):
        data = load_demo()
        data["technical_qualification_results"] = [
            {"qualification_id":"Q1","alternative_id":"ALT-A","requirement_id":"REQ-BCT","status":"qualified","evidence_id":None},
            {"qualification_id":"Q2","alternative_id":"ALT-A","requirement_id":"REQ-STACK","status":"qualified","evidence_id":"EV-006"},
        ]
        outcome = evaluate_technical_qualification(data)["ALT-A"]
        self.assertEqual(outcome.status, "insufficient_data")
        self.assertTrue(any("Provide evidence" in item for item in outcome.validation_required))

    def test_duplicate_requirement_result_rejected(self):
        data = load_demo()
        duplicate = copy.deepcopy(data["technical_qualification_results"][0])
        duplicate["qualification_id"] = "DUP"
        data["technical_qualification_results"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "Duplicate technical qualification result"):
            evaluate_technical_qualification(data)


if __name__ == "__main__":
    unittest.main()
