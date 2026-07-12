import json
import unittest
from pathlib import Path

from src.material_engine import analyze_materials

ROOT = Path(__file__).resolve().parents[2]


def load_demo():
    return json.loads((ROOT / "data/demo/corrugated_shipping_cases.json").read_text(encoding="utf-8"))


class TestMaterialEngine(unittest.TestCase):
    def test_baseline_material_metrics(self):
        result = analyze_materials(load_demo())["ALT-BASE"]
        self.assertEqual(result.component_weight_g, 980.0)
        self.assertEqual(result.component_variance_g, 0.0)
        self.assertEqual(result.annual_material_kg, 1176000.0)
        self.assertEqual(result.material_change_percent_vs_baseline, 0.0)

    def test_alternative_material_reduction(self):
        result = analyze_materials(load_demo())["ALT-B"]
        self.assertEqual(result.material_change_g_vs_baseline, -290.0)
        self.assertAlmostEqual(result.material_change_percent_vs_baseline, -29.591837, places=6)

    def test_missing_component_rejected(self):
        data = load_demo()
        data["material_components"] = [r for r in data["material_components"] if r["alternative_id"] != "ALT-C"]
        with self.assertRaisesRegex(ValueError, "No positive material component weight"):
            analyze_materials(data)

    def test_duplicate_baseline_rejected(self):
        data = load_demo()
        data["packaging_alternatives"][1]["status"] = "baseline"
        with self.assertRaisesRegex(ValueError, "Exactly one baseline"):
            analyze_materials(data)


if __name__ == "__main__":
    unittest.main()
