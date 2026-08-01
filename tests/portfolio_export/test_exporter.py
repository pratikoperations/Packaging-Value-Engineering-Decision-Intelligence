from __future__ import annotations

import csv
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from src.portfolio_export import build_portfolio_export, write_portfolio_export


class PortfolioExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = {
            "dataset_type": "synthetic_demo",
            "schema_version": "0.2.0",
            "synthetic_notice": "Synthetic demonstration data only.",
            "packaging_project": {
                "project_id": "PVE-DEMO-001",
                "annual_volume": 1000,
                "status": "active",
            },
            "baseline_specification": {
                "baseline_id": "BASE-001",
                "evidence_id": "EV-001",
            },
            "packaging_alternatives": [
                {
                    "alternative_id": "ALT-BASE",
                    "name": "Baseline",
                    "status": "baseline",
                    "case_weight_g": 100,
                },
                {
                    "alternative_id": "ALT-A",
                    "name": "Alternative A",
                    "status": "proposed",
                    "case_weight_g": 90,
                },
            ],
        }
        common_risk = {
            "overall_level": "low",
            "data_complete": True,
            "reasons": [],
            "validation_required": [],
            "indicators": [],
        }
        self.package = {
            "metadata": {
                "package_schema": "pve_internal_decision_package",
                "package_version": "0.6.0-decision-package",
                "contract_status": "internal_export_not_final_integration_contract",
                "source_repository": "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
                "source_commit": "abc123def456",
                "generated_at": "2026-08-01T12:00:00Z",
                "dataset_type": "synthetic_demo",
                "schema_version": "0.2.0",
                "synthetic_disclosure": "Synthetic demonstration data only.",
            },
            "executive_summary": {
                "decision_status": "recommended",
                "preferred_alternative_id": "ALT-A",
                "preferred_alternative_name": "Alternative A",
                "summary": "Preferred packaging alternative: ALT-A.",
                "selection_basis": ["Higher annual savings."],
                "technical_approval_required": True,
            },
            "project": {
                "project_id": "PVE-DEMO-001",
                "project_name": "Synthetic project",
                "packaging_category": "corrugated_shipping_case",
                "annual_volume": 1000,
                "annual_volume_unit": "cases_per_year",
                "currency": "INR",
            },
            "scenario": {"annual_volume": 1000, "alternative_ids": ["ALT-A", "ALT-BASE"]},
            "baseline": {
                "alternative_id": "ALT-BASE",
                "name": "Baseline",
                "design_status": "baseline",
                "specification": {"length_mm": 1, "width_mm": 1, "height_mm": 1, "board_grade": "BASE"},
                "scenario_assumptions": ["Annual volume set to 1000 cases."],
                "cost_and_material": {
                    "unit_cost": 10,
                    "annual_cost": 10000,
                    "annual_savings_vs_baseline": 0,
                    "case_weight_g": 100,
                    "annual_material_kg": 100,
                    "material_change_percent_vs_baseline": 0,
                },
                "technical_qualification": {
                    "status": "qualified",
                    "reasons": [],
                    "missing_requirement_ids": [],
                    "evidence_ids": ["EV-001"],
                    "validation_required": [],
                },
                "risk": common_risk,
                "recommendation": None,
            },
            "alternatives": [
                {
                    "alternative_id": "ALT-A",
                    "name": "Alternative A",
                    "design_status": "proposed",
                    "specification": {"length_mm": 1, "width_mm": 1, "height_mm": 1, "board_grade": "ALT"},
                    "scenario_assumptions": ["Annual volume set to 1000 cases."],
                    "cost_and_material": {
                        "unit_cost": 9,
                        "annual_cost": 9000,
                        "annual_savings_vs_baseline": 1000,
                        "case_weight_g": 90,
                        "annual_material_kg": 90,
                        "material_change_percent_vs_baseline": -10,
                    },
                    "technical_qualification": {
                        "status": "qualified",
                        "reasons": ["Evidence complete."],
                        "missing_requirement_ids": [],
                        "evidence_ids": ["EV-001"],
                        "validation_required": [],
                    },
                    "risk": common_risk,
                    "recommendation": {
                        "status": "recommended",
                        "rationale": ["Annual savings versus baseline: 1000.00."],
                        "constraints": [],
                        "validation_required": [],
                    },
                }
            ],
            "decision_controls": {
                "read_only": True,
                "autonomous_technical_approval": False,
                "supplier_allocation": False,
                "external_system_integration": False,
                "integration_contract_finalized": False,
                "engineering_validation_required": True,
            },
        }

    def _build(self):
        return build_portfolio_export(
            self.dataset,
            self.package,
            scenario_name="SCENARIO-001",
            cost_adjustments={"ALT-BASE": 0.0, "ALT-A": 0.0},
            material_adjustments={"ALT-BASE": 0.0, "ALT-A": 0.0},
        )

    def test_required_files_are_generated(self):
        files = self._build()
        self.assertEqual(
            set(files),
            {
                "project_summary.csv",
                "scenario_summary.csv",
                "alternative_summary.csv",
                "scenario_results.csv",
                "technical_qualification.csv",
                "risk_indicators.csv",
                "recommendations.csv",
                "assumptions.csv",
                "data_dictionary.csv",
                "export_manifest.json",
            },
        )

    def test_export_is_deterministic(self):
        self.assertEqual(self._build(), self._build())

    def test_authoritative_values_are_serialized_without_recalculation(self):
        files = self._build()
        rows = list(csv.DictReader(io.StringIO(files["scenario_results.csv"].decode("utf-8"))))
        alternative = next(row for row in rows if row["alternative_id"] == "ALT-A")
        self.assertEqual(alternative["unit_cost"], "9")
        self.assertEqual(alternative["annual_cost"], "9000")
        self.assertEqual(alternative["annual_savings_vs_baseline"], "1000")

    def test_manifest_hashes_match_csv_content(self):
        files = self._build()
        manifest = json.loads(files["export_manifest.json"])
        for record in manifest["files"]:
            content = files[record["file_name"]]
            self.assertEqual(record["sha256"], hashlib.sha256(content).hexdigest())

    def test_non_synthetic_dataset_is_rejected(self):
        self.package["metadata"]["dataset_type"] = "production"
        with self.assertRaisesRegex(ValueError, "restricted to synthetic_demo"):
            self._build()

    def test_write_portfolio_export_creates_all_files(self):
        files = self._build()
        with tempfile.TemporaryDirectory() as directory:
            written = write_portfolio_export(Path(directory), files)
            self.assertEqual(set(written), set(files))
            self.assertTrue(all(path.exists() for path in written.values()))


if __name__ == "__main__":
    unittest.main()
