from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.ai_extraction import ConfidenceBand, ExtractionCandidate
from src.document_intake import (
    DocumentPair,
    DocumentRole,
    ParsedDocument,
    SourceBlock,
    SourceBlockType,
    SourceLocation,
)
from src.intake_mapping import (
    IntakeMappingError,
    build_canonical_dataset_draft,
    build_confirmed_snapshot,
    collect_confirmed_fields,
)
from src.persistence.database import Database
from src.persistence.migrations import initialize_database
from src.persistence.project_repository import ProjectRepository
from src.persistence.word_intake_repository import WordIntakeRepository
from src.review_comparison import (
    build_candidate_reviews,
    confirm,
    correct_and_confirm,
    group_reviews,
)


def parsed_document(role: DocumentRole, sha: str, entries: list[tuple[str, str]]) -> ParsedDocument:
    blocks = tuple(
        SourceBlock(
            block_id=block_id,
            block_type=SourceBlockType.TABLE_CELL,
            text=text,
            location=SourceLocation(
                table_index=0,
                row_index=index,
                cell_index=1,
                section_title="Specification",
            ),
        )
        for index, (block_id, text) in enumerate(entries)
    )
    return ParsedDocument(
        filename=f"{role.value}.docx",
        role=role,
        sha256=sha,
        blocks=blocks,
    )


def candidate(
    field_name: str,
    role: DocumentRole,
    block_id: str,
    raw_value,
    normalized_value,
    unit: str | None = None,
) -> ExtractionCandidate:
    return ExtractionCandidate(
        field_name=field_name,
        document_role=role,
        raw_value=raw_value,
        normalized_value=normalized_value,
        unit=unit,
        confidence=96.0,
        confidence_band=ConfidenceBand.HIGH,
        source_block_id=block_id,
        source_excerpt=str(raw_value),
        ambiguity_codes=(),
    )


class MappingAndPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Database(Path(self.temp_dir.name) / "pve.db")
        initialize_database(self.database)
        self.projects = ProjectRepository(self.database)
        self.project = self.projects.create(
            project_id="project-pve2",
            project_code="PVE2-WORD-001",
            project_name="Synthetic Word Intake",
            category="corrugated_shipping_case",
            currency="INR",
            annual_volume=100000,
            status="active",
            volume_unit="cases_per_year",
        )
        self.existing = parsed_document(
            DocumentRole.EXISTING,
            "e" * 64,
            [("e-length", "400"), ("e-weight", "780"), ("e-ply", "5"), ("e-flute", "BC")],
        )
        self.proposed = parsed_document(
            DocumentRole.PROPOSED,
            "p" * 64,
            [("p-length", "390"), ("p-weight", "650"), ("p-ply", "3"), ("p-flute", "B")],
        )
        reviews = []
        for doc, values in (
            (
                self.existing,
                [
                    candidate("internal_length", DocumentRole.EXISTING, "e-length", 400, 400, "mm"),
                    candidate("box_weight", DocumentRole.EXISTING, "e-weight", 780, 780, "g"),
                    candidate("ply_count", DocumentRole.EXISTING, "e-ply", 5, 5, "ply"),
                    candidate("flute_combination", DocumentRole.EXISTING, "e-flute", "BC", "BC"),
                ],
            ),
            (
                self.proposed,
                [
                    candidate("internal_length", DocumentRole.PROPOSED, "p-length", 390, 390, "mm"),
                    candidate("box_weight", DocumentRole.PROPOSED, "p-weight", 650, 650, "g"),
                    candidate("ply_count", DocumentRole.PROPOSED, "p-ply", 3, 3, "ply"),
                    candidate("flute_combination", DocumentRole.PROPOSED, "p-flute", "B", "B"),
                ],
            ),
        ):
            reviews.extend(build_candidate_reviews(values, [doc]))
        reviews = list(reviews)
        reviews[0] = confirm(reviews[0], reviewer_note="Verified")
        reviews[1] = correct_and_confirm(
            reviews[1], 775, "g", reviewer_note="Corrected from specification note"
        )
        for index in range(2, len(reviews)):
            reviews[index] = confirm(reviews[index])
        self.groups = group_reviews(reviews)
        self.documents = DocumentPair(self.existing, self.proposed)

    def tearDown(self):
        self.temp_dir.cleanup()

    def build_snapshot(self, *, snapshot_id="word-intake-test"):
        draft, issues, valid = build_canonical_dataset_draft(
            project=self.project,
            groups=self.groups,
            source_repository="pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
            source_commit="test-sha",
        )
        return build_confirmed_snapshot(
            snapshot_id=snapshot_id,
            project_id=self.project["project_id"],
            documents=self.documents,
            groups=self.groups,
            canonical_dataset_draft=draft,
            canonical_validation_issues=issues,
            canonical_validation_valid=valid,
            parser_version="pve-docx-parser-v1",
            extraction_schema_version="pve-word-extraction-v1",
            alias_registry_version="1.0",
            provider_id="mock-provider",
        )

    def test_maps_only_confirmed_values_and_preserves_correction(self):
        fields = collect_confirmed_fields(self.groups)
        existing_weight = next(
            field
            for field in fields
            if field.document_role == "existing" and field.field_name == "box_weight"
        )
        self.assertEqual(existing_weight.raw_value, 780)
        self.assertEqual(existing_weight.normalized_value, 780)
        self.assertEqual(existing_weight.corrected_value, 775)
        self.assertEqual(existing_weight.effective_value, 775)
        self.assertEqual(existing_weight.review_state, "corrected_confirmed")
        self.assertEqual(existing_weight.source_block_id, "e-weight")

    def test_generates_partial_canonical_draft_and_invokes_existing_validator(self):
        draft, issues, valid = build_canonical_dataset_draft(
            project=self.project,
            groups=self.groups,
            source_repository="repo",
            source_commit="sha",
        )
        self.assertFalse(valid)
        self.assertTrue(any(issue["code"] == "insufficient_alternatives" for issue in issues))
        baseline, proposed = draft["packaging_alternatives"]
        self.assertEqual(baseline["length_mm"], 400)
        self.assertEqual(baseline["case_weight_g"], 775)
        self.assertEqual(baseline["board_grade"], "5PLY_BC_FLUTE")
        self.assertEqual(proposed["length_mm"], 390)
        self.assertEqual(proposed["case_weight_g"], 650)
        self.assertEqual(proposed["board_grade"], "3PLY_B_FLUTE")
        self.assertEqual(draft["decision_recommendation"]["status"], "insufficient_data")

    def test_snapshot_hash_is_deterministic_and_versions_are_preserved(self):
        first = self.build_snapshot(snapshot_id="snapshot-a")
        second = self.build_snapshot(snapshot_id="snapshot-b")
        self.assertEqual(first.content_hash, second.content_hash)
        self.assertEqual(first.existing_document_hash, "e" * 64)
        self.assertEqual(first.proposed_document_hash, "p" * 64)
        self.assertEqual(first.parser_version, "pve-docx-parser-v1")
        self.assertEqual(first.extraction_schema_version, "pve-word-extraction-v1")
        self.assertEqual(first.alias_registry_version, "1.0")

    def test_append_only_repository_round_trip_and_duplicate_content_rejection(self):
        repository = WordIntakeRepository(self.database)
        snapshot = self.build_snapshot()
        stored = repository.create(snapshot)
        self.assertEqual(stored["word_intake_snapshot_id"], "word-intake-test")
        self.assertEqual(stored["project_id"], self.project["project_id"])
        self.assertEqual(stored["confirmed_fields"][0]["document_role"], "existing")
        self.assertEqual(len(repository.list_for_project(self.project["project_id"])), 1)
        with self.assertRaises(sqlite3.IntegrityError):
            repository.create(self.build_snapshot(snapshot_id="different-id"))
        with self.assertRaises(ValueError):
            repository.update("word-intake-test", provider_id="changed")
        with self.assertRaises(ValueError):
            repository.delete("word-intake-test")

    def test_database_triggers_reject_update_and_delete(self):
        repository = WordIntakeRepository(self.database)
        repository.create(self.build_snapshot())
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "UPDATE word_intake_snapshots SET provider_id = 'changed' WHERE word_intake_snapshot_id = 'word-intake-test'"
                )
        with self.assertRaises(sqlite3.IntegrityError):
            with self.database.transaction() as connection:
                connection.execute(
                    "DELETE FROM word_intake_snapshots WHERE word_intake_snapshot_id = 'word-intake-test'"
                )

    def test_archived_and_cross_project_writes_are_rejected(self):
        repository = WordIntakeRepository(self.database)
        cross_project_snapshot = self.build_snapshot(snapshot_id="cross-project")
        object.__setattr__(cross_project_snapshot, "project_id", "missing-project")
        with self.assertRaises(KeyError):
            repository.create(cross_project_snapshot)

        self.projects.archive(self.project["project_id"])
        with self.assertRaisesRegex(ValueError, "Archived projects"):
            repository.create(self.build_snapshot(snapshot_id="archived-project"))
        with self.assertRaisesRegex(IntakeMappingError, "Archived projects"):
            build_canonical_dataset_draft(
                project=self.projects.get(self.project["project_id"]),
                groups=self.groups,
                source_repository="repo",
                source_commit="sha",
            )


if __name__ == "__main__":
    unittest.main()
