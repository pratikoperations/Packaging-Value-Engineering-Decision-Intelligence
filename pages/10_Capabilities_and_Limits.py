from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Capabilities & Limits", layout="wide")
st.title("Capabilities & Limits")
st.caption("Controlled portfolio demonstration boundaries for Packaging Value Engineering Decision Intelligence.")

left, right = st.columns(2)
with left:
    st.subheader("What this application supports")
    st.markdown(
        """
- Task-based navigation across project, upload, rules, scenarios and decisions.
- Structured project-data upload through XLSX, JSON and the governed two-file CSV contract.
- Automatic detection of XLSX, CSV, JSON, DOCX and searchable PDF.
- Specification comparison for PDF/PDF, DOCX/DOCX, PDF/DOCX and DOCX/PDF.
- Exactly one Existing and one Proposed specification.
- Source-grounded deterministic extraction against the governed 25-field registry.
- Human review with Confirm, Correct and Confirm, Intentionally Omit, Reject and Pending states.
- Confirmed-only canonical draft generation and unchanged canonical validation.
- Append-only, content-addressed unified specification snapshots.
"""
    )

with right:
    st.subheader("What this application does not support")
    st.markdown(
        """
- OCR, scanned or image-only PDF interpretation.
- Engineering drawing, chart, diagram or embedded-image interpretation.
- Encrypted or malformed PDF processing.
- Live AI-provider execution or autonomous semantic extraction.
- Autonomous packaging approval, supplier award or commercial commitment.
- Automatic cost, risk, qualification or sustainability evidence creation.
- Production ERP, PLM, laboratory or supplier-system integration.
- Replacement of engineering validation, procurement governance or human approval.
"""
    )

st.subheader("Governance boundary")
st.info(
    "The application records controlled evidence and produces deterministic decision-support outputs. "
    "It does not prove production readiness, technical qualification, supplier acceptance, regulatory compliance or realized business impact."
)

st.subheader("Data policy")
st.warning(
    "Use synthetic or sanitized demonstration content only. Do not upload confidential supplier, customer, employee, pricing or production documents."
)

st.subheader("Evidence interpretation")
st.markdown(
    """
**The application proves:** governed workflow design, deterministic validation, source traceability, human-review controls, mixed-format document handling and append-only evidence preservation.

**The application does not prove:** model accuracy on arbitrary documents, OCR performance, production-scale throughput, integration resilience, cybersecurity certification or quantified savings realization.
"""
)
