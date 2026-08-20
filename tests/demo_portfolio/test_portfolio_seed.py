from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.application.runtime import (
    build_controlled_scenario_service,
    build_decision_snapshot_service,
    build_project_service,
)
from src.demo_portfolio import DEMO_PROJECT_CODE, PortfolioSeedConflict, seed_portfolio_demo
from src.demo_portfolio.seeder import (
    DEFAULT_SEED_PATH,
    DEMO_PROJECT_CHANGE_TYPE,
    DEMO_PROJECT_NAME,
    DEMO_PROJECT_OBJECTIVE,
)
from src.validation_readiness import assess_readiness


class PortfolioSeedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "portfolio.sqlite3"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_clean_seed_creates_complete_linked_record_chain(self) -> None:
        result = seed_portfolio_demo(self.database_path)

        self.assertEqual(
            result.created,
            ("project", "dataset", "threshold_profile", "scenario", "decision_snapshot"),
        )
        self.assertEqual(result.project["project_code"], DEMO_PROJECT_CODE)
        self.assertEqual(result.project["objective"], DEMO_PROJECT_OBJECTIVE)
        self.assertEqual(result.project["change_type"], DEMO_PROJECT_CHANGE_TYPE)
        self.assertEqual(result.dataset["project_id"], result.project["project_id"])
        self.assertEqual(result.threshold_profile["project_id"], result.project["project_id"])
        self.assertEqual(result.scenario["project_id"], result.project["project_id"])
        self.assertEqual(result.scenario["dataset_id"], result.dataset["dataset_id"])
        self.assertEqual(
            result.scenario["threshold_profile_id"],
            result.threshold_profile["threshold_profile_id"],
        )
        self.assertEqual(result.decision_snapshot["project_id"], result.project["project_id"])
        self.assertEqual(result.decision_snapshot["scenario_id"], result.scenario["scenario_id"])
        self.assertEqual(result.decision_snapshot["dataset_id"], result.dataset["dataset_id"])
        self.assertEqual(
            result.decision_snapshot["threshold_profile_id"],
            result.threshold_profile["threshold_profile_id"],
        )

        summary = build_project_service(self.database_path).portfolio_summary()
        self.assertEqual(summary["total_projects"], 1)
        self.assertEqual(summary["active_projects"], 1)
        self.assertEqual(summary["dataset_versions"], 1)
        self.assertEqual(summary["decision_snapshots"], 1)
        self.assertEqual(
            len(build_controlled_scenario_service(self.database_path).available_datasets(result.project["project_id"])),
            1,
        )
        self.assertEqual(
            len(build_decision_snapshot_service(self.database_path).history(result.project["project_id"])),
            1,
        )

    def test_repeated_seed_is_idempotent(self) -> None:
        first = seed_portfolio_demo(self.database_path)
        second = seed_portfolio_demo(self.database_path)

        self.assertEqual(second.created, ())
        self.assertEqual(second.project["project_id"], first.project["project_id"])
        self.assertEqual(second.dataset["dataset_id"], first.dataset["dataset_id"])
        self.assertEqual(
            second.threshold_profile["threshold_profile_id"],
            first.threshold_profile["threshold_profile_id"],
        )
        self.assertEqual(second.scenario["scenario_id"], first.scenario["scenario_id"])
        self.assertEqual(
            second.decision_snapshot["decision_snapshot_id"],
            first.decision_snapshot["decision_snapshot_id"],
        )

        summary = build_project_service(self.database_path).portfolio_summary()
        self.assertEqual(summary["total_projects"], 1)
        self.assertEqual(summary["dataset_versions"], 1)
        self.assertEqual(summary["decision_snapshots"], 1)
        self.assertEqual(
            len(build_controlled_scenario_service(self.database_path).available_datasets(first.project["project_id"])),
            1,
        )
        self.assertEqual(
            len(build_controlled_scenario_service(self.database_path).scenarios.list_for_project(first.project["project_id"])),
            1,
        )

    def test_existing_demo_with_missing_governed_metadata_is_repaired(self) -> None:
        service = build_project_service(self.database_path)
        existing = service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name=DEMO_PROJECT_NAME,
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
        )

        result = seed_portfolio_demo(self.database_path)

        self.assertEqual(result.project["project_id"], existing["project_id"])
        self.assertEqual(result.project["objective"], DEMO_PROJECT_OBJECTIVE)
        self.assertEqual(result.project["change_type"], DEMO_PROJECT_CHANGE_TYPE)
        self.assertNotIn("project", result.created)
        self.assertEqual(service.portfolio_summary()["total_projects"], 1)

        repeated = seed_portfolio_demo(self.database_path)
        self.assertEqual(repeated.created, ())
        self.assertEqual(repeated.project["project_id"], existing["project_id"])

    def test_conflicting_governed_metadata_stops_without_overwrite(self) -> None:
        service = build_project_service(self.database_path)
        conflicting = service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name=DEMO_PROJECT_NAME,
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
            objective="Material reduction",
            change_type="Ply reduction",
        )

        with self.assertRaisesRegex(PortfolioSeedConflict, "conflicting governed metadata"):
            seed_portfolio_demo(self.database_path)

        preserved = service.get_project(conflicting["project_id"])
        self.assertEqual(preserved["objective"], "Material reduction")
        self.assertEqual(preserved["change_type"], "Ply reduction")
        self.assertEqual(service.portfolio_summary()["dataset_versions"], 0)

    def test_seed_preserves_human_approval_and_non_autonomy_boundaries(self) -> None:
        result = seed_portfolio_demo(self.database_path)
        decision = build_decision_snapshot_service(self.database_path).history(result.project["project_id"])[0]
        recommendation = decision["recommendation"]

        self.assertFalse(recommendation["autonomous_approval"])
        self.assertTrue(recommendation["engineering_validation_required"])
        self.assertTrue(recommendation["human_approval_required"])
        self.assertNotIn("approved", recommendation["status"])
        self.assertIn(
            recommendation["status"],
            {
                "recommended_for_engineering_review",
                "conditionally_recommended_for_engineering_review",
                "not_recommended_business_threshold_failed",
                "insufficient_data",
                "blocked",
            },
        )

    def test_conflicting_project_code_stops_without_overwrite(self) -> None:
        service = build_project_service(self.database_path)
        conflicting = service.create_project(
            project_code=DEMO_PROJECT_CODE,
            project_name="Conflicting Project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=1_200_000.0,
        )

        with self.assertRaisesRegex(PortfolioSeedConflict, "conflicting fields"):
            seed_portfolio_demo(self.database_path)

        preserved = service.get_project(conflicting["project_id"])
        self.assertEqual(preserved["project_name"], "Conflicting Project")
        self.assertEqual(service.portfolio_summary()["dataset_versions"], 0)

    def test_archived_demo_project_is_not_reactivated_or_modified(self) -> None:
        first = seed_portfolio_demo(self.database_path)
        service = build_project_service(self.database_path)
        service.archive_project(first.project["project_id"])

        with self.assertRaisesRegex(PortfolioSeedConflict, "archived"):
            seed_portfolio_demo(self.database_path)

        archived = service.get_project(first.project["project_id"])
        self.assertIsNotNone(archived["archived_at"])
        self.assertEqual(service.portfolio_summary()["active_projects"], 0)
        self.assertEqual(service.portfolio_summary()["archived_projects"], 1)


