import json
import unittest

from src.reports import build_executive_summary, render_summary_json, render_summary_markdown
from src.validation_readiness.models import ComponentScore, OutputStatus, ReadinessAssessment


class ExecutiveSummaryTestCase(unittest.TestCase):
    def setUp(self):
        self.project = {
            "project_id": "project-1", "project_code": "PVE-1", "project_name": "Demo",
            "category": "corrugated", "objective": "Cost reduction", "change_type": "GSM reduction",
            "annual_volume": 1000, "current_unit_cost": 10, "proposed_unit_cost": 9,
        }
        self.assessment = ReadinessAssessment(
            "project-1", "dataset-1", "corrugated", 70.0, "Ready for Laboratory Testing",
            (ComponentScore("project_metadata", "Project metadata", 10, 7, 7),),
            ("Missing mandatory laboratory test: BCT",),
            (OutputStatus("document_completeness", True), OutputStatus("technical_feasibility", False, ("Engineering validation required.",))),
            {"manually_entered_fact": 3, "assumption": 1},
            "Engineering validation and human approval remain mandatory; autonomous approval is prohibited.",
        )

    def test_summary_contains_explicit_unavailable_reasons(self):
        summary = build_executive_summary(project=self.project, canonical_data={"intake_values": []}, assessment=self.assessment)
        unavailable = {item["output"]: item["reasons"] for item in summary["unavailable_outputs"]}
        self.assertIn("technical_feasibility", unavailable)
        self.assertTrue(unavailable["technical_feasibility"])

    def test_commercial_outputs_are_estimates_when_inputs_exist(self):
        summary = build_executive_summary(project=self.project, canonical_data={"intake_values": []}, assessment=self.assessment)
        self.assertEqual(summary["commercial_opportunity"]["annual_gross_saving"], 1000)
        self.assertIn("Estimate", summary["commercial_opportunity"]["labels"]["annual_gross_saving"])

    def test_json_and_markdown_retain_approval_limitation(self):
        summary = build_executive_summary(project=self.project, canonical_data={"intake_values": []}, assessment=self.assessment)
        payload = json.loads(render_summary_json(summary))
        markdown = render_summary_markdown(summary)
        self.assertIn("human approval", payload["approval_limitation"])
        self.assertIn("Approval Limitation", markdown)
        self.assertIn("autonomous approval is prohibited", markdown)

    def test_missing_commercial_input_has_reason(self):
        project = dict(self.project, proposed_unit_cost=None)
        summary = build_executive_summary(project=project, canonical_data={"intake_values": []}, assessment=self.assessment)
        reasons = [reason for item in summary["unavailable_outputs"] if item["output"] == "commercial_analysis" for reason in item["reasons"]]
        self.assertTrue(any("proposed_unit_cost" in reason for reason in reasons))


if __name__ == "__main__":
    unittest.main()
