import unittest

from src.category_registry import default_registry


class CategoryRegistryTestCase(unittest.TestCase):
    def test_default_registry_contains_all_eight_categories(self):
        registry = default_registry()
        self.assertEqual(
            registry.keys(),
            (
                "closures",
                "corrugated",
                "flexible_packaging",
                "folding_carton",
                "glass",
                "labels",
                "metal",
                "rigid_plastic",
            ),
        )

    def test_each_category_has_objectives_and_change_types(self):
        for category in default_registry().list():
            with self.subTest(category=category.key):
                self.assertTrue(category.objectives)
                self.assertTrue(category.change_types)
                self.assertTrue(category.supports_objective("Cost reduction"))

    def test_unknown_category_is_rejected(self):
        with self.assertRaises(KeyError):
            default_registry().get("unknown")


if __name__ == "__main__":
    unittest.main()
