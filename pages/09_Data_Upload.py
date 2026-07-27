from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.application.runtime import build_project_service, build_upload_service
from src.application.specification_upload import (
    SpecificationUploadInput,
    parse_specification_pair,
    source_block_rows,
)
from src.application.structured_upload import (
    STRUCTURED_CONFIRMATION_KEY,
    StructuredUploadFile,
    invalidate_structured_state_on_change,
    prepare_structured_upload,
    validate_structured_batch,
)
from src.specification_intake import DocumentRole
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
    "Structured files reuse the existing governed validation workflow. "
    "DOCX and searchable PDF specifications can now be assigned roles and parsed into a common source-block contract."
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
        specification_items = [
            (upload, detection)
            for upload, detection in zip(uploaded_files, detections)
            if detection.workflow is WorkflowKind.SPECIFICATION_COMPARISON
        ]

        if structured_files and specification_items:
            st.warning("This batch contains project data and specification documents. Process one workflow group at a time.")
        elif specification_items:
            if len(specification_items) != 2:
                st.error("Exactly two specification documents are required: one Existing and one Proposed.")
            else:
                st.subheader("Specification roles")
                role_values = [DocumentRole.EXISTING.value, DocumentRole.PROPOSED.value]
                role_by_hash: dict[str, DocumentRole] = {}
                for upload, detection in specification_items:
                    selected = st.selectbox(
                        f"Role for {upload.name}",
                        role_values,
                        key=f"data_upload.role.{detection.sha256}",
                        format_func=str.title,
                    )
                    role_by_hash[detection.sha256] = DocumentRole(selected)

                roles = set(role_by_hash.values())
                if roles != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
                    st.error("Assign exactly one Existing and one Proposed specification.")
                else:
                    formats = [detection.file_format.value.upper() for _, detection in specification_items]
                    st.success(f"Specification pair ready: {formats[0]} + {formats[1]}.")
                    confirmed = st.checkbox(
                        "Confirm specification roles and parse source blocks",
                        key="data_upload.specification.confirmed",
                    )
                    if confirmed:
                        try:
                            pair = parse_specification_pair(
                                tuple(
                                    SpecificationUploadInput(
                                        filename=upload.name,
                                        mime_type=upload.type,
                                        content=upload.getvalue(),
                                        detection=detection,
                                        role=role_by_hash[detection.sha256],
                                    )
                                    for upload, detection in specification_items
                                )
                            )
                            st.success(
                                f"Parsed {pair.pair_format.value.replace('_', ' + ').upper()} pair into the common specification contract."
                            )
                            metadata_rows = [
                                {
                                    "Role": document.document_role.value.title(),
                                    "Format": document.document_format.value.upper(),
                                    "File": document.filename,
                                    "SHA-256": document.sha256,
                                    "Parser": document.parser_name,
                                    "Parser version": document.parser_version,
                                    "Source blocks": len(document.source_blocks),
                                    "Warnings": ", ".join(document.warnings),
                                }
                                for document in (pair.existing, pair.proposed)
                            ]
                            st.dataframe(metadata_rows, width="stretch", hide_index=True)
                            st.subheader("Common source blocks")
                            st.dataframe(source_block_rows(pair), width="stretch", hide_index=True)
                        except ValueError as error:
                            st.error(str(error))
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

with st.expander("Build U3 scope and limitations"):
    st.write("- XLSX, CSV and JSON reuse the existing structured validation and immutable-save workflow")
    st.write("- DOCX and searchable PDF reuse their existing validators and deterministic parsers")
    st.write("- PDF/PDF, DOCX/DOCX, PDF/DOCX and DOCX/PDF pairs are supported")
    st.write("- Exactly one Existing and one Proposed role is required")
    st.write("- Format, SHA-256, parser identity, parser version and source location are preserved")
    st.write("- Common source blocks are displayed; extraction, review, comparison, mapping and snapshots remain inactive")
    st.write("- No OCR or live AI")
