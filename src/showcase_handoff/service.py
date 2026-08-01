from __future__ import annotations

from .domain import AudienceRole, HandoffChecklist, ShowcaseJourney
from .journeys import ALL_PAGE_REFERENCES, build_journeys


class ShowcaseHandoffService:
    def __init__(self) -> None:
        self._journeys = build_journeys()
        self._validate_registry()

    def list_journeys(self, audience: AudienceRole | None = None) -> tuple[ShowcaseJourney, ...]:
        journeys = self._journeys
        if audience is not None:
            journeys = tuple(item for item in journeys if item.audience is audience)
        return journeys

    def get_journey(self, journey_id: str) -> ShowcaseJourney:
        for journey in self._journeys:
            if journey.journey_id == journey_id:
                return journey
        raise KeyError(f"Unsupported showcase journey: {journey_id}")

    def handoff_checklist(self) -> HandoffChecklist:
        return HandoffChecklist(
            environment_checks=("Use Python 3.12.", "Install requirements.txt.", "Start with streamlit run app.py."),
            repository_checks=("Confirm the governed repository and exact commit.", "Keep main unchanged unless separately authorized."),
            data_boundary_checks=("Disclose synthetic demonstration data before discussing results.", "Do not represent uploads as validated enterprise integrations."),
            workflow_checks=("Select one project.", "Review blockers and pending validation.", "Use SourceMate, Calculation Evidence and the Evidence Ledger only for their defined purposes."),
            test_commands=("python -m unittest discover -s tests -p \"test_*.py\"",),
            known_limitations=("No autonomous approval, supplier allocation or realized-savings tracking.", "No production deployment, authentication or enterprise integration is proven."),
            recovery_guidance=("Return to Home.", "Confirm the synthetic dataset is unchanged.", "Run the complete test suite and restart Streamlit."),
        )

    def export_markdown(self, journey_id: str) -> str:
        journey = self.get_journey(journey_id)
        lines = [f"# {journey.title}", "", f"Audience: {journey.audience.value}", f"Target duration: {journey.target_duration_minutes} minutes", "", f"## Business objective\n{journey.business_objective}", "", "## Steps"]
        for step in journey.steps:
            lines.extend(("", f"### {step.step_number}. {step.title} — {step.page_reference}", f"Time: {step.expected_duration_seconds} seconds", step.speaker_message, "", "Evidence to show:", *[f"- {item}" for item in step.evidence_to_show], "", "Do not claim:", *[f"- {item}" for item in step.avoid_claiming]))
        lines.extend(("", "## What this proves", *[f"- {item}" for item in journey.proof_statements], "", "## What this does not prove", *[f"- {item}" for item in journey.limitation_statements]))
        return "\n".join(lines).strip() + "\n"

    def _validate_registry(self) -> None:
        ids = [item.journey_id for item in self._journeys]
        if len(ids) != len(set(ids)):
            raise ValueError("Showcase journey identifiers must be unique.")
        pages = {step.page_reference for journey in self._journeys for step in journey.steps}
        unsupported = pages.difference(ALL_PAGE_REFERENCES)
        if unsupported:
            raise ValueError(f"Unsupported page references: {sorted(unsupported)}")
        executive = self.get_journey("executive-5")
        if executive.total_duration_seconds > 330 or executive.page_transitions > 6:
            raise ValueError("The five-minute journey exceeds its duration or transition limit.")
