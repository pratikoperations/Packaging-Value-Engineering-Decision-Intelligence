from __future__ import annotations

import json
import unittest

from src.ui.calculation_evidence_ui import render_calculation_evidence_page


class _Expander:
    def __enter__(self): return self
    def __exit__(self, *args): return False


class FakeStreamlit:
    def __init__(self, *, click: bool = False):
        self.click = click
        self.calls = []
    def __getattr__(self, name):
        def call(*args, **kwargs):
            self.calls.append((name, args, kwargs))
            if name == "selectbox": return args[1][0]
            if name == "button": return self.click
            if name == "expander": return _Expander()
            return None
        return call


class FakeContext:
    def list_scenarios(self, project_id):
        return ({
            "scenario_id": "scenario-1",
            "project_id": project_id,
            "scenario_name": "Scenario",
            "created_at": "2026-08-01",
            "content_hash": "hash",
            "assumptions_json": json.dumps({
                "annual_volume": 1000,
                "cost_adjustment_percent_by_alternative": {"ALT-A": 0.0},
                "material_adjustment_percent_by_alternative": {"ALT-A": 0.0},
            }),
            "results_json": json.dumps({"alternatives": {"ALT-A": {
                "unit_cost": 48.8,
                "annual_cost": 48800.0,
                "annual_savings_vs_baseline": 3600.0,
                "case_weight_g": 880.0,
                "annual_material_kg": 880.0,
                "material_change_percent_vs_baseline": -10.204081632653061,
                "technical_validation_required": [],
                "risk_validation_required": [],
            }}}),
        },)
    def get_scenario(self, project_id, scenario_id):
        return self.list_scenarios(project_id)[0], False


class CalculationEvidenceUiTests(unittest.TestCase):
    def project(self):
        return {"project_id": "project-1", "project_code": "P1", "project_name": "Project"}

    def test_empty_state_renders(self):
        st = FakeStreamlit()
        render_calculation_evidence_page(st, projects=(), context=FakeContext())
        self.assertIn("info", [item[0] for item in st.calls])

    def test_success_state_and_export_render(self):
        st = FakeStreamlit(click=True)
        render_calculation_evidence_page(st, projects=(self.project(),), context=FakeContext())
        names = [item[0] for item in st.calls]
        self.assertIn("metric", names)
        self.assertIn("download_button", names)

    def test_page_has_no_editable_formula_or_prompt_controls(self):
        st = FakeStreamlit(click=False)
        render_calculation_evidence_page(st, projects=(self.project(),), context=FakeContext())
        names = set(item[0] for item in st.calls)
        self.assertTrue({"text_input", "text_area", "chat_input", "number_input"}.isdisjoint(names))


if __name__ == "__main__":
    unittest.main()
