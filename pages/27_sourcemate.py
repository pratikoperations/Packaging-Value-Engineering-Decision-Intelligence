from __future__ import annotations

import streamlit as st

from src.ui.sourcemate_ui import render_sourcemate_page


st.set_page_config(page_title="SourceMate", page_icon="🔎", layout="wide")
render_sourcemate_page(st, contexts=st.session_state.get("sourcemate_contexts", ()))
