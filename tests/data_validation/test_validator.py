import copy
import json
import unittest
from pathlib import Path

from src.data_models import validate_dataset


ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


class TestCanonicalDataValidation(unittest.TestCase):
    def test_valid_complete_dataset(self):
        result = validate_dataset(load_demo())
        self.assertTrue(result.is_valid, result.issues)
        self.assertTrue(result.insufficient_data_eligible)

    def test_missing_mandatory_field(self):
        data = load_demo()
        del data["packaging_project"]["project_id"]
        result = validate_dataset(data)
        self.assertIn("missing_required", {issue.code for issue in result.issues})

    def test_negative_value(self):
        data = load_demo()
        data["packaging_alternatives"][0]["length_mm"] = -1
        result = validate_dataset(data)
        self.assertIn("out_of_range", {issue.code for issue in result.issues})

    def test_duplicate_id(self):
        data = load_demo()
        data["packaging_alternatives"].append(copy.deepcopy(data["packaging_alternatives"][0]))
        result = validate_dataset(data)
        self.assertIn("duplicate_id", {issue.code for issue in result.issues})

    def test_unsupported_unit(self):
        data = load_demo()
        data["packaging_project"]["annual_volume_unit"] = "cartons_per_month"
        result = validate_dataset(data)
        self.assertIn("unsupported_unit", {issue.code for issue in result.issues})

    def test_invalid_enum_value(self):
        data = load_demo()
        data["packaging_alternatives"][1]["status"] = "approved"
        result = validate_dataset(data)
        self.assertIn("invalid_enum", {issue.code for issue in result.issues})

    def test_missing_evidence(self):
        data = load_demo()
        data["cost_inputs"][0]["evidence_id"] = "EV-MISSING"
        result = validate_dataset(data)
        self.assertIn("missing_evidence", {issue.code for issue in result.issues})

    def test_invalid_percentage(self):
        data = load_demo()
        data["risk_records"][0]["probability_percent"] = 140
        result = validate_dataset(data)
        self.assertIn("invalid_percentage", {issue.code for issue in result.issues})

    def test_partial_dataset_is_insufficient_data_eligible(self):
        data = load_demo()
        del data["technical_qualification_results"]
        result = validate_dataset(data)
        self.assertTrue(result.insufficient_data_eligible)

    def test_currency_consistency(self):
        data = load_demo()
        data["cost_inputs"][0]["currency"] = "USD"
        result = validate_dataset(data)
        self.assertIn("currency_mismatch", {issue.code for issue in result.issues})


if __name__ == "__main__":
    unittest.main()
