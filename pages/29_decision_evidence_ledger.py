from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.evidence_ledger import EvidenceLedgerRepositoryContext, EvidenceLedgerService
from src.ui.evidence_ledger_ui import render_evidence_ledger_page

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.environ.get("PVE_DATABASE_PATH", ROOT / "data" / "pve.sqlite3"))

st.set_page_config(page_title="Decision Evidence Ledger", page_icon="🧾", layout="wide")

try:
    context = EvidenceLedgerRepositoryContext(DATABASE_PATH)
    projects = context.list_projects()
    service = EvidenceLedgerService(context)
except Exception:
    st.error(
        "Governed project evidence could not be loaded safely. "
        "No ledger was generated and no source record was changed."
    )
    context = None
    projects = ()

if context is not None:
    render_evidence_ledger_page(st, projects=projects, service=service)
