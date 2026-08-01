from __future__ import annotations

from pathlib import Path

from src.showcase_handoff import AudienceRole, ShowcaseHandoffService


ROOT = Path(__file__).resolve().parents[2]
PAGE_REGISTRY_SESSION_KEY = "_pve_page_registry"
PAGE_TOKENS = (
    ("Showcase & Handoff", "showcase_handoff"),
    ("Project Dashboard", "project_dashboard"),
    ("Guided Workflow", "guided_workflow"),
    ("Specification Review", "specification_review"),
    ("Data Upload", "data_upload"),
    ("Business Rules & Thresholds", "business_thresholds"),
    ("Scenario Analysis", "controlled_scenarios"),
    ("Decision Records", "decision_history"),
    ("SourceMate", "sourcemate"),
    ("Calculation Evidence", "calculation_evidence"),
    ("Decision Evidence Ledger", "decision_evidence_ledger"),
    ("Capabilities & Limits", "capabilities_and_limits"),
)


def _build_page_paths() -> dict[str, str]:
    paths: dict[str, str] = {"Home": "app.py"}
    page_files = tuple(sorted((ROOT / "pages").glob("*.py")))
    for title, token in PAGE_TOKENS:
        matches = [path for path in page_files if token in path.stem.lower()]
        if len(matches) == 1:
            paths[title] = matches[0].relative_to(ROOT).as_posix()
    return paths


PAGE_PATHS = _build_page_paths()

LIVE_DEMO_RECOVERY = (
    "Refresh the browser if the current page stops responding.",
    "Return to Home and reopen Showcase & Handoff.",
    "Select the five-minute executive journey and use the designated synthetic demonstration project.",
    "Skip optional drill-downs if time is limited.",
    "Close on Capabilities & Limits so governance boundaries remain explicit.",
)


def render_showcase_handoff_page(st, service: ShowcaseHandoffService) -> None:
    st.title("Showcase and Handoff Hub")
    st.caption("Deterministic interview journeys, proof boundaries and new-user recovery guidance")
    st.warning(
        "Synthetic demonstration data must be disclosed before presenting any result. "
        "This hub does not calculate, approve or persist business records."
    )

    audiences = list(AudienceRole)
    audience = st.selectbox("Audience", audiences, format_func=lambda value: value.value)
    journeys = service.list_journeys(audience)
    if not journeys:
        st.info("No governed journey is available for this audience.")
        return

    journey = st.selectbox("Journey", journeys, format_func=lambda value: value.title)
    summary_columns = st.columns(2)
    with summary_columns[0]:
        st.metric("Target duration", f"{journey.target_duration_minutes} min")
    with summary_columns[1]:
        st.metric("Governed steps", len(journey.steps))

    st.write("**Business objective**")
    st.write(journey.business_objective)
    st.info(journey.opening_statement)

    page_registry = getattr(st, "session_state", {}).get(PAGE_REGISTRY_SESSION_KEY, {})
    for step in journey.steps:
        label = (
            f"{step.step_number}. {step.title} — "
            f"{step.page_reference} ({step.expected_duration_seconds}s)"
        )
        with st.expander(label):
            st.write(step.speaker_message)
            st.write("**Evidence to show**")
            for item in step.evidence_to_show:
                st.write(f"- {item}")
            st.write("**Do not claim**")
            for item in step.avoid_claiming:
                st.write(f"- {item}")
            target_page = page_registry.get(step.page_reference)
            if target_page is not None:
                st.page_link(target_page, label=f"Open {step.page_reference}", width="stretch")

    st.subheader("What this proves")
    for item in journey.proof_statements:
        st.write(f"- {item}")

    st.subheader("What this does not prove")
    for item in journey.limitation_statements:
        st.write(f"- {item}")

    st.success(journey.closing_statement)

    st.download_button(
        "Download governed journey (Markdown)",
        data=service.export_markdown(journey.journey_id),
        file_name=f"{journey.journey_id}.md",
        mime="text/markdown",
        width="stretch",
    )
    st.download_button(
        "Download governed journey (JSON)",
        data=journey.canonical_json(),
        file_name=f"{journey.journey_id}.json",
        mime="application/json",
        width="stretch",
    )

    with st.expander("Live-demo recovery", expanded=False):
        st.write(
            "Use this short recovery path during an interview or executive review. "
            "It does not replace technical diagnosis."
        )
        for item in LIVE_DEMO_RECOVERY:
            st.write(f"- {item}")

    checklist = service.handoff_checklist()
    with st.expander("New-user handoff checklist"):
        for heading, items in (
            ("Environment", checklist.environment_checks),
            ("Repository", checklist.repository_checks),
            ("Data boundaries", checklist.data_boundary_checks),
            ("Workflow", checklist.workflow_checks),
            ("Tests", checklist.test_commands),
            ("Known limitations", checklist.known_limitations),
            ("Technical recovery", checklist.recovery_guidance),
        ):
            st.write(f"**{heading}**")
            for item in items:
                st.write(f"- {item}")
