from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.application.runtime import build_project_service, build_upload_service
from src.application.structured_upload import (
    STRUCTURED_CONFIRMATION_KEY,
    StructuredUploadFile,
    invalidate_structured_state_on_change,
    prepare_structured_upload,
    validate_structured_batch,
)
from src.upload_routing import DetectionStatus, WorkflowKind, detect_upload
from src.uploads import DuplicateDatasetError, UploadParseError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"


@st.cache_resource
def services():
    return build_project_service(DATABASE_PATH), build_upload_service(DATABASE_PATH)


def issue_rows(prepared):
    return [{"Code": issue.code, "Path": issue.path, "Message": issue.message} for issue in prepared.validation.issues]


def render_prepared_upload(upload_service, project, prepared):
    if prepared.validation.is_valid:
        st.success("Validation passed. This canonical dataset is eligible for immutable storage.")
    else:
        st.error("Validation failed. Correct all reported issues before saving a dataset version.")
        st.dataframe(issue_rows(prepared), width="stretch", hide_index=True)
    if prepared.validation.insufficient_data_eligible:
        st.warning("The dataset remains eligible for an insufficient-data outcome. Technical evidence and human approval controls still apply.")
    with st.expander("Canonical normalized dataset"):
        st.json(prepared.canonical_data)
    if st.button("Save immutable dataset version", disabled=not prepared.validation.is_valid, width="stretch", key=f"save-{prepared.source_type}-{prepared.original_filename}"):
        try:
            saved = upload_service.save_valid_dataset(project_id=project["project_id"], prepared=prepared)
            st.success(f"Dataset version {saved['version_number']} saved.")
            st.rerun()
        except DuplicateDatasetError as error:
            st.warning(str(error))
        except ValueError as error:
            st.error(str(error))


st.set_page_config(page_title="Data Upload", layout="wide")
st.title("Data Upload")
st.caption("Upload project data or packaging specifications. File type and intended workflow are detected automatically.")
st.info(
    "Structured XLSX, CSV and JSON files can now enter the existing governed validation workflow. "
    "DOCX and PDF processing remain inactive in Build U2."
)

uploaded_files = st.file_uploader(
    "Upload files",
    type=["xlsx", "csv", "json", "docx", "pdf"],
    accept_multiple_files=True,
    help="Supported: XLSX, CSV, JSON, DOCX and searchable PDF.",
)

if uploaded_files:
    detections = [detect_upload(upload.name, upload.type, upload.getvalue()) for upload in uploaded_files]
    rows = [
        {
            "File": detection.filename,
            "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected",
            "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None",
            "Status": detection.status.value.replace("_", " ").title(),
            "Role confirmation": "Required" if detection.requires_document_role else "Not required",
            "Reason": detection.reason_code or "",
        }
        for detection in detections
    ]
    st.subheader("Detection and routing")
    st.dataframe(rows, width="stretch", hide_index=True)

    rejected = [item for item in detections if item.status is DetectionStatus.REJECTED]
    if rejected:
        for item in rejected:
            st.error(f"{item.filename}: {item.detail or item.reason_code}")
    else:
        structured_files = [
            StructuredUploadFile(upload.name, upload.getvalue(), detection)
            for upload, detection in zip(uploaded_files, detections)
            if detection.workflow is WorkflowKind.STRUCTURED_PROJECT_DATA
        ]
        specification_count = sum(item.requires_document_role for item in detections)

        if structured_files and specification_count:
            st.warning("This batch contains project data and specification documents. Process one workflow group at a time.")
        elif specification_count:
            st.warning(
                "Specification documents require one Existing and one Proposed role. "
                "DOCX and PDF workflow execution remains inactive in Build U2."
            )
        elif structured_files:
            invalidate_structured_state_on_change(st.session_state, structured_files)
            try:
                detected_format = validate_structured_batch(structured_files)
                st.success(f"Detected structured project-data workflow: {detected_format.value.upper()}.")
                confirmed = st.checkbox(
                    "Confirm that these files should be processed as structured project data",
                    key=STRUCTURED_CONFIRMATION_KEY,
                )
                if confirmed:
                    project_service, upload_service = services()
                    active_project_id = st.session_state.get("active_project_id")
                    if not active_project_id:
                        st.info("Select an active workspace from the Project Dashboard before validating project data.")
                    else:
                        try:
                            project = project_service.get_project(str(active_project_id))
                        except KeyError:
                            st.session_state.pop("active_project_id", None)
                            st.error("The active project no longer exists.")
                        else:
                            if project["archived_at"] is not None:
                                st.error("Archived projects are read-only and cannot receive new uploads.")
                            else:
                                st.success(f"Active project: {project['project_code']} — {project['project_name']}")
                                try:
                                    prepared = prepare_structured_upload(upload_service, project, structured_files)
                                    render_prepared_upload(upload_service, project, prepared)
                                except UploadParseError as error:
                                    st.error(str(error))
            except UploadParseError as error:
                st.error(str(error))
        else:
            st.success("All uploaded files passed detection checks.")
else:
    st.write("No files uploaded.")

with st.expander("Build U2 scope and limitations"):
    st.write("- Automatic extension, MIME, signature and structural detection")
    st.write("- XLSX, CSV and JSON reuse the existing structured validation and immutable-save workflow")
    st.write("- Structured upload confirmation is required before processing")
    st.write("- Upload changes invalidate structured confirmation and prepared state")
    st.write("- Searchable-PDF eligibility check; no OCR")
    st.write("- Mixed-pair classification for PDF/PDF, DOCX/DOCX, PDF/DOCX and DOCX/PDF")
    st.write("- DOCX and PDF processing are not invoked in this build")
