from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from src.sourcemate.repository_context import SourceMateRepositoryContextProvider
from src.ui.sourcemate_ui import render_sourcemate_page

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = Path(os.environ.get("PVE_DATABASE_PATH", ROOT / "data" / "pve.sqlite3"))

st.set_page_config(page_title="SourceMate", page_icon="🔎", layout="wide")

try:
    contexts = SourceMateRepositoryContextProvider(DATABASE_PATH).list_contexts()
except Exception:
    st.error(
        "Governed SourceMate records could not be loaded safely. "
        "No explanation has been generated and no record was changed."
    )
    contexts = ()

render_sourcemate_page(st, contexts=contexts)
