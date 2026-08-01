from __future__ import annotations

import json
from typing import Any, Iterable

from src.calculation_evidence.domain import CalculationEvidenceError
from src.calculation_evidence.service import CalculationEvidenceService


RESULT_LABELS = {
    "annual_cost": "Annual cost",
    "annual_savings_vs_baseline": "Annual savings versus baseline",
    "annual_material_kg": "Annual material",
    "material_change_percent_vs_baseline": "Material change versus baseline",
}


def render_calculation_evidence_page(st, *, projects: Iterable[dict[str, Any]], context) -> None:
    service = CalculationEvidenceService()
    available_projects = tuple(projects)
    st.title("Calculation Evidence")
    st.caption(
        "Read-only reconstruction of existing governed scenario results. "
        "This page does not run, modify, or replace any analytical engine."
    )
    if not available_projects:
        st.info("No governed projects are available for legacy persisted calculation evidence.")
        _limitations(st)
        return

    project_by_label = {
        f"{item.get('project_code', item['project_id'])} — {item.get('project_name', '')}": item
        for item in available_projects
    }
    project = project_by_label[st.selectbox("Project", sorted(project_by_label))]
    scenarios = context.list_scenarios(project["project_id"])
    if not scenarios:
        st.info("No persisted governed scenarios are available for this project.")
        _limitations(st)
        return
    scenario_by_label = {
        f"{item.get('scenario_name', item['scenario_id'])} — {item['scenario_id']}": item
        for item in scenarios
    }
    scenario = scenario_by_label[st.selectbox("Scenario", sorted(scenario_by_label))]
    try:
        results = json.loads(scenario["results_json"])
        alternatives = results.get("alternatives", {})
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        st.error("The selected scenario result payload cannot be read safely.")
        _limitations(st)
        return
    if not alternatives:
        st.info("The selected scenario has no supported alternative results.")
        _limitations(st)
        return
    alternative_id = st.selectbox("Alternative", sorted(alternatives))
    result_name = st.selectbox(
        "Stored result",
        sorted(service.SUPPORTED_RESULTS),
        format_func=lambda value: RESULT_LABELS[value],
    )
    if st.button("Show governed calculation evidence", type="primary"):
        try:
            selected, archived = context.get_scenario(project["project_id"], scenario["scenario_id"])
            evidence = service.build_for_scenario(
                project_id=project["project_id"],
                scenario=selected,
                alternative_id=alternative_id,
                result_name=result_name,
                archived=archived,
            )
        except CalculationEvidenceError as exc:
            st.error(f"{exc.code}: {exc.message}")
        else:
            st.subheader("Recorded result")
            st.metric(RESULT_LABELS[result_name], f"{evidence.result_value:g} {evidence.result_unit}")
            if evidence.archived:
                st.warning("Archived project record — read-only evidence only.")
            with st.expander("Assumptions", expanded=True):
                st.write([item.canonical() for item in evidence.assumptions])
            with st.expander("Formula and intermediate steps", expanded=True):
                st.write([item.canonical() for item in evidence.steps])
            with st.expander("Units, evidence gaps and validation"):
                st.write({
                    "unit_conversions": list(evidence.unit_conversions),
                    "evidence_gaps": list(evidence.evidence_gaps),
                    "validation_requirements": list(evidence.validation_requirements),
                })
            with st.expander("Lineage and limitations"):
                st.write({
                    "source_hash": evidence.source_hash,
                    "revision_reference": evidence.revision_reference,
                    "claim_limitations": list(evidence.claim_limitations),
                })
            st.download_button(
                "Export canonical JSON",
                data=service.canonical_json(evidence),
                file_name=f"calculation-evidence-{scenario['scenario_id']}-{alternative_id}-{result_name}.json",
                mime="application/json",
            )
    _limitations(st)


def render_independent_reconciliation(st, evidence: dict[str, Any]) -> None:
    st.divider()
    st.subheader("Independent Decimal Reconciliation")
    st.warning(evidence["disclosure"])
    st.caption(
        "The evidence engine independently maps raw inputs, applies its own versioned Decimal formulas, "
        "and only then compares results with the primary engine."
    )
    summary = evidence["summary"]
    columns = st.columns(5)
    for column, key, label in zip(
        columns,
        ("matched", "matched_within_tolerance", "mismatch", "insufficient_evidence", "unsupported"),
        ("Matched", "Within tolerance", "Mismatch", "Insufficient", "Unsupported"),
    ):
        column.metric(label, summary[key])
    state_filter = st.selectbox(
        "Reconciliation state",
        ("all", "matched", "matched_within_tolerance", "mismatch", "insufficient_evidence", "unsupported"),
        key="independent-calculation-state-filter",
    )
    rows = evidence["results"]
    if state_filter != "all":
        rows = [item for item in rows if item["state"] == state_filter]
    st.dataframe(
        [
            {
                "Calculation": item["calculation_id"],
                "Alternative": item["alternative_id"],
                "Primary": item["primary_result"],
                "Independent": item["independent_result"],
                "Unit": item["unit"],
                "Absolute variance": item["absolute_variance"],
                "Tolerance": item["allowed_variance"],
                "State": item["state"],
            }
            for item in rows
        ],
        width="stretch",
        hide_index=True,
    )
    with st.expander("Formula, assumption and rule lineage"):
        st.write(
            {
                "registry_version": evidence["registry_version"],
                "numeric_formula_count": evidence["catalogue_count"],
                "assumptions": evidence["assumptions"],
                "rule_lineage": evidence["rule_lineage"],
            }
        )
    with st.expander("Raw-input lineage and limitations"):
        st.write(rows)


def _limitations(st) -> None:
    with st.expander("Capabilities and limitations"):
        st.markdown(
            "- Read-only evidence for existing governed scenario outputs.\n"
            "- Independent Decimal recalculation is available for the governed synthetic scenarios.\n"
            "- No editable formulas, thresholds, unrestricted expressions, approval, supplier ranking, allocation, or award.\n"
            "- A reconciliation match is not supplier, engineering, regulatory, production or realized-savings validation.\n"
            "- Engineering validation and explicit human approval remain mandatory."
        )
