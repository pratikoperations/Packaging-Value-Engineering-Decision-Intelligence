from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace

from src.ui.specification_review_ui import (
    SnapshotActionRequest,
    business_blocker_message,
    execute_snapshot_once,
    snapshot_action_token,
    snapshot_identity_rows,
    snapshot_metrics,
)


def request(**changes: str) -> SnapshotActionRequest:
    values = {
        "project_id": "project-1",
        "review_id": "review-1",
        "source_review_revision_id": "revision-4",
        "actor_reference": "buyer@example.com",
        "approval_reason": "All governed fields were reviewed.",
    }
    values.update(changes)
    return SnapshotActionRequest(**values)


def snapshot():
    return SimpleNamespace(
        snapshot_id="approved-snapshot-1",
        review_id="review-1",
        source_review_revision_number=4,
        source_review_revision_id="revision-4",
        existing_dataset_id="dataset-existing",
        proposed_dataset_id="dataset-proposed",
        actor_reference="buyer@example.com",
        created_at="2026-07-31T12:00:00+00:00",
        approved_values=(
            SimpleNamespace(source="accepted_proposed"),
            SimpleNamespace(source="corrected"),
            SimpleNamespace(source="retained_existing"),
            SimpleNamespace(source="unchanged"),
        ),
        excluded_fields=("optional.coating",),
    )


class ApprovedSpecificationUiTests(unittest.TestCase):
    def test_snapshot_request_requires_all_authorization_fields(self):
        for field in (
            "project_id",
            "review_id",
            "source_review_revision_id",
            "actor_reference",
            "approval_reason",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, field):
                    request(**{field: " "})

    def test_snapshot_token_is_deterministic_and_authorization_sensitive(self):
        first = snapshot_action_token(request())
        second = snapshot_action_token(request())
        changed = snapshot_action_token(
            request(approval_reason="Different rationale")
        )
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)
        self.assertNotEqual(changed, first)

    def test_snapshot_execution_is_rerun_safe(self):
        session: dict[str, object] = {}
        calls: list[str] = []
        first = execute_snapshot_once(
            session,
            request(),
            lambda: calls.append("created") or "snapshot",
        )
        second = execute_snapshot_once(
            session,
            request(),
            lambda: calls.append("duplicate") or "other",
        )
        self.assertEqual(first, (True, "snapshot"))
        self.assertEqual(second, (False, None))
        self.assertEqual(calls, ["created"])

    def test_failed_snapshot_execution_clears_pending_token(self):
        session: dict[str, object] = {}

        def fail():
            raise RuntimeError("failure")

        with self.assertRaises(RuntimeError):
            execute_snapshot_once(session, request(), fail)
        self.assertNotIn("approved_snapshot_pending_action_token", session)

    def test_blockers_are_business_readable(self):
        self.assertTrue(
            business_blocker_message(
                "existing_baseline_not_confirmed"
            ).startswith("Confirm the Existing")
        )
        self.assertIn(
            "mandatory field",
            business_blocker_message("mandatory_candidate_pending"),
        )

    def test_unknown_blocker_does_not_expose_technical_details(self):
        message = business_blocker_message("internal_unknown_code")
        self.assertNotIn("internal_unknown_code", message)
        self.assertIn("governed review condition", message)

    def test_snapshot_metrics_count_each_materialization_source(self):
        self.assertEqual(
            snapshot_metrics(snapshot()),
            {
                "approved_field_count": 4,
                "accepted_field_count": 1,
                "corrected_field_count": 1,
                "retained_baseline_count": 1,
                "unchanged_field_count": 1,
                "optional_exclusion_count": 1,
            },
        )

    def test_snapshot_identity_rows_are_read_only_business_fields(self):
        rows = snapshot_identity_rows(snapshot())
        labels = [row["Label"] for row in rows]
        self.assertEqual(
            labels,
            [
                "Snapshot ID",
                "Review ID",
                "Source revision",
                "Existing dataset",
                "Proposed dataset",
                "Approval actor",
                "Created",
            ],
        )
        self.assertTrue(
            all(set(row) == {"Label", "Value"} for row in rows)
        )

    def test_page_requires_confirmation_and_disables_incomplete_creation(self):
        source = Path("pages/25_specification_review.py").read_text(
            encoding="utf-8"
        )
        self.assertIn("st.checkbox(", source)
        self.assertIn(
            "not actor.strip() or not reason.strip() or not confirmed",
            source,
        )
        self.assertIn(
            "Create immutable approved specification snapshot",
            source,
        )

    def test_page_renders_hash_only_inside_collapsed_audit_section(self):
        source = Path("pages/25_specification_review.py").read_text(
            encoding="utf-8"
        )
        expander = source.index(
            'st.expander("Snapshot audit details", expanded=False)'
        )
        content_hash = source.index("snapshot.content_hash")
        self.assertGreater(content_hash, expander)
        self.assertNotIn("st.json(", source)


if __name__ == "__main__":
    unittest.main()
