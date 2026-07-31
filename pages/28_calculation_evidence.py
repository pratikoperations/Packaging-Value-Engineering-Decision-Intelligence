from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.calculation_evidence.repository_context import CalculationEvidenceRepositoryContext
from src.ui.calculation_evidence_ui import render_calculation_evidence_page

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.environ.get("PVE_DATABASE_PATH", ROOT / "data" / "pve.sqlite3"))

st.set_page_config(page_title="Calculation Evidence", page_icon="🧮", layout="wide")

try:
    context = CalculationEvidenceRepositoryContext(DATABASE_PATH)
    projects = context.list_projects()
except Exception:
    st.error(
        "Governed calculation records could not be loaded safely. "
        "No evidence has been generated and no record was changed."
    )
    context = None
    projects = ()

if context is not None:
    render_calculation_evidence_page(st, projects=projects, context=context)
