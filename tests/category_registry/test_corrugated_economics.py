from __future__ import annotations

import unittest

from src.category_registry import analyze_corrugated_economics
from src.uploads.normalizer import normalize_user_dataset


class CorrugatedEconomicsTestCase(unittest.TestCase):
    def setUp(self):
        self.currency = "INR"
        self.should_cost = []
        for context, values in {
            "baseline": {"board_or_paper": 12, "conversion": 3, "printing": 1, "freight": 2},
            "proposed": {"board_or_paper": 10, "conversion": 3, "printing": 1, "freight": 1.5},
        }.items():
            for component, value in values.items():
                self.should_cost.append({
                    "record_id": f"{context}-{component}", "context": context,
                    "component": component, "value_per_case": value, "currency": "INR",
                    "source_classification": "manually_entered_fact", "source_reference": "COST-1",
                })
        self.failure = [
            {"record_id": "fail-b", "context": "baseline", "annual_cases": 100000,
             "damage_rate_percent": 1, "loss_per_damaged_case": 50, "currency": "INR",
             "source_classification": "uploaded_fact", "source_reference": "HISTORY-1", "source_role": "historical"},
            {"record_id": "fail-p", "context": "proposed", "annual_cases": 100000,
             "damage_rate_percent": 1.5, "loss_per_damaged_case": 50, "currency": "INR",
             "source_classification": "assumption", "source_reference": "ASSUMPTION-1", "source_role": "scenario"},
        ]
        self.inventory = [
            {"record_id": "inv-b", "context": "baseline", "annual_cases": 100000,
             "inventory_days": 20, "unit_inventory_value": 18, "transition_stock_units": 0,
             "obsolete_stock_units": 0, "write_off_percent": 100, "currency": "INR",
             "source_classification": "uploaded_fact", "source_reference": "ERP-1"},
            {"record_id": "inv-p", "context": "proposed", "annual_cases": 100000,
             "inventory_days": 30, "unit_inventory_value": 15.5, "transition_stock_units": 1000,
             "obsolete_stock_units": 500, "write_off_percent": 100, "currency": "INR",
             "source_classification": "manually_entered_fact", "source_reference": "PLAN-1"},
        ]
        self.one_time = [
            {"record_id": "tooling", "component": "tooling", "value": 50000, "currency": "INR",
             "source_classification": "supplier_declared", "source_reference": "QUOTE-1"},
            {"record_id": "trial", "component": "trials", "value": 25000, "currency": "INR",
             "source_classification": "manually_entered_fact", "source_reference": "TRIAL-PLAN"},
        ]

    def assess(self, blockers=()):
        return analyze_corrugated_economics(
            currency=self.currency, annual_cases=100000,
            should_cost_inputs=self.should_cost, failure_cost_inputs=self.failure,
            inventory_inputs=self.inventory, one_time_costs=self.one_time,
            technical_blockers=blockers,
        )

    def test_should_cost_and_gross_benefit(self):
        result = self.assess()
        self.assertEqual(result.outputs["should_cost"].value, 15.5)
        self.assertEqual(result.outputs["gross_annual_benefit"].value, 350000)

    def test_failure_cost_and_risk_adjusted_benefit(self):
        result = self.assess()
        self.assertEqual(result.outputs["incremental_failure_cost"].value, 25000)
        self.assertEqual(result.outputs["risk_adjusted_annual_benefit"].value, 325000)
        self.assertIn("ASSUMPTION-1", result.outputs["risk_adjusted_annual_benefit"].assumptions)

    def test_inventory_working_capital_and_write_off(self):
        result = self.assess()
        self.assertAlmostEqual(result.outputs["incremental_working_capital"].value, 44109.58904109589)
        self.assertEqual(result.outputs["obsolete_stock_write_off"].value, 7750)

    def test_first_year_benefit_and_payback(self):
        result = self.assess()
        expected = 325000 - 75000 - 44109.58904109589 - 7750
        self.assertAlmostEqual(result.outputs["first_year_net_benefit"].value, expected)
        self.assertAlmostEqual(result.outputs["payback_months"].value, 75000 / 325000 * 12)

    def test_duplicate_one_time_cost_is_rejected_without_double_counting(self):
        duplicate = self.one_time + [dict(self.one_time[0], record_id="tooling-2")]
        result = analyze_corrugated_economics(
            currency="INR", annual_cases=100000, should_cost_inputs=self.should_cost,
            failure_cost_inputs=self.failure, inventory_inputs=self.inventory,
            one_time_costs=duplicate,
        )
        self.assertEqual(result.outputs["first_year_net_benefit"].status, "unavailable")
        self.assertIn("Duplicate one-time component", result.outputs["first_year_net_benefit"].limitations[-1])

    def test_currency_mismatch_is_unavailable(self):
        bad = [dict(self.should_cost[0], currency="USD")] + self.should_cost[1:]
        result = analyze_corrugated_economics(
            currency="INR", annual_cases=100000, should_cost_inputs=bad,
            failure_cost_inputs=self.failure, inventory_inputs=self.inventory,
            one_time_costs=self.one_time,
        )
        self.assertEqual(result.outputs["should_cost"].status, "unavailable")

    def test_missing_inputs_return_unavailable_outputs(self):
        result = analyze_corrugated_economics(
            currency="INR", annual_cases=100000, should_cost_inputs=[],
            failure_cost_inputs=[], inventory_inputs=[], one_time_costs=[],
        )
        self.assertEqual(result.outputs["gross_annual_benefit"].status, "unavailable")
        self.assertEqual(result.outputs["risk_adjusted_annual_benefit"].status, "unavailable")
        self.assertEqual(result.outputs["first_year_net_benefit"].status, "unavailable")

    def test_technical_blockers_override_economic_attractiveness(self):
        result = self.assess(("BCT below governed requirement",))
        self.assertGreater(result.outputs["risk_adjusted_annual_benefit"].value, 0)
        self.assertEqual(result.outputs["risk_adjusted_annual_benefit"].status, "blocked")
        self.assertIn("BCT below governed requirement", result.outputs["risk_adjusted_annual_benefit"].blocking_conditions)

    def test_source_traceability_is_preserved(self):
        result = self.assess()
        sources = {(row["source_classification"], row["source_reference"]) for row in result.source_traceability}
        self.assertIn(("uploaded_fact", "HISTORY-1"), sources)
        self.assertIn(("assumption", "ASSUMPTION-1"), sources)
        self.assertIn(("supplier_declared", "QUOTE-1"), sources)

    def test_invalid_source_classification_is_rejected(self):
        invalid = [dict(self.failure[0], source_classification="historical")] + self.failure[1:]
        with self.assertRaisesRegex(ValueError, "source_classification is invalid"):
            analyze_corrugated_economics(
                currency="INR", annual_cases=100000, should_cost_inputs=self.should_cost,
                failure_cost_inputs=invalid, inventory_inputs=self.inventory,
                one_time_costs=self.one_time,
            )

    def test_normalizer_preserves_build6_collections(self):
        raw = {
            "should_cost_inputs": [{"value_per_case": "12.5", "source_reference": "COST-1"}],
            "failure_cost_inputs": [{"damage_rate_percent": "1.2", "loss_per_damaged_case": "50"}],
            "inventory_inputs": [{"inventory_days": "30", "moq_units": "5000"}],
            "one_time_costs": [{"value": "25000"}],
        }
        project = {"project_id": "P1", "project_name": "P", "category": "corrugated", "annual_volume": 1, "currency": "INR"}
        normalized = normalize_user_dataset(raw, project)
        self.assertEqual(normalized["should_cost_inputs"][0]["value_per_case"], 12.5)
        self.assertEqual(normalized["failure_cost_inputs"][0]["damage_rate_percent"], 1.2)
        self.assertEqual(normalized["inventory_inputs"][0]["moq_units"], 5000)
        self.assertEqual(normalized["one_time_costs"][0]["value"], 25000)


if __name__ == "__main__":
    unittest.main()
