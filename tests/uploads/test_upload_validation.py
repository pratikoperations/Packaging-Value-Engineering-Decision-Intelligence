from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.application import ProjectService
from src.persistence import Database, DatasetRepository, ProjectRepository
from src.persistence._utils import content_hash
from src.persistence.migrations import initialize_database
from src.uploads import DuplicateDatasetError, UploadParseError, UploadService
from src.uploads.csv_parser import parse_csv_uploads
from src.uploads.json_parser import MAX_UPLOAD_BYTES, parse_json_upload
from src.uploads.normalizer import normalize_user_dataset
from src.uploads.templates import (
    build_alternatives_csv_template,
    build_json_template,
    build_project_csv_template,
)
from src.uploads.validation import validate_user_dataset

ROOT = Path(__file__).resolve().parents[2]
UPLOAD_PAGE = ROOT / "pages" / "02_Upload_Validate.py"


class UploadValidationTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "upload.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project_service = ProjectService(self.projects)
        self.datasets = DatasetRepository(self.database)
        self.upload_service = UploadService(self.datasets)
        self.project = self.project_service.create_project(
            project_code="PVE-UPLOAD-001",
            project_name="Upload project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100000,
        )

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def json_bytes(self) -> bytes:
        return build_json_template(self.project).encode("utf-8")

    def csv_files(self) -> dict[str, bytes]:
        return {
            "project.csv": build_project_csv_template(self.project).encode("utf-8"),
            "alternatives.csv": build_alternatives_csv_template().encode("utf-8"),
        }

    def test_json_parser_accepts_utf8_object(self):
        parsed = parse_json_upload(b'{"value": 1}')
        self.assertEqual(parsed, {"value": 1})

    def test_json_parser_rejects_invalid_json(self):
        with self.assertRaisesRegex(UploadParseError, "Invalid JSON"):
            parse_json_upload(b"{")

    def test_json_parser_rejects_non_object_root(self):
        with self.assertRaisesRegex(UploadParseError, "root must be an object"):
            parse_json_upload(b"[]")

    def test_json_parser_rejects_empty_file(self):
        with self.assertRaisesRegex(UploadParseError, "empty"):
            parse_json_upload(b"")

    def test_json_parser_enforces_size_limit(self):
        with self.assertRaisesRegex(UploadParseError, "2 MB"):
            parse_json_upload(b"x" * (MAX_UPLOAD_BYTES + 1))

    def test_csv_parser_requires_both_templates(self):
        with self.assertRaisesRegex(UploadParseError, "Missing"):
            parse_csv_uploads({"project.csv": self.csv_files()["project.csv"]})

    def test_csv_parser_rejects_unsupported_file(self):
        files = self.csv_files()
        files["costs.csv"] = b"cost_id\nC-1\n"
        with self.assertRaisesRegex(UploadParseError, "Unsupported CSV"):
            parse_csv_uploads(files)

    def test_csv_parser_requires_one_project_row(self):
        files = self.csv_files()
        files["project.csv"] = (
            "project_name,category,annual_volume,currency\n"
            "One,corrugated_shipping_case,1,INR\n"
            "Two,corrugated_shipping_case,2,INR\n"
        ).encode("utf-8")
        with self.assertRaisesRegex(UploadParseError, "exactly one"):
            parse_csv_uploads(files)

    def test_csv_parser_requires_alternative_columns(self):
        files = self.csv_files()
        files["alternatives.csv"] = b"alternative_id,name\nALT-BASE,Base\n"
        with self.assertRaisesRegex(UploadParseError, "missing required columns"):
            parse_csv_uploads(files)

    def test_normalizer_binds_upload_to_active_project(self):
        canonical = normalize_user_dataset({}, self.project)
        self.assertEqual(canonical["dataset_type"], "user_upload")
        self.assertEqual(canonical["packaging_project"]["project_id"], self.project["project_id"])
        self.assertEqual(canonical["packaging_project"]["category"], self.project["category"])

    def test_normalizer_coerces_csv_numbers(self):
        raw = parse_csv_uploads(self.csv_files())
        canonical = normalize_user_dataset(raw, self.project)
        self.assertIsInstance(canonical["packaging_project"]["annual_volume"], int)
        self.assertIsInstance(canonical["packaging_alternatives"][0]["length_mm"], int)

    def test_normalizer_preserves_non_integral_decimals(self):
        raw = {
            "packaging_project": {
                "annual_volume": "100000.25",
            },
            "packaging_alternatives": [],
        }
        canonical = normalize_user_dataset(raw, self.project)
        value = canonical["packaging_project"]["annual_volume"]
        self.assertIsInstance(value, float)
        self.assertEqual(value, 100000.25)

    def test_normalizer_preserves_booleans_in_numeric_fields(self):
        raw = {
            "packaging_project": {
                "annual_volume": True,
            },
            "packaging_alternatives": [],
        }
        canonical = normalize_user_dataset(raw, self.project)
        value = canonical["packaging_project"]["annual_volume"]
        self.assertIs(value, True)
        self.assertIsInstance(value, bool)

    def test_json_template_validates_for_active_project(self):
        prepared = self.upload_service.prepare_json(
            content=self.json_bytes(),
            filename="template.json",
            project=self.project,
        )
        self.assertTrue(prepared.validation.is_valid)
        self.assertTrue(prepared.validation.insufficient_data_eligible)

    def test_csv_templates_validate_for_active_project(self):
        prepared = self.upload_service.prepare_csv(files=self.csv_files(), project=self.project)
        self.assertTrue(prepared.validation.is_valid)
        self.assertEqual(prepared.source_type, "csv_templates")

    def test_user_validator_rejects_category_mismatch(self):
        canonical = json.loads(build_json_template(self.project))
        canonical["packaging_project"]["category"] = "flexible_packaging"
        result = validate_user_dataset(
            canonical,
            expected_project_id=self.project["project_id"],
            expected_category=self.project["category"],
            expected_currency=self.project["currency"],
        )
        self.assertIn("category_mismatch", {issue.code for issue in result.issues})

    def test_user_validator_rejects_currency_mismatch(self):
        canonical = json.loads(build_json_template(self.project))
        canonical["packaging_project"]["currency"] = "USD"
        result = validate_user_dataset(
            canonical,
            expected_project_id=self.project["project_id"],
            expected_category=self.project["category"],
            expected_currency=self.project["currency"],
        )
        self.assertIn("currency_mismatch", {issue.code for issue in result.issues})

    def test_user_validator_rejects_multiple_baselines(self):
        canonical = json.loads(build_json_template(self.project))
        canonical["packaging_alternatives"][1]["status"] = "baseline"
        result = validate_user_dataset(
            canonical,
            expected_project_id=self.project["project_id"],
            expected_category=self.project["category"],
            expected_currency=self.project["currency"],
        )
        self.assertIn("invalid_baseline_count", {issue.code for issue in result.issues})

    def test_user_validator_blocks_uploaded_approval(self):
        canonical = json.loads(build_json_template(self.project))
        canonical["decision_recommendation"]["status"] = "recommended"
        result = validate_user_dataset(
            canonical,
            expected_project_id=self.project["project_id"],
            expected_category=self.project["category"],
            expected_currency=self.project["currency"],
        )
        self.assertIn("unsafe_upload_recommendation", {issue.code for issue in result.issues})

    def test_invalid_upload_cannot_be_saved(self):
        raw = json.loads(build_json_template(self.project))
        raw["packaging_alternatives"] = []
        prepared = self.upload_service.prepare_json(
            content=json.dumps(raw).encode("utf-8"),
            filename="invalid.json",
            project=self.project,
        )
        with self.assertRaisesRegex(ValueError, "Invalid uploads"):
            self.upload_service.save_valid_dataset(
                project_id=self.project["project_id"],
                prepared=prepared,
            )

    def test_valid_upload_creates_immutable_dataset_version(self):
        prepared = self.upload_service.prepare_json(
            content=self.json_bytes(),
            filename="template.json",
            project=self.project,
        )
        saved = self.upload_service.save_valid_dataset(
            project_id=self.project["project_id"],
            prepared=prepared,
        )
        self.assertEqual(saved["version_number"], 1)
        self.assertEqual(saved["validation_status"], "valid")

    def test_duplicate_upload_is_rejected(self):
        prepared = self.upload_service.prepare_json(
            content=self.json_bytes(),
            filename="template.json",
            project=self.project,
        )
        self.upload_service.save_valid_dataset(
            project_id=self.project["project_id"],
            prepared=prepared,
        )
        with self.assertRaisesRegex(DuplicateDatasetError, "already exists"):
            self.upload_service.save_valid_dataset(
                project_id=self.project["project_id"],
                prepared=prepared,
            )

    def test_duplicate_detection_uses_canonical_content_across_formats(self):
        json_prepared = self.upload_service.prepare_json(
            content=self.json_bytes(),
            filename="template.json",
            project=self.project,
        )
        csv_prepared = self.upload_service.prepare_csv(
            files=self.csv_files(),
            project=self.project,
        )

        json_volume = json_prepared.canonical_data["packaging_project"]["annual_volume"]
        csv_volume = csv_prepared.canonical_data["packaging_project"]["annual_volume"]
        self.assertEqual(type(json_volume), type(csv_volume))
        self.assertEqual(json_volume, csv_volume)
        self.assertEqual(json_prepared.canonical_data, csv_prepared.canonical_data)
        self.assertEqual(
            content_hash(json_prepared.canonical_data),
            content_hash(csv_prepared.canonical_data),
        )

        self.upload_service.save_valid_dataset(
            project_id=self.project["project_id"],
            prepared=json_prepared,
        )
        with self.assertRaises(DuplicateDatasetError):
            self.upload_service.save_valid_dataset(
                project_id=self.project["project_id"],
                prepared=csv_prepared,
            )

    def test_same_content_can_exist_in_different_projects(self):
        second = self.project_service.create_project(
            project_code="PVE-UPLOAD-002",
            project_name="Second upload project",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100000,
        )
        first_prepared = self.upload_service.prepare_json(
            content=self.json_bytes(),
            filename="first.json",
            project=self.project,
        )
        second_prepared = self.upload_service.prepare_json(
            content=build_json_template(second).encode("utf-8"),
            filename="second.json",
            project=second,
        )
        self.upload_service.save_valid_dataset(
            project_id=self.project["project_id"],
            prepared=first_prepared,
        )
        saved = self.upload_service.save_valid_dataset(
            project_id=second["project_id"],
            prepared=second_prepared,
        )
        self.assertEqual(saved["version_number"], 1)

    def test_upload_page_static_contract(self):
        page = UPLOAD_PAGE.read_text(encoding="utf-8")
        for marker in (
            "Upload and Validate Packaging Data",
            "Download JSON template",
            "Download project.csv",
            "Download alternatives.csv",
            "Save immutable dataset version",
            "Archived projects are read-only",
            "Duplicate canonical content is rejected",
        ):
            self.assertIn(marker, page)

    def test_upload_page_excludes_unapproved_scope(self):
        page = UPLOAD_PAGE.read_text(encoding="utf-8")
        for prohibited in (
            "Run scenario",
            "Configure thresholds",
            "Decision history",
            "Supplier allocation",
            "st.file_uploader(\"Upload PDF",
        ):
            self.assertNotIn(prohibited, page)


if __name__ == "__main__":
    unittest.main()
