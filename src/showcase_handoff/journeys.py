from __future__ import annotations

from .domain import AudienceRole, ShowcaseJourney, ShowcaseStep

ALL_PAGE_REFERENCES = (
    "Home", "Showcase & Handoff", "Project Dashboard", "Guided Workflow",
    "Specification Review", "Data Upload", "Business Rules & Thresholds",
    "Scenario Analysis", "Decision Records", "SourceMate",
    "Calculation Evidence", "Decision Evidence Ledger", "Capabilities & Limits",
)


def _step(number: int, page: str, title: str, message: str, seconds: int, evidence: str, limit: str) -> ShowcaseStep:
    return ShowcaseStep(
        number,
        page,
        title,
        f"Use {page} to {title.lower()}.",
        message,
        (evidence,),
        (limit,),
        seconds,
        fallback_step="Capabilities & Limits",
    )


def _journey(journey_id: str, title: str, audience: AudienceRole, minutes: int, pages: tuple[str, ...]) -> ShowcaseJourney:
    messages = {
        "Home": ("Frame the opportunity", "This synthetic case shows packaging value engineering with explicit commercial, technical and governance boundaries.", "Synthetic-data warning and business objective.", "Do not present outputs as validated supplier or production data."),
        "Project Dashboard": ("Orient the project", "The dashboard shows the governed project state, blockers and the next controlled action.", "Project state and unresolved controls.", "Do not call project status an approval."),
        "Guided Workflow": ("Show the controlled process", "The workflow separates intake, review, analysis, evidence and decision records.", "Ordered governed stages.", "Do not imply autonomous workflow execution."),
        "Specification Review": ("Show data quality", "Specification differences and unresolved evidence are governed before analysis.", "Review revisions, blockers and pending fields.", "Do not treat review eligibility as engineering approval."),
        "Data Upload": ("Explain intake boundaries", "Data intake is classified and remains subject to validation.", "Source classification and validation state.", "Do not claim enterprise integration or verified supplier data."),
        "Business Rules & Thresholds": ("Explain transparent controls", "Rules and thresholds are explicit rather than hidden in an opaque model.", "Governed rule and threshold references.", "Do not claim these defaults fit every business."),
        "Scenario Analysis": ("Show the business result", "The scenario compares cost, material, qualification and risk using deterministic logic.", "Cost, material, qualification, risk and recommendation.", "Do not present potential savings as realized savings."),
        "Decision Records": ("Show persistence", "Decision records preserve the reviewed outcome and its limitations.", "Decision status, rationale and validation requirements.", "Do not present a decision record as supplier award or approval."),
        "SourceMate": ("Explain why", "SourceMate answers controlled questions about why a governed status or outcome exists.", "A predefined supported explanation.", "Do not describe SourceMate as an unrestricted chatbot or decision maker."),
        "Calculation Evidence": ("Explain how", "Calculation Evidence traces a supported stored numeric result through assumptions, units and rounding.", "One stored annual-cost, savings or material result.", "Do not claim it recalculates or changes stored results."),
        "Decision Evidence Ledger": ("Prove lineage", "The ledger shows chronology, revisions, hashes, blockers and pending validation.", "Record lineage and integrity state.", "Do not call the projection a new audit event or approval log."),
        "Capabilities & Limits": ("Close with governance", "The system supports transparent decisions while human engineering and commercial approval remain mandatory.", "Formal capabilities and exclusions.", "Do not claim production readiness, autonomous approval or supplier allocation."),
        "Showcase & Handoff": ("Select the governed route", "This hub provides a timed route, proof statements and claim limits without duplicating business logic.", "Journey duration and audience.", "Do not call the hub a second dashboard or analytical engine."),
    }
    seconds = max(35, min(90, (minutes * 60) // len(pages)))
    steps = tuple(
        _step(i, page, messages[page][0], messages[page][1], seconds, messages[page][2], messages[page][3])
        for i, page in enumerate(pages, 1)
    )
    return ShowcaseJourney(
        journey_id,
        title,
        audience,
        minutes,
        "Explain the governed business decision clearly, quickly and without unsupported claims.",
        "Start with the packaging business problem and disclose that the demonstration data is synthetic.",
        "Close by separating decision support from human approval, validation and value realization.",
        steps,
        ("The application demonstrates deterministic calculations, governed evidence and reproducible decision support.", "SourceMate, Calculation Evidence and the Evidence Ledger provide distinct explanation layers."),
        ("The application does not prove production readiness, realized savings, supplier award or autonomous approval.", "Engineering trials, commercial review and enterprise controls remain outside this showcase."),
        ("Return to Home and confirm the synthetic dataset.", "Open Capabilities & Limits if a page is unavailable.", "Run python -m unittest discover -s tests -p 'test_*.py'."),
    )


def build_journeys() -> tuple[ShowcaseJourney, ...]:
    return (
        _journey("executive-5", "Five-minute executive interview", AudienceRole.EXECUTIVE, 5, ("Home", "Project Dashboard", "Scenario Analysis", "SourceMate", "Calculation Evidence", "Decision Evidence Ledger", "Capabilities & Limits")),
        _journey("detailed-10", "Ten-minute detailed demonstration", AudienceRole.EXECUTIVE, 10, ("Home", "Guided Workflow", "Specification Review", "Data Upload", "Business Rules & Thresholds", "Scenario Analysis", "Decision Records", "SourceMate", "Calculation Evidence", "Decision Evidence Ledger", "Capabilities & Limits")),
        _journey("procurement", "Procurement-leader walkthrough", AudienceRole.PROCUREMENT, 8, ("Project Dashboard", "Scenario Analysis", "Decision Records", "SourceMate", "Calculation Evidence", "Decision Evidence Ledger", "Capabilities & Limits")),
        _journey("packaging", "Packaging-technical walkthrough", AudienceRole.PACKAGING, 8, ("Guided Workflow", "Specification Review", "Data Upload", "Business Rules & Thresholds", "Scenario Analysis", "Calculation Evidence", "Decision Evidence Ledger", "Capabilities & Limits")),
        _journey("governance", "Technical and governance walkthrough", AudienceRole.GOVERNANCE, 8, ("Guided Workflow", "Decision Records", "SourceMate", "Calculation Evidence", "Decision Evidence Ledger", "Capabilities & Limits")),
        _journey("handoff", "New-user handoff", AudienceRole.HANDOFF, 10, ("Showcase & Handoff", "Home", "Project Dashboard", "Guided Workflow", "Decision Records", "Capabilities & Limits")),
    )
