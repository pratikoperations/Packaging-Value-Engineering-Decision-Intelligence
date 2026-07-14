import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.persistence import Database, ProjectRepository, ReadinessRepository
from src.persistence.migrations import SCHEMA_VERSION, current_schema_version, initialize_database
from src.validation_readiness import assess_readiness


def canonical(complete=True):
    value = 1 if complete else None
    return {
        "packaging_project": {
            "project_id": "PROJECT", "project_name": "Readiness", "category": "corrugated",
            "objective": "Cost reduction", "change_type": "GSM reduction",
            "annual_volume": 1000, "currency": "INR",
        },
        "intake_values": [
            {"context": "baseline", "field_key": "length_mm", "requirement": "mandatory", "value": value, "unit": "mm", "source_classification": "uploaded_fact"},
            {"context": "proposed", "field_key": "length_mm", "requirement": "mandatory", "value": value, "unit": "mm", "source_classification": "supplier_declared"},
            {"context": "commercial", "field_key": "annual_volume", "requirement": "mandatory", "value": 1000, "source_classification": "manually_entered_fact"},
            {"context": "commercial", "field_key": "current_unit_cost", "requirement": "mandatory", "value": 10 if complete else None, "source_classification": "uploaded_fact"},
            {"context": "commercial", "field_key": "proposed_unit_cost", "requirement": "recommended", "value": 9 if complete else None, "source_classification": "supplier_declared"},
            {"context": "logistics", "field_key": "route", "requirement": "recommended", "value": "A-B" if complete else None, "source_classification": "assumption"},
        ],
        "quality_tests": [{"test_name": "BCT", "requirement": "mandatory", "result_value": 100 if complete else None, "source_classification": "laboratory_tested", "validation_status": "valid"}],
        "document_register": [
            {"document_type": "current_specification", "requirement": "mandatory", "upload_status": "uploaded" if complete else "missing", "file_reference": "current.pdf" if complete else None, "verification_status": "valid"},
            {"document_type": "proposed_specification", "requirement": "mandatory", "upload_status": "uploaded" if complete else "missing", "file_reference": "proposed.pdf" if complete else None, "verification_status": "valid"},
        ],
    }


class ReadinessTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.tempdir.name) / "pve.sqlite3")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project = self.projects.create(
            project_code="PVE-RDY-1", project_name="Readiness", category="corrugated",
            currency="INR", annual_volume=1000, objective="Cost reduction",
            change_type="GSM reduction", volume_unit="units/year",
        )
        self.repository = ReadinessRepository(self.database)

    def tearDown(self):
        self.tempdir.cleanup()

    def test_current_schema_preserves_readiness_storage(self):
        self.assertEqual(current_schema_version(self.database), SCHEMA_VERSION)

    def test_blockers_override_score_and_never_approve(self):
        data = canonical(True)
        data["document_register"][0]["upload_status"] = "missing"
        assessment = assess_readiness(project=self.project, canonical_data=data)
        self.assertGreater(assessment.score_percent, 50)
        self.assertEqual(assessment.stage, "Insufficient Data")
        self.assertIn("autonomous approval is prohibited", assessment.approval_limitation)

    def test_output_availability_and_traceability(self):
        assessment = assess_readiness(project=self.project, canonical_data=canonical(True))
        outputs = {item.name: item for item in assessment.outputs}
        self.assertTrue(outputs["commercial_analysis"].available)
        self.assertFalse(outputs["technical_feasibility"].available)
        self.assertFalse(outputs["approval_decision"].available)
        self.assertEqual(assessment.source_traceability["supplier_declared"], 2)

    def test_persistence_is_append_only(self):
        assessment = assess_readiness(project=self.project, canonical_data=canonical(True))
        saved = self.repository.create(project_id=self.project["project_id"], dataset_id=None, assessment=assessment.as_dict())
        self.assertEqual(saved["stage"], assessment.stage)
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("UPDATE readiness_assessments SET stage = 'Draft'")

    def test_archived_projects_reject_writes(self):
        assessment = assess_readiness(project=self.project, canonical_data=canonical(True))
        self.projects.archive(self.project["project_id"])
        with self.assertRaisesRegex(ValueError, "Archived projects"):
            self.repository.create(project_id=self.project["project_id"], dataset_id=None, assessment=assessment.as_dict())

    def test_incomplete_data_is_insufficient(self):
        assessment = assess_readiness(project=self.project, canonical_data=canonical(False))
        self.assertEqual(assessment.stage, "Insufficient Data")
        self.assertIn("No baseline specification", assessment.blockers)


if __name__ == "__main__":
    unittest.main()
