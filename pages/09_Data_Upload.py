from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.application.runtime import build_project_service, build_upload_service
from src.application.specification_upload import (
    SPEC_CONFIRMATION_KEY,
    SPEC_REVIEWS_KEY,
    SpecificationUploadInput,
    invalidate_specification_state_on_change,
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
from src.review_comparison import ReviewError, ReviewState
from src.specification_intake import (
    DocumentRole,
    all_reviews_resolved,
    apply_review_action,
    build_common_review_views,
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


def render_reviews(views):
    updated = list(views)
    st.subheader("Governed extraction review")
    st.caption("Candidates are deterministic, source-grounded and limited to the existing governed 25-field registry.")
    for index, view in enumerate(updated):
        with st.expander(f"{view.document_role.value.title()} — {view.field_name.replace('_', ' ').title()}"):
            st.write(f"**Extracted:** {view.normalized_value} {view.unit or ''}".strip())
            st.write(f"**Source:** {view.source_excerpt}")
            st.write(f"**Format / parser:** {view.document_format.upper()} — {view.parser_name} / {view.parser_version}")
            st.json(view.source_location)
            action = st.selectbox(
                "Review action",
                [state.value for state in ReviewState],
                index=[state.value for state in ReviewState].index(view.state.value),
                key=f"review-action-{view.review_id}",
                format_func=lambda value: value.replace("_", " ").title(),
            )
            corrected_value = corrected_unit = note = None
            selected_state = ReviewState(action)
            if selected_state is ReviewState.CORRECTED_CONFIRMED:
                corrected_value = st.text_input("Corrected value", key=f"corrected-value-{view.review_id}")
                corrected_unit = st.text_input("Corrected unit", value=view.unit or "", key=f"corrected-unit-{view.review_id}") or None
                note = st.text_input("Correction note", key=f"review-note-{view.review_id}")
            elif selected_state in {ReviewState.INTENTIONALLY_OMITTED, ReviewState.REJECTED}:
                note = st.text_input("Required reviewer note", key=f"review-note-{view.review_id}")
            elif selected_state is ReviewState.CONFIRMED:
                note = st.text_input("Reviewer note (optional)", key=f"review-note-{view.review_id}") or None
            if st.button("Apply review", key=f"apply-review-{view.review_id}"):
                try:
                    updated[index] = apply_review_action(
                        view,
                        selected_state,
                        corrected_value=corrected_value,
                        corrected_unit=corrected_unit,
                        reviewer_note=note,
                    )
                    st.session_state[SPEC_REVIEWS_KEY] = tuple(updated)
                    st.rerun()
                except ReviewError as error:
                    st.error(str(error))
    resolved = all_reviews_resolved(updated)
    if resolved:
        st.success("All extraction candidates are reviewed. Reviewed values are eligible for the next controlled build stage.")
    else:
        st.warning("Pending candidates remain. No values can continue to downstream mapping.")


st.set_page_config(page_title="Data Upload", layout="wide")
st.title("Data Upload")
st.caption("Upload project data or packaging specifications. File type and intended workflow are detected automatically.")
st.info(
    "Structured files reuse the existing governed validation workflow. "
    "DOCX and searchable PDF specifications reuse existing parsers, grounding and human-review controls."
)

uploaded_files = st.file_uploader(
    "Upload files",
    type=["xlsx", "csv", "json", "docx", "pdf"],
    accept_multiple_files=True,
    help="Supported: XLSX, CSV, JSON, DOCX and searchable PDF.",
)

if uploaded_files:
    detections = [detect_upload(upload.name, upload.type, upload.getvalue()) for upload in uploaded_files]
    rows = [{
        "File": detection.filename,
        "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected",
        "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None",
        "Status": detection.status.value.replace("_", " ").title(),
        "Role confirmation": "Required" if detection.requires_document_role else "Not required",
        "Reason": detection.reason_code or "",
    } for detection in detections]
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
                role_by_hash = {}
                for upload, detection in specification_items:
                    selected = st.selectbox(
                        f"Role for {upload.name}",
                        [role.value for role in DocumentRole],
                        key=f"data_upload.role.{detection.sha256}",
                        format_func=str.title,
                    )
                    role_by_hash[detection.sha256] = DocumentRole(selected)
                if set(role_by_hash.values()) != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
                    st.error("Assign exactly one Existing and one Proposed specification.")
                else:
                    inputs = tuple(
                        SpecificationUploadInput(
                            filename=upload.name,
                            mime_type=upload.type,
                            content=upload.getvalue(),
                            detection=detection,
                            role=role_by_hash[detection.sha256],
                        )
                        for upload, detection in specification_items
                    )
                    invalidate_specification_state_on_change(st.session_state, inputs)
                    formats = [item.detection.file_format.value.upper() for item in inputs]
                    st.success(f"Specification pair ready: {formats[0]} + {formats[1]}.")
                    confirmed = st.checkbox("Confirm roles and run governed extraction", key=SPEC_CONFIRMATION_KEY)
                    if confirmed:
                        try:
                            pair = parse_specification_pair(inputs)
                            st.success(f"Parsed {pair.pair_format.value.replace('_', ' + ').upper()} pair.")
                            st.dataframe(source_block_rows(pair), width="stretch", hide_index=True)
                            if SPEC_REVIEWS_KEY not in st.session_state:
                                st.session_state[SPEC_REVIEWS_KEY] = build_common_review_views(pair)
                            render_reviews(st.session_state[SPEC_REVIEWS_KEY])
                        except (ValueError, ReviewError) as error:
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
                                try:
                                    prepared = prepare_structured_upload(upload_service, project, structured_files)
                                    render_prepared_upload(upload_service, project, prepared)
                                except UploadParseError as error:
                                    st.error(str(error))
            except UploadParseError as error:
                st.error(str(error))
else:
    st.write("No files uploaded.")

with st.expander("Build U4 scope and limitations"):
    st.write("- Existing 25-field registry, grounding, confidence, ambiguity and review controls are reused")
    st.write("- PDF/PDF, DOCX/DOCX, PDF/DOCX and DOCX/PDF pairs are supported")
    st.write("- Confirm, Correct and Confirm, Intentionally Omit, Reject and Pending states are supported")
    st.write("- File, role or pair-format changes invalidate specification confirmation and review state")
    st.write("- Canonical mapping, snapshots and persistence remain inactive")
    st.write("- No OCR or live AI")
