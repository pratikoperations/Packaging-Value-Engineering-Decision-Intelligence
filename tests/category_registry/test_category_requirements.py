import unittest

from src.category_registry import default_registry


class CategoryRequirementsTestCase(unittest.TestCase):
    def setUp(self):
        self.registry = default_registry()

    def test_all_categories_have_three_requirement_levels(self):
        for category in self.registry.list():
            levels = {field.requirement for field in category.fields}
            self.assertIn("mandatory", levels)
            self.assertIn("recommended", levels)
            self.assertTrue(category.fields)

    def test_all_fields_have_supported_value_types_and_valid_ranges(self):
        allowed = {"number", "integer", "text", "date", "boolean"}
        for category in self.registry.list():
            for field in category.fields:
                self.assertIn(field.value_type, allowed)
                if field.minimum is not None and field.maximum is not None:
                    self.assertLessEqual(field.minimum, field.maximum)

    def test_all_categories_have_documents_tests_blockers_and_analyses(self):
        for category in self.registry.list():
            self.assertTrue(category.documents)
            self.assertTrue(category.tests)
            self.assertTrue(category.readiness_blockers)
            self.assertIn("cost_comparison", category.available_analyses)
            self.assertIn("final_technical_feasibility", category.unavailable_analyses)

    def test_mandatory_specification_documents_exist(self):
        for category in self.registry.list():
            mandatory = {d.document_type for d in category.documents_by_requirement("mandatory")}
            self.assertIn("current_specification", mandatory)
            self.assertIn("proposed_specification", mandatory)
            self.assertIn("supplier_quotation", mandatory)

    def test_critical_fields_or_tests_exist_for_every_category(self):
        for category in self.registry.list():
            self.assertTrue(
                any(field.critical for field in category.fields)
                or any(test.critical for test in category.tests)
            )


if __name__ == "__main__":
    unittest.main()
