from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from src.recommendation import recommend_alternatives
from src.risk_engine import evaluate_risks
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.synthetic_data import SYNTHETIC_DISCLOSURE, build_legacy_dataset, load_governed_package
from src.synthetic_data.domain import SyntheticDataError
from src.synthetic_data.identifiers import validate_identifier
from src.synthetic_data.validator import validate_package
from src.technical_qualification import evaluate_technical_qualification


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "data" / "demo" / "governed_synthetic"


class GovernedSyntheticDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = load_governed_package(PACKAGE_ROOT)

    def test_manifest_is_governed_and_inr_only(self) -> None:
        manifest = self.package["manifest"]
        self.assertEqual("synthetic_demo", manifest["dataset_type"])
        self.assertEqual("INR", manifest["currency_basis"]["currency"])
        self.assertEqual(SYNTHETIC_DISCLOSURE, manifest["synthetic_disclosure"])

    def test_manifest_counts_match_all_collections(self) -> None:
        counts = self.package["manifest"]["record_counts"]
        for key, expected in counts.items():
            self.assertEqual(expected, len(self.package[key]))

    def test_exactly_three_positive_scenarios_exist(self) -> None:
        self.assertEqual(3, len(self.package["scenarios"]))
        self.assertEqual(
            {"SCN-SYN-001", "SCN-SYN-002", "SCN-SYN-003"},
            {item["scenario_id"] for item in self.package["scenarios"]},
        )

    def test_at_least_eight_negative_cases_exist(self) -> None:
        self.assertGreaterEqual(len(self.package["invalid_cases"]), 8)

    def test_identifiers_are_deterministic_and_governed(self) -> None:
        validate_identifier("supplier", "SUP-SYN-001")
        validate_identifier("scenario", "SCN-SYN-003")
        with self.assertRaises(SyntheticDataError):
            validate_identifier("supplier", "REAL-SUPPLIER")

    def test_loading_is_deterministic(self) -> None:
        first = load_governed_package(PACKAGE_ROOT)
        second = load_governed_package(PACKAGE_ROOT)
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

    def test_all_scenarios_adapt_to_existing_engine_contract(self) -> None:
        for item in self.package["scenarios"]:
            with self.subTest(scenario_id=item["scenario_id"]):
                dataset = build_legacy_dataset(self.package, item["scenario_id"])
                ids = {alt["alternative_id"] for alt in dataset["packaging_alternatives"]}
                inputs = ScenarioInputs(
                    annual_volume=dataset["packaging_project"]["annual_volume"],
                    cost_adjustment_percent_by_alternative={value: 0.0 for value in ids},
                    material_adjustment_percent_by_alternative={value: 0.0 for value in ids},
                )
                scenario = evaluate_scenario(dataset, inputs)
                qualifications = evaluate_technical_qualification(dataset)
                risks = evaluate_risks(dataset)
                recommendation = recommend_alternatives(dataset, scenario, qualifications, risks)
                self.assertEqual(ids, set(scenario.alternatives))
                self.assertEqual(ids, set(qualifications))
                self.assertEqual(ids, set(risks))
                self.assertEqual(ids - {"ALT-BASE"}, set(recommendation.alternatives))

    def test_unknown_scenario_fails_closed(self) -> None:
        with self.assertRaises(SyntheticDataError):
            build_legacy_dataset(self.package, "SCN-SYN-999")

    def test_orphan_supplier_reference_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["quotations"][0]["supplier_id"] = "SUP-SYN-999"
        with self.assertRaisesRegex(SyntheticDataError, "Unknown quotation supplier"):
            validate_package(PACKAGE_ROOT, mutated)

    def test_duplicate_identifier_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["quotations"][1]["quotation_id"] = mutated["quotations"][0]["quotation_id"]
        with self.assertRaisesRegex(SyntheticDataError, "Duplicate quotation_id"):
            validate_package(PACKAGE_ROOT, mutated)

    def test_non_inr_currency_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["quotations"][0]["currency"] = "USD"
        with self.assertRaises(SyntheticDataError) as context:
            validate_package(PACKAGE_ROOT, mutated)
        self.assertEqual("UNSUPPORTED_CURRENCY", context.exception.code)

    def test_negative_cost_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["quotations"][0]["unit_price"] = -1
        with self.assertRaises(SyntheticDataError) as context:
            validate_package(PACKAGE_ROOT, mutated)
        self.assertEqual("NEGATIVE_COST", context.exception.code)

    def test_missing_disclosure_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["manifest"]["synthetic_disclosure"] = ""
        with self.assertRaises(SyntheticDataError) as context:
            validate_package(PACKAGE_ROOT, mutated)
        self.assertEqual("MISSING_DISCLOSURE", context.exception.code)

    def test_possible_real_company_name_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["suppliers"][0]["name"] = "Tata"
        with self.assertRaises(SyntheticDataError) as context:
            validate_package(PACKAGE_ROOT, mutated)
        self.assertEqual("REAL_NAME_DETECTED", context.exception.code)

    def test_identifiable_email_fails(self) -> None:
        mutated = copy.deepcopy(self.package)
        mutated["suppliers"][0]["contact"] = "buyer@example.com"
        with self.assertRaises(SyntheticDataError) as context:
            validate_package(PACKAGE_ROOT, mutated)
        self.assertEqual("IDENTIFIABLE_DATA_DETECTED", context.exception.code)


if __name__ == "__main__":
    unittest.main()
