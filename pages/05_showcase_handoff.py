from __future__ import annotations

import streamlit as st

from src.showcase_handoff import ShowcaseHandoffService
from src.ui.showcase_handoff_ui import render_showcase_handoff_page

st.set_page_config(page_title="Showcase and Handoff", page_icon="🧭", layout="wide")

try:
    service = ShowcaseHandoffService()
except Exception:
    st.error("The governed showcase registry could not be loaded safely. No business record was read or changed.")
else:
    render_showcase_handoff_page(st, service)
