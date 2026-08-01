from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.calculation_evidence import IndependentCalculationEvidenceService
from src.calculation_evidence.repository_context import CalculationEvidenceRepositoryContext
from src.scenario_engine import ScenarioInputs, evaluate_scenario
from src.synthetic_data import build_legacy_dataset, load_governed_package
from src.ui.calculation_evidence_ui import (
    render_calculation_evidence_page,
    render_independent_reconciliation,
)

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.environ.get("PVE_DATABASE_PATH", ROOT / "data" / "pve.sqlite3"))
GOVERNED_DEMO_PATH = ROOT / "data" / "demo" / "governed_synthetic"

st.set_page_config(page_title="Calculation Evidence", page_icon="🧮", layout="wide")

try:
    context = CalculationEvidenceRepositoryContext(DATABASE_PATH)
    projects = context.list_projects()
except Exception:
    st.error(
        "Governed persisted calculation records could not be loaded safely. "
        "No record was changed. The independent synthetic reconciliation remains available below."
    )
    context = None
    projects = ()

if context is not None:
    render_calculation_evidence_page(st, projects=projects, context=context)
else:
    st.title("Calculation Evidence")

try:
    governed_package = load_governed_package(GOVERNED_DEMO_PATH)
    scenario_options = {item["scenario_id"]: item["title"] for item in governed_package["scenarios"]}
    selected_scenario_id = st.selectbox(
        "Independent synthetic scenario",
        tuple(scenario_options),
        format_func=lambda value: scenario_options[value],
        key="calculation-evidence-governed-scenario",
    )
    dataset = build_legacy_dataset(governed_package, selected_scenario_id)
    alternative_ids = [item["alternative_id"] for item in dataset["packaging_alternatives"]]
    zero_adjustments = {alternative_id: 0.0 for alternative_id in alternative_ids}
    scenario = evaluate_scenario(
        dataset,
        ScenarioInputs(
            annual_volume=float(dataset["packaging_project"]["annual_volume"]),
            cost_adjustment_percent_by_alternative=zero_adjustments,
            material_adjustment_percent_by_alternative=zero_adjustments,
        ),
    )
    independent_evidence = IndependentCalculationEvidenceService().evaluate(
        dataset=dataset,
        scenario_id=selected_scenario_id,
        scenario_result=scenario,
        cost_adjustments=zero_adjustments,
        material_adjustments=zero_adjustments,
    )
except Exception as exc:
    st.error(
        "Independent synthetic calculation evidence could not be generated safely. "
        f"No primary result was changed. Diagnostic: {type(exc).__name__}."
    )
else:
    render_independent_reconciliation(st, independent_evidence)
