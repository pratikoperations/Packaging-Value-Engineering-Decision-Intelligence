from __future__ import annotations

import unittest

from src.application.specification_upload import (
    serialize_provisional_triage,
    restore_provisional_triage,
)


class ProvisionalTriageDraftTests(unittest.TestCase):
    def test_round_trip_preserves_notes_and_separates_review_records(self):
        state = {
            "triage_value_box_weight_proposed": "790 g",
            "triage_evidence_box_weight_proposed": "Supplier assertion; lab report pending",
        }
        entries = serialize_provisional_triage(state)
        self.assertEqual(len(entries), 1)
        restored = {}
        reviews = restore_provisional_triage(
            restored, ({"review_id": "proposed:box_weight:block1", "state": "pending"},) + entries
        )
        self.assertEqual(len(reviews), 1)
        self.assertEqual(restored, state)
        self.assertEqual(entries[0]["state"], "provisional")

    def test_manual_source_mapping_persists_through_triage_draft(self):
        mapping = {
            "block_id": "proposed-block-2",
            "sha256": "b" * 64,
            "value": "790 g",
        }
        state = {
            "triage_value_box_weight_proposed": "790 g",
            "triage_evidence_box_weight_proposed": "Source checked by reviewer",
            "manual_source_box_weight_proposed": mapping,
        }
        records = serialize_provisional_triage(state)
        recovered = {}
        restore_provisional_triage(recovered, records)
        self.assertEqual(recovered["manual_source_box_weight_proposed"], mapping)
        self.assertEqual(recovered["triage_value_box_weight_proposed"], "790 g")

    def test_invalid_manual_mapping_rejected(self):
        with self.assertRaises(ValueError):
            restore_provisional_triage({}, ({
                "review_id": "provisional-triage:box_weight_proposed",
                "state": "provisional",
                "value": "790 g",
                "evidence": "",
                "manual_source": {"block_id": "missing"},
            },))

    def test_rejected_late_record_does_not_partially_mutate_session(self):
        state = {"triage_value_box_weight_proposed": "original"}
        valid = {
            "review_id": "provisional-triage:liner_gsm_proposed",
            "state": "provisional",
            "value": "140",
            "evidence": "Supplier document",
        }
        invalid = {
            "review_id": "provisional-triage:box_weight_proposed",
            "state": "provisional",
            "value": "790 g",
            "evidence": "",
            "manual_source": {"block_id": "not-valid"},
        }
        with self.assertRaises(ValueError):
            restore_provisional_triage(state, (valid, invalid))
        self.assertEqual(state, {"triage_value_box_weight_proposed": "original"})

    def test_manual_mapping_must_match_provisional_value(self):
        with self.assertRaises(ValueError):
            restore_provisional_triage({}, ({
                "review_id": "provisional-triage:box_weight_proposed",
                "state": "provisional", "value": "790 g", "evidence": "",
                "manual_source": {
                    "block_id": "block-2", "sha256": "b" * 64, "value": "900 g",
                },
            },))

    def test_source_backed_existing_mapping_can_be_restored(self):
        state = {}
        record = {
            "review_id": "provisional-triage:box_weight_existing",
            "state": "provisional", "value": "790 g", "evidence": "Approved baseline block",
            "manual_source": {
                "block_id": "block-2", "sha256": "b" * 64, "value": "790 g",
            },
        }
        self.assertEqual(restore_provisional_triage(state, (record,)), ())
        self.assertEqual(state["manual_source_box_weight_existing"]["block_id"], "block-2")


    def test_empty_values_do_not_create_evidence(self):
        self.assertEqual(serialize_provisional_triage({"triage_value_a": "  "}), ())

    def test_invalid_duplicate_triage_is_rejected(self):
        record = {
            "review_id": "provisional-triage:box_weight_proposed",
            "state": "provisional",
            "value": "1",
            "evidence": "None",
        }
        with self.assertRaises(ValueError):
            restore_provisional_triage({}, (record, record))

    def test_provisional_record_cannot_claim_confirmation(self):
        with self.assertRaises(ValueError):
            restore_provisional_triage({}, ({
                "review_id": "provisional-triage:box_weight_proposed",
                "state": "confirmed",
                "value": "1",
            },))


if __name__ == "__main__":
    unittest.main()
