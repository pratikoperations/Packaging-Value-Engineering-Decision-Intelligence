from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.ai_extraction import ConfidenceBand, ExtractionCandidate
from src.document_intake import DocumentRole
from src.pdf_intake import ParsedPdf, PdfSourceBlock
from src.pdf_intake.integration import build_pdf_review_bundle
from src.pdf_intake.snapshot import build_confirmed_pdf_snapshot, build_pdf_canonical_dataset_draft
from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.pdf_intake_repository import PdfIntakeRepository
from src.persistence.project_repository import ProjectRepository
from src.review_comparison import confirm, correct_and_confirm, group_reviews


def document(role, block_id, text):
    return ParsedPdf(
        filename=f"{role.value}.pdf", role=role,
        sha256=("e" if role is DocumentRole.EXISTING else "p") * 64,
        page_count=2, parser_version="pve-pdf-parser-v1",
        blocks=(PdfSourceBlock(
            block_id=block_id, page_number=2, block_index=0, extraction_order=3,
            raw_text=text.replace(" ", "  "), normalized_text=text,
            parser_version="pve-pdf-parser-v1",
        ),),
    )


def candidate(role, block_id, value):
    return ExtractionCandidate(
        field_name="box_weight", document_role=role,
        raw_value=value, normalized_value=value, unit="g", confidence=96,
        confidence_band=ConfidenceBand.HIGH, source_block_id=block_id,
        source_excerpt=f"Box weight: {value} g", ambiguity_codes=(),
    )


class PdfSnapshotPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp.name) / "pve.db")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project = self.projects.create(
            project_id="pdf-project", project_code="PDF-001",
            project_name="Synthetic PDF Intake", category="corrugated_shipping_case",
            currency="INR", annual_volume=100000, status="active",
            volume_unit="cases_per_year",
        )
        self.existing = document(DocumentRole.EXISTING, "pdf-e", "Box weight: 780 g")
        self.proposed = document(DocumentRole.PROPOSED, "pdf-p", "Box weight: 650 g")
        bundle = build_pdf_review_bundle(
            (candidate(DocumentRole.EXISTING, "pdf-e", 780), candidate(DocumentRole.PROPOSED, "pdf-p", 650)),
            (self.existing, self.proposed),
        )
        reviews = [confirm(bundle.reviews[0].review)]
        reviews.append(correct_and_confirm(bundle.reviews[1].review, 645, "g", reviewer_note="Verified against PDF note"))
        self.groups = group_reviews(reviews)

    def tearDown(self):
        self.temp.cleanup()

    def snapshot(self, snapshot_id="pdf-snapshot-1"):
        draft, issues, valid = build_pdf_canonical_dataset_draft(
            project=self.project, groups=self.groups,
            source_repository="repo", source_commit="sha",
        )
        return build_confirmed_pdf_snapshot(
            snapshot_id=snapshot_id, project_id="pdf-project",
            documents=(self.existing, self.proposed), groups=self.groups,
            canonical_dataset_draft=draft,
            canonical_validation_issues=issues,
            canonical_validation_valid=valid,
            extraction_schema_version="pve-word-extraction-v1",
            alias_registry_version="1.0", provider_id="mock-pdf-provider",
        )

    def test_snapshot_preserves_pdf_source_and_corrections(self):
        snapshot = self.snapshot()
        proposed = next(field for field in snapshot.confirmed_fields if field.document_role == "proposed")
        self.assertEqual(proposed.raw_value, 650)
        self.assertEqual(proposed.corrected_value, 645)
        self.assertEqual(proposed.effective_value, 645)
        self.assertEqual(proposed.page_number, 2)
        self.assertEqual(proposed.block_index, 0)
        self.assertEqual(proposed.extraction_order, 3)
        self.assertIn("  ", proposed.raw_pdf_text)
        self.assertEqual(snapshot.existing_document_hash, "e" * 64)
        self.assertEqual(snapshot.parser_version, "pve-pdf-parser-v1")

    def test_hash_is_deterministic_and_canonical_validation_is_reused(self):
        first = self.snapshot("a")
        second = self.snapshot("b")
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertFalse(first.canonical_validation_valid)
        self.assertTrue(first.canonical_validation_issues)
        self.assertIn("PDF-intake", first.canonical_dataset_draft["synthetic_notice"])

    def test_append_only_repository_and_duplicate_content_protection(self):
        repository = PdfIntakeRepository(self.database)
        stored = repository.create(self.snapshot())
        self.assertEqual(stored["project_id"], "pdf-project")
        self.assertEqual(stored["confirmed_fields"][0]["page_number"], 2)
        with self.assertRaises(sqlite3.IntegrityError):
            repository.create(self.snapshot("different-id"))
        with self.assertRaises(ValueError):
            repository.update("pdf-snapshot-1")
        with self.assertRaises(ValueError):
            repository.delete("pdf-snapshot-1")

    def test_database_triggers_and_project_protections(self):
        repository = PdfIntakeRepository(self.database)
        repository.create(self.snapshot())
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("UPDATE pdf_intake_snapshots SET provider_id='changed'")
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute("DELETE FROM pdf_intake_snapshots")
        missing = self.snapshot("missing")
        object.__setattr__(missing, "project_id", "missing-project")
        with self.assertRaises(KeyError):
            repository.create(missing)
        self.projects.archive("pdf-project")
        with self.assertRaisesRegex(ValueError, "Archived projects"):
            repository.create(self.snapshot("archived"))


if __name__ == "__main__":
    unittest.main()
