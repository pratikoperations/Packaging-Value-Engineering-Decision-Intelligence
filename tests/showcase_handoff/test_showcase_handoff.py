from __future__ import annotations

import unittest

from src.showcase_handoff import ALL_PAGE_REFERENCES, AudienceRole, ShowcaseHandoffService


class ShowcaseHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ShowcaseHandoffService()

    def test_registry_contains_six_governed_journeys(self) -> None:
        self.assertEqual(6, len(self.service.list_journeys()))

    def test_five_minute_journey_respects_duration_and_transition_limits(self) -> None:
        journey = self.service.get_journey("executive-5")
        self.assertLessEqual(journey.total_duration_seconds, 330)
        self.assertLessEqual(journey.page_transitions, 6)
        self.assertEqual(AudienceRole.EXECUTIVE, journey.audience)

    def test_all_registered_pages_are_covered(self) -> None:
        covered = {step.page_reference for journey in self.service.list_journeys() for step in journey.steps}
        self.assertTrue(set(ALL_PAGE_REFERENCES).issubset(covered))

    def test_every_step_separates_evidence_and_claim_limit(self) -> None:
        for journey in self.service.list_journeys():
            for step in journey.steps:
                self.assertTrue(step.evidence_to_show)
                self.assertTrue(step.avoid_claiming)

    def test_exports_are_deterministic(self) -> None:
        journey = self.service.get_journey("executive-5")
        self.assertEqual(journey.canonical_json(), journey.canonical_json())
        self.assertEqual(self.service.export_markdown(journey.journey_id), self.service.export_markdown(journey.journey_id))
        self.assertNotIn("generated_at", journey.canonical_json())

    def test_audience_filter_is_controlled(self) -> None:
        journeys = self.service.list_journeys(AudienceRole.PACKAGING)
        self.assertEqual(1, len(journeys))
        self.assertEqual("packaging", journeys[0].journey_id)

    def test_unknown_journey_fails_closed(self) -> None:
        with self.assertRaises(KeyError):
            self.service.get_journey("unrestricted")

    def test_handoff_checklist_contains_exact_test_command(self) -> None:
        checklist = self.service.handoff_checklist()
        self.assertIn('python -m unittest discover -s tests -p "test_*.py"', checklist.test_commands)
        self.assertIn("synthetic", " ".join(checklist.data_boundary_checks).lower())


if __name__ == "__main__":
    unittest.main()
