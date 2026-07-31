from __future__ import annotations

import unittest
from dataclasses import dataclass
from types import SimpleNamespace

from src.sourcemate.repository_context import SourceMateRepositoryContextProvider


@dataclass(frozen=True)
class Value:
    field_key: str
    value: object
    source: str


class FakeProjects:
    def list(self, *, archived=None):
        return [
            {"project_id": "p-active", "archived_at": None},
            {"project_id": "p-archived", "archived_at": "2026-01-01"},
        ]


class FakeDecisions:
    def list_for_project(self, project_id):
        if project_id != "p-active":
            return []
        return [{
            "decision_snapshot_id": "d-1",
            "project_id": project_id,
            "scenario_id": "s-1",
            "dataset_id": "data-1",
            "status": "blocked",
            "recommendation_json": '{"rationale":"Technical blocker overrides savings","assumptions":["volume declared"]}',
            "gate_results_json": '{"blockers":["compression evidence missing"],"required_validation":["compression test"]}',
            "content_hash": "decision-hash",
            "created_at": "2026-01-01",
        }]


class FakeReviews:
    def list_reviews_for_project(self, project_id):
        if project_id != "p-active":
            return []
        return [SimpleNamespace(review_id="r-1")]

    def list_history(self, review_id, *, project_id):
        eligibility = SimpleNamespace(eligible=False, blockers=("pending field",))
        candidate = SimpleNamespace(status="pending", field_key="gsm")
        comparison = SimpleNamespace(field_key="gsm", candidate=candidate)
        state = SimpleNamespace(
            project_id=project_id,
            existing_dataset_id="old",
            proposed_dataset_id="new",
            eligibility=eligibility,
            comparisons=(comparison,),
        )
        return [SimpleNamespace(
            review_id=review_id,
            review_revision_id="rr-1",
            revision_number=1,
            state=state,
            content_hash="review-hash",
        )]


class FakeSnapshots:
    def list_snapshots_for_project(self, project_id):
        if project_id != "p-active":
            return []
        return [SimpleNamespace(
            snapshot_id="snap-1",
            project_id=project_id,
            source_review_revision_id="rr-1",
            approved_values=(Value("gsm", 180, "accepted_proposed"),),
            content_hash="snapshot-hash",
        )]


class FakeConsumption:
    def list_envelopes_for_project(self, project_id):
        if project_id != "p-active":
            return []
        return [SimpleNamespace(
            envelope_id="env-1",
            snapshot_id="snap-1",
            source_review_revision_id="rr-1",
            approved_values=(Value("gsm", 180, "accepted_proposed"),),
            envelope_content_hash="envelope-hash",
        )]

    def list_authorizations_for_snapshot(self, snapshot_id, *, project_id):
        return [SimpleNamespace(
            envelope_id="env-1",
            purpose=SimpleNamespace(value="cost_analysis_input"),
        )]


class RepositoryContextTests(unittest.TestCase):
    def provider(self):
        provider = SourceMateRepositoryContextProvider.__new__(
            SourceMateRepositoryContextProvider
        )
        provider.projects = FakeProjects()
        provider.decisions = FakeDecisions()
        provider.reviews = FakeReviews()
        provider.snapshots = FakeSnapshots()
        provider.consumption = FakeConsumption()
        return provider

    def test_contexts_are_loaded_from_all_governed_record_families(self):
        contexts = self.provider().list_contexts()
        self.assertEqual(
            {item.target_type for item in contexts},
            {
                "decision_snapshot",
                "specification_review",
                "approved_specification_snapshot",
                "governed_consumption_envelope",
            },
        )
        self.assertTrue(all(item.source_hash for item in contexts))

    def test_decision_preserves_blocker_precedence_and_validation(self):
        context = next(
            item for item in self.provider().list_contexts()
            if item.target_type == "decision_snapshot"
        )
        self.assertIn("compression evidence missing", context.blockers)
        self.assertIn("compression test", context.required_validation)
        self.assertIn("Technical blocker overrides savings", context.status_reason)

    def test_review_honors_historical_revision_and_pending_control(self):
        context = next(
            item for item in self.provider().list_contexts()
            if item.target_type == "specification_review"
        )
        self.assertEqual(context.revision_reference, "rr-1")
        self.assertEqual(context.status, "blocked")
        self.assertTrue(context.status_improvement_requirements)

    def test_snapshot_retains_claim_limitations(self):
        context = next(
            item for item in self.provider().list_contexts()
            if item.target_type == "approved_specification_snapshot"
        )
        self.assertEqual(context.source_hash, "snapshot-hash")
        self.assertIn("does not autonomously approve", context.claim_limitations[0])

    def test_consumption_retains_non_execution_boundary(self):
        context = next(
            item for item in self.provider().list_contexts()
            if item.target_type == "governed_consumption_envelope"
        )
        self.assertEqual(context.status, "authorized_handoff")
        self.assertIn("does not execute analysis", context.claim_limitations[0])

    def test_archived_projects_remain_visible_but_read_only(self):
        provider = self.provider()
        provider.decisions = SimpleNamespace(
            list_for_project=lambda project_id: [{
                "decision_snapshot_id": "archived-d",
                "project_id": project_id,
                "scenario_id": "s",
                "dataset_id": "d",
                "status": "recorded",
                "recommendation_json": "{}",
                "gate_results_json": "{}",
                "content_hash": "h",
                "created_at": "2026-01-01",
            }] if project_id == "p-archived" else []
        )
        context = next(
            item for item in provider.list_contexts()
            if item.target_id == "archived-d"
        )
        self.assertTrue(context.archived)


if __name__ == "__main__":
    unittest.main()
