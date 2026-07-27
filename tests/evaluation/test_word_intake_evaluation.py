from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.document_intake import DocumentRole, DocumentValidationError, validate_docx
from src.evaluation import GroundTruthField, PredictedField, evaluate
from src.persistence.database import Database
from src.persistence.migrations import current_schema_version, initialize_database
from src.persistence.word_intake_migration import initialize_word_intake_schema


class EvaluationCorpusTests(unittest.TestCase):
    def test_manifest_has_ten_pairs_and_required_layouts(self):
        manifest = json.loads(Path("evaluation/pve_2_0_word/corpus_manifest.json").read_text())
        self.assertTrue(manifest["independent_ground_truth"])
        self.assertEqual(len(manifest["pairs"]), 10)
        self.assertEqual({p["layout"] for p in manifest["pairs"]}, {"paragraph", "table", "mixed"})
        features = {feature for pair in manifest["pairs"] for feature in pair["features"]}
        self.assertIn("prompt_injection", features)
        self.assertIn("unsupported_image", features)
        self.assertIn("oversized_rejection", features)

    def test_threshold_metrics_pass_for_grounded_reference_predictions(self):
        truth = []
        predictions = []
        for pair in range(1, 11):
            for role in ("existing", "proposed"):
                for field, value in (("internal_length", 400 + pair), ("box_weight", 700 - pair)):
                    block = f"PAIR-{pair:02d}:{role}:{field}"
                    truth.append(GroundTruthField(f"PAIR-{pair:02d}", role, field, value, block))
                    predictions.append(PredictedField(f"PAIR-{pair:02d}", role, field, value, block))
                truth.append(GroundTruthField(f"PAIR-{pair:02d}", role, "missing_field", None, "", present=False))
        result = evaluate(truth, predictions)
        self.assertEqual(result.precision, 1.0)
        self.assertEqual(result.recall, 1.0)
        self.assertEqual(result.source_grounding_accuracy, 1.0)
        self.assertEqual(result.document_role_accuracy, 1.0)
        self.assertEqual(result.missing_field_accuracy, 1.0)
        self.assertTrue(result.meets_thresholds())

    def test_invented_unsourced_and_unconfirmed_values_fail_gate(self):
        truth = [GroundTruthField("PAIR-01", "existing", "box_weight", 780, "b1")]
        predictions = [
            PredictedField("PAIR-01", "existing", "box_weight", 780, None),
            PredictedField("PAIR-01", "existing", "supplier_name", "Invented", "b2"),
        ]
        result = evaluate(truth, predictions, unconfirmed_values_mapped=1)
        self.assertEqual(result.accepted_invented_values, 1)
        self.assertEqual(result.accepted_unsourced_values, 1)
        self.assertEqual(result.unconfirmed_values_mapped, 1)
        self.assertFalse(result.meets_thresholds())

    def test_oversized_and_malformed_docx_are_rejected(self):
        with self.assertRaises(DocumentValidationError):
            validate_docx("oversized.docx", b"x" * 101, DocumentRole.EXISTING, max_bytes=100)
        with self.assertRaises(DocumentValidationError):
            validate_docx("malformed.docx", b"not-a-zip", DocumentRole.EXISTING)

    def test_word_intake_migration_is_backward_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            database = Database(Path(directory) / "evaluation.db")
            self.assertEqual(initialize_database(database), 9)
            legacy_version = current_schema_version(database)
            initialize_word_intake_schema(database)
            self.assertEqual(current_schema_version(database), legacy_version)
            with database.connect() as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
            self.assertIn("projects", tables)
            self.assertIn("word_intake_snapshots", tables)


if __name__ == "__main__":
    unittest.main()
