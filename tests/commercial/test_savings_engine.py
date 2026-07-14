import unittest

from src.commercial import calculate_commercial_analysis


class CommercialAnalysisTestCase(unittest.TestCase):
    def test_complete_commercial_analysis(self):
        result = calculate_commercial_analysis(
            current_unit_cost=12.0,
            proposed_unit_cost=10.0,
            annual_volume=120000,
            realization_percent=80,
            testing_cost=10000,
            tooling_cost=20000,
            implementation_cost=5000,
            qualification_cost=5000,
            current_material_weight=500,
            proposed_material_weight=450,
            assumptions=("Annual volume remains stable.",),
        )
        self.assertEqual(result.saving_per_unit, 2.0)
        self.assertEqual(result.annual_gross_saving, 240000.0)
        self.assertEqual(result.expected_realized_saving, 192000.0)
        self.assertEqual(result.first_year_net_benefit, 152000.0)
        self.assertAlmostEqual(result.payback_months, 2.5)
        self.assertEqual(result.material_reduction_per_unit, 50.0)
        self.assertEqual(result.annual_material_reduction, 6000000.0)
        self.assertAlmostEqual(result.percentage_cost_reduction, 16.6666666667)
        self.assertEqual(result.percentage_material_reduction, 10.0)
        self.assertTrue(result.labels)
        self.assertEqual(result.assumptions, ("Annual volume remains stable.",))

    def test_no_positive_monthly_saving_has_no_payback(self):
        result = calculate_commercial_analysis(
            current_unit_cost=10,
            proposed_unit_cost=10,
            annual_volume=1000,
            implementation_cost=500,
        )
        self.assertIsNone(result.payback_months)

    def test_material_weights_must_be_supplied_together(self):
        with self.assertRaises(ValueError):
            calculate_commercial_analysis(
                current_unit_cost=10,
                proposed_unit_cost=9,
                annual_volume=1000,
                current_material_weight=100,
            )

    def test_realization_percentage_is_validated(self):
        with self.assertRaises(ValueError):
            calculate_commercial_analysis(
                current_unit_cost=10,
                proposed_unit_cost=9,
                annual_volume=1000,
                realization_percent=101,
            )

    def test_negative_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            calculate_commercial_analysis(
                current_unit_cost=-1,
                proposed_unit_cost=1,
                annual_volume=1000,
            )


if __name__ == "__main__":
    unittest.main()