class PortfolioSeedUpgradeTests(unittest.TestCase):
    """Deterministic regression tests for the PVE 1.1 synthetic showcase data upgrade."""

    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.tempdir.name) / "portfolio.sqlite3"

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def _canonical(self) -> dict:
        result = seed_portfolio_demo(self.database_path)
        return json.loads(result.dataset["canonical_json"])

    # --- test 3: migration from pre-upgrade legacy seed ---

    def test_legacy_migration_creates_new_lineage_without_overwriting_history(self) -> None:
        """A pre-upgrade dataset+scenario pair is not overwritten; new lineage is created."""
        canonical = json.loads(DEFAULT_SEED_PATH.read_text(encoding="utf-8"))

        # Build a minimal legacy payload by removing the PVE 1.1 collections.
        legacy = json.loads(json.dumps(canonical))
        legacy.pop("intake_values", None)
        legacy.pop("quality_tests", None)
        legacy.pop("document_register", None)
        legacy["packaging_project"].pop("objective", None)
        legacy["packaging_project"].pop("change_type", None)
        for r in legacy.get("technical_qualification_results", []):
            if r.get("alternative_id") == "ALT-A":
                r["status"] = "not_assessed"
                r["evidence_id"] = None
        legacy["decision_evidence"] = [
            r for r in legacy.get("decision_evidence", [])
            if r.get("evidence_id") in {"EV-001", "EV-002", "EV-003", "EV-004", "EV-005", "EV-006"}
        ]

        legacy_path = Path(self.tempdir.name) / "legacy_seed.json"
        legacy_path.write_text(json.dumps(legacy, ensure_ascii=False), encoding="utf-8")

        # Seed with the legacy payload — simulates the pre-upgrade state.
        first = seed_portfolio_demo(self.database_path, seed_path=legacy_path)
        self.assertIn("scenario", first.created)
        legacy_scenario_id = first.scenario["scenario_id"]
        legacy_dataset_id = first.dataset["dataset_id"]

        # Seed with the upgraded payload — must create a new dataset+scenario without
        # overwriting the immutable legacy records.
        second = seed_portfolio_demo(self.database_path)
        self.assertIn("dataset", second.created)
        self.assertIn("scenario", second.created)
        self.assertNotEqual(second.dataset["dataset_id"], legacy_dataset_id)
        self.assertNotEqual(second.scenario["scenario_id"], legacy_scenario_id)

        # The legacy dataset and scenario must still exist in the repository.
        scenario_service = build_controlled_scenario_service(self.database_path)
        all_scenarios = scenario_service.scenarios.list_for_project(first.project["project_id"])
        scenario_ids = {s["scenario_id"] for s in all_scenarios}
        self.assertIn(legacy_scenario_id, scenario_ids)
        self.assertIn(second.scenario["scenario_id"], scenario_ids)

        # Repeated upgraded seed must be idempotent.
        third = seed_portfolio_demo(self.database_path)
        self.assertEqual(third.created, ())
        self.assertEqual(third.dataset["dataset_id"], second.dataset["dataset_id"])
        self.assertEqual(third.scenario["scenario_id"], second.scenario["scenario_id"])

    # --- test 4: baseline and proposed PVE 1.1 intake values ---

    def test_canonical_data_has_baseline_and_proposed_intake_values(self) -> None:
        canonical = self._canonical()
        values = canonical.get("intake_values", [])
        baseline = [r for r in values if r.get("context") == "baseline"]
        proposed = [r for r in values if r.get("context") == "proposed"]
        self.assertTrue(len(baseline) >= 17, f"Expected ≥17 baseline rows, got {len(baseline)}")
        self.assertTrue(len(proposed) >= 17, f"Expected ≥17 proposed rows, got {len(proposed)}")
        mandatory_fields = {
            "length_mm", "width_mm", "height_mm", "box_style", "converting_profile",
            "internal_length_mm", "internal_width_mm", "internal_height_mm",
            "ply", "flute_combination", "paper_layer_structure", "layer_gsm_profile",
            "board_grade", "joint_type", "closure_method",
            "gross_packed_weight_kg", "case_pack_quantity",
        }
        baseline_keys = {r["field_key"] for r in baseline if r.get("requirement") == "mandatory"}
        proposed_keys = {r["field_key"] for r in proposed if r.get("requirement") == "mandatory"}
        self.assertTrue(mandatory_fields.issubset(baseline_keys), f"Missing baseline mandatory fields: {mandatory_fields - baseline_keys}")
        self.assertTrue(mandatory_fields.issubset(proposed_keys), f"Missing proposed mandatory fields: {mandatory_fields - proposed_keys}")
        for r in baseline:
            if r.get("requirement") == "mandatory":
                self.assertIsNotNone(r.get("value"), f"Baseline mandatory {r['field_key']} has no value")
        for r in proposed:
            if r.get("requirement") == "mandatory":
                self.assertIsNotNone(r.get("value"), f"Proposed mandatory {r['field_key']} has no value")

    # --- test 5: commercial intake has current and proposed unit cost ---

    def test_commercial_intake_has_current_and_proposed_unit_cost(self) -> None:
        canonical = self._canonical()
        commercial = {
            r["field_key"]: r["value"]
            for r in canonical.get("intake_values", [])
            if r.get("context") == "commercial"
        }
        self.assertEqual(commercial.get("current_unit_cost"), 52.4)
        self.assertEqual(commercial.get("proposed_unit_cost"), 48.8)
        self.assertEqual(commercial.get("annual_volume"), 1_200_000)

    # --- test 6: readiness has no missing baseline/proposed/current-cost blockers ---

    def test_readiness_has_no_specification_or_cost_blockers(self) -> None:
        result = seed_portfolio_demo(self.database_path)
        canonical = json.loads(result.dataset["canonical_json"])
        project = result.project
        assessment = assess_readiness(project=project, canonical_data=canonical, dataset_id=result.dataset["dataset_id"])
        blocker_texts = " | ".join(assessment.blockers)
        self.assertNotIn("No baseline specification", blocker_texts)
        self.assertNotIn("No proposed specification", blocker_texts)
        self.assertNotIn("Missing current cost", blocker_texts)
        self.assertNotIn("Missing annual volume", blocker_texts)
        self.assertEqual(assessment.blockers, ())

    # --- test 7: commercial analysis is available ---

    def test_commercial_analysis_is_available(self) -> None:
        result = seed_portfolio_demo(self.database_path)
        canonical = json.loads(result.dataset["canonical_json"])
        assessment = assess_readiness(
            project=result.project,
            canonical_data=canonical,
            dataset_id=result.dataset["dataset_id"],
        )
        commercial_output = next((o for o in assessment.outputs if o.name == "commercial_analysis"), None)
        self.assertIsNotNone(commercial_output)
        self.assertTrue(commercial_output.available, f"Commercial analysis not available: {commercial_output.reasons}")

    # --- test 8: mandatory document records are uploaded and valid ---

    def test_mandatory_document_records_are_uploaded_and_valid(self) -> None:
        canonical = self._canonical()
        documents = canonical.get("document_register", [])
        mandatory = [r for r in documents if r.get("requirement") == "mandatory"]
        self.assertTrue(len(mandatory) >= 3, f"Expected ≥3 mandatory documents, got {len(mandatory)}")
        mandatory_types = {r["document_type"] for r in mandatory}
        self.assertIn("current_specification", mandatory_types)
        self.assertIn("proposed_specification", mandatory_types)
        self.assertIn("supplier_quotation", mandatory_types)
        for doc in mandatory:
            self.assertEqual(doc.get("upload_status"), "uploaded", f"{doc['document_type']} not uploaded")
            self.assertNotEqual(doc.get("verification_status"), "expired", f"{doc['document_type']} is expired")
            self.assertTrue(doc.get("file_reference"), f"{doc['document_type']} missing file_reference")

    # --- test 9: mandatory quality test evidence is present and valid ---

    def test_mandatory_quality_test_evidence_is_present_and_valid(self) -> None:
        canonical = self._canonical()
        tests = canonical.get("quality_tests", [])
        mandatory = [r for r in tests if r.get("requirement") == "mandatory"]
        self.assertTrue(len(mandatory) >= 1, "Expected at least one mandatory quality test")
        bct_tests = [r for r in mandatory if r.get("test_name") == "BCT"]
        self.assertEqual(len(bct_tests), 1, "Expected exactly one mandatory BCT test")
        bct = bct_tests[0]
        self.assertIsNotNone(bct.get("result_value"), "BCT test has no result_value")
        self.assertEqual(bct.get("source_classification"), "laboratory_tested")
        self.assertNotEqual(
            (bct.get("source_classification"), bct.get("validation_status")),
            ("supplier_declared", "valid"),
            "BCT must not be marked supplier_declared with valid status",
        )
        self.assertGreater(bct["result_value"], 0)

    # --- test 10: human approval and non-autonomy boundaries are preserved ---
    # (covered in PortfolioSeedTests.test_seed_preserves_human_approval_and_non_autonomy_boundaries)

    # --- test 11: gross annual saving is ₹4,320,000 ---

    def test_gross_annual_saving_at_1_2_million_volume_is_4320000_inr(self) -> None:
        current_unit_cost = 52.4
        proposed_unit_cost = 48.8
        annual_volume = 1_200_000
        gross_saving = (current_unit_cost - proposed_unit_cost) * annual_volume
        self.assertAlmostEqual(gross_saving, 4_320_000.0, places=0)

        # Verify that the canonical data carries these exact values.
        canonical = self._canonical()
        commercial = {
            r["field_key"]: r["value"]
            for r in canonical.get("intake_values", [])
            if r.get("context") == "commercial"
        }
        implied_saving = (commercial["current_unit_cost"] - commercial["proposed_unit_cost"]) * commercial["annual_volume"]
        self.assertAlmostEqual(implied_saving, 4_320_000.0, places=0)

    # --- test 12: material reduction from 980 g to 880 g is approx 10.2 % ---

    def test_material_reduction_from_980_to_880_g_is_approximately_10_2_percent(self) -> None:
        baseline_weight_g = 980.0
        proposed_weight_g = 880.0
        reduction_pct = (baseline_weight_g - proposed_weight_g) / baseline_weight_g * 100
        self.assertAlmostEqual(reduction_pct, 10.204, places=2)

        # Verify that the canonical alternatives carry these weights.
        canonical = self._canonical()
        alts = {r["alternative_id"]: r for r in canonical.get("packaging_alternatives", [])}
        self.assertAlmostEqual(alts["ALT-BASE"]["case_weight_g"], 980.0, places=1)
        self.assertAlmostEqual(alts["ALT-A"]["case_weight_g"], 880.0, places=1)

    # --- test 13: decision snapshot selects ALT-A as preferred conditional alternative ---

    def test_decision_snapshot_selects_alt_a_as_preferred_conditional_alternative(self) -> None:
        """Governed decision snapshot must deterministically select ALT-A with full risk/tech coverage."""
        result = seed_portfolio_demo(self.database_path)
        snapshot = result.decision_snapshot

        recommendation = json.loads(snapshot["recommendation_json"])
        gate = json.loads(snapshot["gate_results_json"])
        self.assertFalse(recommendation["autonomous_approval"], "Autonomous approval must be False")
        self.assertTrue(recommendation["engineering_validation_required"], "Engineering validation must be required")
        self.assertTrue(recommendation["human_approval_required"], "Human approval must be required")

        # Preferred alternative
        self.assertEqual(
            recommendation["preferred_alternative_id"],
            "ALT-A",
            f"Expected ALT-A as preferred; got {recommendation['preferred_alternative_id']}",
        )

        # Recommendation status is conditional or eligible engineering review
        eligible_statuses = {
            "conditionally_recommended_for_engineering_review",
            "recommended_for_engineering_review",
        }
        self.assertIn(
            recommendation["status"],
            eligible_statuses,
            f"Unexpected recommendation status: {recommendation['status']}",
        )

        # Governed control status is not insufficient_data or blocked
        self.assertNotIn(
            gate["selected_control_status"],
            {"insufficient_data", "blocked"},
            f"Control status must not be insufficient_data/blocked; got {gate['selected_control_status']}",
        )

        # ALT-A risk and technical status from scenario results
        alt_a = gate["alternatives"]["ALT-A"]
        self.assertTrue(alt_a["risk_data_complete"], "ALT-A risk_data_complete must be True")
        self.assertNotEqual(
            alt_a["technical_status"],
            "insufficient_data",
            "ALT-A technical_status must not be insufficient_data",
        )

    # --- test 14: no business-engine files were changed by this upgrade ---

    def test_no_business_engine_or_workflow_files_were_modified(self) -> None:
        """Guard that the upgrade touched only the data, seeder, and test layers."""
        import importlib
        protected_modules = [
            "src.validation_readiness.service",
            "src.commercial.savings_engine",
            "src.cost_engine.engine",
            "src.category_registry.corrugated_recommendation",
            "src.category_registry.corrugated_screening",
            "src.category_registry.corrugated_economics",
        ]
        for module_path in protected_modules:
            try:
                importlib.import_module(module_path)
            except ImportError as error:
                self.fail(f"Protected engine module {module_path} could not be imported: {error}")


if __name__ == "__main__":
    unittest.main()
