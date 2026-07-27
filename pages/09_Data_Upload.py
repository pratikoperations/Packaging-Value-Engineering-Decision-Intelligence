from __future__ import annotations

from dataclasses import asdict

import streamlit as st

from src.upload_routing import DetectionStatus, detect_upload


st.set_page_config(page_title="Data Upload", layout="wide")
st.title("Data Upload")
st.caption("Upload project data or packaging specifications. File type and intended workflow are detected automatically.")
st.info(
    "Build U1 provides detection, validation and routing preview only. "
    "Structured, Word and PDF processing are not invoked yet."
)

uploaded_files = st.file_uploader(
    "Upload files",
    type=["xlsx", "csv", "json", "docx", "pdf"],
    accept_multiple_files=True,
    help="Supported: XLSX, CSV, JSON, DOCX and searchable PDF.",
)

if uploaded_files:
    detections = [
        detect_upload(upload.name, upload.type, upload.getvalue())
        for upload in uploaded_files
    ]
    rows = []
    for detection in detections:
        rows.append(
            {
                "File": detection.filename,
                "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected",
                "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None",
                "Status": detection.status.value.replace("_", " ").title(),
                "Role confirmation": "Required" if detection.requires_document_role else "Not required",
                "Reason": detection.reason_code or "",
            }
        )
    st.subheader("Detection and routing preview")
    st.dataframe(rows, width="stretch", hide_index=True)

    rejected = [item for item in detections if item.status is DetectionStatus.REJECTED]
    if rejected:
        for item in rejected:
            st.error(f"{item.filename}: {item.detail or item.reason_code}")
    else:
        specification_count = sum(item.requires_document_role for item in detections)
        if specification_count:
            st.warning(
                "Specification documents require one Existing and one Proposed role. "
                "Role assignment and workflow execution will be added in the next approved build."
            )
        st.success("All uploaded files passed Build U1 detection and structural eligibility checks.")
else:
    st.write("No files uploaded.")

with st.expander("Build U1 scope and limitations"):
    st.write("- Automatic extension, MIME, signature and structural detection")
    st.write("- Searchable-PDF eligibility check; no OCR")
    st.write("- Format-neutral specification contract")
    st.write("- Mixed-pair classification for PDF/PDF, DOCX/DOCX, PDF/DOCX and DOCX/PDF")
    st.write("- No structured, Word or PDF processing invoked in this build")
