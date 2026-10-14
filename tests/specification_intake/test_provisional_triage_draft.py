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
