from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.application import ProjectService
from src.persistence import Database, ProjectRepository, ThresholdRepository
from src.persistence.migrations import initialize_database
from src.thresholds import MANDATORY_ENGINEERING_CONTROLS, ThresholdService, ThresholdValidationError
from src.thresholds.policy import DEFAULT_CONTROLLED_PROFILE, business_thresholds_pass, validate_threshold_profile

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "pages" / "03_Business_Thresholds.py"
TEMPLATE = ROOT / "docs" / "templates" / "PVE_THRESHOLD_PROFILE_TEMPLATE.json"


class ThresholdProfileTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "thresholds.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project_service = ProjectService(self.projects)
        self.thresholds = ThresholdRepository(self.database)
        self.service = ThresholdService(self.thresholds)
        self.project = self.project_service.create_project(
            project_code="PVE-THRESH-001",
            project_name="Threshold project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100000,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def test_default_profile_is_created_once(self):
        first = self.service.ensure_default_profile()
        second = self.service.ensure_default_profile()
        self.assertEqual(first["threshold_profile_id"], second["threshold_profile_id"])
        self.assertEqual(first["version_number"], 1)

    def test_default_profile_is_global_and_read_only(self):
        default = self.service.ensure_default_profile()
        self.assertIsNone(default["project_id"])
        with self.assertRaisesRegex(ThresholdValidationError, "cannot be edited"):
            self.service.create_new_version(
                threshold_profile_id=default["threshold_profile_id"],
                profile=DEFAULT_CONTROLLED_PROFILE,
            )

    def test_create_project_specific_profile(self):
        record = self.service.create_project_profile(
            project_id=self.project["project_id"],
            profile_name="Savings Gate",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        self.assertEqual(record["project_id"], self.project["project_id"])
        self.assertEqual(record["version_number"], 1)

    def test_new_profile_content_creates_new_version(self):
        first = self.service.create_project_profile(
            project_id=self.project["project_id"],
            profile_name="Savings Gate",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        updated = dict(DEFAULT_CONTROLLED_PROFILE)
        updated["minimum_annual_savings"] = 50000
        second = self.service.create_new_version(
            threshold_profile_id=first["threshold_profile_id"],
            profile=updated,
        )
        self.assertEqual(second["version_number"], 2)
        self.assertNotEqual(first["threshold_profile_id"], second["threshold_profile_id"])

    def test_duplicate_profile_content_returns_existing_version(self):
        first = self.service.create_project_profile(
            project_id=self.project["project_id"],
            profile_name="Savings Gate",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        second = self.service.create_project_profile(
            project_id=self.project["project_id"],
            profile_name="Savings Gate",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        self.assertEqual(first["threshold_profile_id"], second["threshold_profile_id"])

    def test_available_profiles_include_global_and_current_project_only(self):
        other = self.project_service.create_project(
            project_code="PVE-THRESH-002",
            project_name="Other",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100,
        )
        self.service.create_project_profile(
            project_id=self.project["project_id"],
            profile_name="Mine",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        self.service.create_project_profile(
            project_id=other["project_id"],
            profile_name="Other",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        records = self.service.available_profiles(self.project["project_id"])
        project_ids = {record["project_id"] for record in records}
        self.assertEqual(project_ids, {None, self.project["project_id"]})

    def test_threshold_profiles_remain_immutable(self):
        record = self.service.create_project_profile(
            project_id=self.project["project_id"],
            profile_name="Immutable",
            profile=DEFAULT_CONTROLLED_PROFILE,
        )
        with self.assertRaises(Exception):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE threshold_profiles SET profile_name = 'Changed' WHERE threshold_profile_id = ?",
                    (record["threshold_profile_id"],),
                )

    def test_validation_rejects_missing_fields(self):
        with self.assertRaisesRegex(ValueError, "Missing threshold fields"):
            validate_threshold_profile({})

    def test_validation_rejects_extra_fields(self):
        profile = dict(DEFAULT_CONTROLLED_PROFILE)
        profile["engineering_validation_required"] = False
        with self.assertRaisesRegex(ValueError, "Unsupported threshold fields"):
            validate_threshold_profile(profile)

    def test_validation_rejects_negative_values(self):
        profile = dict(DEFAULT_CONTROLLED_PROFILE)
        profile["minimum_annual_savings"] = -1
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            validate_threshold_profile(profile)

    def test_business_thresholds_pass_for_compliant_case(self):
        passed, reasons = business_thresholds_pass(
            profile=DEFAULT_CONTROLLED_PROFILE,
            annual_savings=100,
            material_change_percent=-1,
            overall_risk="medium",
        )
        self.assertTrue(passed)
        self.assertEqual(reasons, ())

    def test_business_thresholds_reject_below_savings_gate(self):
        profile = dict(DEFAULT_CONTROLLED_PROFILE)
        profile["minimum_annual_savings"] = 1000
        passed, reasons = business_thresholds_pass(
            profile=profile,
            annual_savings=100,
            material_change_percent=-1,
            overall_risk="medium",
        )
        self.assertFalse(passed)
        self.assertIn("Annual savings are below", reasons[0])

    def test_business_thresholds_reject_excessive_risk(self):
        profile = dict(DEFAULT_CONTROLLED_PROFILE)
        profile["maximum_business_risk"] = "medium"
        passed, reasons = business_thresholds_pass(
            profile=profile,
            annual_savings=100,
            material_change_percent=-1,
            overall_risk="high",
        )
        self.assertFalse(passed)
        self.assertTrue(any("risk exceeds" in reason for reason in reasons))

    def test_mandatory_engineering_controls_are_fixed(self):
        self.assertTrue(MANDATORY_ENGINEERING_CONTROLS["engineering_validation_required"])
        self.assertFalse(MANDATORY_ENGINEERING_CONTROLS["autonomous_approval_allowed"])
        self.assertTrue(MANDATORY_ENGINEERING_CONTROLS["critical_risk_blocked"])
        self.assertTrue(MANDATORY_ENGINEERING_CONTROLS["not_qualified_blocked"])

    def test_template_matches_default_profile(self):
        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        self.assertEqual(template, DEFAULT_CONTROLLED_PROFILE)

    def test_threshold_page_static_contract(self):
        page = PAGE.read_text(encoding="utf-8")
        for marker in (
            "Configurable Business Thresholds",
            "Mandatory Engineering Controls",
            "fixed, non-disableable",
            "Save immutable threshold version",
            "active_threshold_profile_id",
            "cannot override failed technical qualification",
        ):
            self.assertIn(marker, page)

    def test_threshold_page_excludes_unapproved_scope(self):
        page = PAGE.read_text(encoding="utf-8")
        for prohibited in (
            "Run scenario",
            "Decision history",
            "Supplier allocation",
            "st.file_uploader",
        ):
            self.assertNotIn(prohibited, page)


if __name__ == "__main__":
    unittest.main()
