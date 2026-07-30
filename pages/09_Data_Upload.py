from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from src.application.runtime import build_project_service, build_specification_snapshot_repository, build_upload_service
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
from src.persistence.specification_snapshot_repository import DuplicateSpecificationSnapshotError
from src.review_comparison import ReviewError, ReviewState
from src.specification_intake import (
    DocumentRole,
    all_reviews_resolved,
    apply_review_action,
    build_common_review_views,
    build_unified_canonical_draft,
    build_unified_snapshot,
)
from src.specification_intake.comparison_presentation import (
    COMPARISON_STATUSES,
    CRITICALITY_LEVELS,
    FIELD_CRITICALITY,
    comparison_rows,
    display_value,
    filter_comparison_rows,
    missing_priority_summary,
)
from src.upload_routing import DetectionStatus, WorkflowKind, detect_upload
from src.uploads import DuplicateDatasetError, UploadParseError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"
SOURCE_REPOSITORY = "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence"
SOURCE_REFERENCE = "FINAL-WORKFLOW-CORRECTION-DRAFT"
BASELINE_CONFIRMATION_KEY = "data_upload.approved_existing_baseline"

REVIEW_STATE_HEADING = {
    ReviewState.PENDING: "🟧 ACTION REQUIRED",
    ReviewState.CONFIRMED: "✅ CONFIRMED",
    ReviewState.CORRECTED_CONFIRMED: "✅ CORRECTED AND CONFIRMED",
    ReviewState.INTENTIONALLY_OMITTED: "⚪ INTENTIONALLY OMITTED",
    ReviewState.REJECTED: "⛔ REJECTED",
}


@st.cache_resource
def services():
    return build_project_service(DATABASE_PATH), build_upload_service(DATABASE_PATH), build_specification_snapshot_repository(DATABASE_PATH)


def issue_rows(prepared):
    return [{"Code": issue.code, "Path": issue.path, "Message": issue.message} for issue in prepared.validation.issues]


def format_source_location(location: dict[str, object]) -> str:
    if location.get("type") == "pdf":
        parts = [f"Page {location.get('page_number', '—')}"]
        if location.get("block_index") is not None:
            parts.append(f"Block {location['block_index']}")
        return " · ".join(parts)
    parts: list[str] = []
    if location.get("section_title"):
        parts.append(f"Section: {location['section_title']}")
    for key, label in (("paragraph_index", "Paragraph"), ("table_index", "Table"), ("row_index", "Row"), ("cell_index", "Cell")):
        if location.get(key) is not None:
            parts.append(f"{label} {location[key]}")
    return " · ".join(parts) or "Location not available"


def canonical_summary_rows(data: dict[str, Any]) -> list[dict[str, str]]:
    project = data.get("packaging_project", {})
    return [
        {"Item": "Dataset type", "Value": str(data.get("dataset_type", "Not provided"))},
        {"Item": "Schema version", "Value": str(data.get("schema_version", "Not provided"))},
        {"Item": "Project ID", "Value": str(project.get("project_id", "Not provided"))},
        {"Item": "Project name", "Value": str(project.get("project_name", "Not provided"))},
        {"Item": "Category", "Value": str(project.get("category", "Not provided"))},
        {"Item": "Annual volume", "Value": display_value(project.get("annual_volume"), project.get("annual_volume_unit"))},
        {"Item": "Currency", "Value": str(project.get("currency", "Not provided"))},
        {"Item": "Packaging alternatives", "Value": str(len(data.get("packaging_alternatives", [])))},
        {"Item": "Evidence references", "Value": str(len(data.get("decision_evidence", [])))},
    ]


def alternative_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [{
        "Alternative": item.get("name", item.get("alternative_id", "Unnamed")),
        "Status": str(item.get("status", "Not provided")).title(),
        "Length (mm)": item.get("length_mm"),
        "Width (mm)": item.get("width_mm"),
        "Height (mm)": item.get("height_mm"),
        "Weight (g)": item.get("case_weight_g"),
        "Board grade": item.get("board_grade", "Not provided"),
    } for item in data.get("packaging_alternatives", [])]


def render_canonical_summary(data: dict[str, Any], title: str) -> None:
    with st.expander(title):
        st.dataframe(canonical_summary_rows(data), width="stretch", hide_index=True)
        alternatives = alternative_rows(data)
        if alternatives:
            st.markdown("**Packaging alternatives**")
            st.dataframe(alternatives, width="stretch", hide_index=True)


def render_prepared_upload(upload_service, project, prepared):
    if prepared.validation.is_valid:
        st.success("Validation passed. This canonical dataset is eligible for immutable storage.")
    else:
        st.error("Validation failed. Correct all reported issues before saving a dataset version.")
        st.dataframe(issue_rows(prepared), width="stretch", hide_index=True)
    if prepared.validation.insufficient_data_eligible:
        st.warning("The dataset remains eligible for an insufficient-data outcome. Technical evidence and human approval controls still apply.")
    render_canonical_summary(prepared.canonical_data, "Canonical dataset summary")
    if st.button("Save immutable dataset version", disabled=not prepared.validation.is_valid, width="stretch", key=f"save-{prepared.source_type}-{prepared.original_filename}"):
        try:
            saved = upload_service.save_valid_dataset(project_id=project["project_id"], prepared=prepared)
            st.success(f"Dataset version {saved['version_number']} saved.")
            st.rerun()
        except DuplicateDatasetError as error:
            st.warning(str(error))
        except ValueError as error:
            st.error(str(error))


def render_missing_priority_alerts(rows: list[dict[str, str]]) -> None:
    gaps = missing_priority_summary(rows)
    if gaps.critical:
        st.error("Critical parameters missing from one document: " + ", ".join(gaps.critical) + ". Resolve before treating the comparison as complete.")
    if gaps.major:
        st.warning("Major parameters missing from one document: " + ", ".join(gaps.major) + ". Review before continuing downstream.")
    if gaps.minor and not gaps.has_high_priority_gap:
        st.info("Only minor parameters are incomplete: " + ", ".join(gaps.minor) + ". The review may continue, subject to existing validation and human approval controls.")


def confirm_existing_baseline(views):
    confirmed = []
    for view in views:
        if view.document_role is DocumentRole.EXISTING and view.state is ReviewState.PENDING:
            confirmed.append(apply_review_action(view, ReviewState.CONFIRMED, reviewer_note="Approved existing baseline confirmed by the reviewer."))
        else:
            confirmed.append(view)
    return tuple(confirmed)


def render_baseline_views(views, visible_fields: set[str]) -> None:
    st.subheader("Approved existing baseline")
    st.caption("Existing values are read-only reference evidence. Review actions apply only to the Proposed specification.")
    for view in views:
        if view.document_role is not DocumentRole.EXISTING:
            continue
        parameter = view.field_name.replace("_", " ").title()
        if parameter not in visible_fields:
            continue
        criticality = FIELD_CRITICALITY[view.field_name].value
        with st.expander(f"✅ APPROVED BASELINE — Existing — {parameter} · {criticality}"):
            st.write(f"**Baseline value:** {display_value(view.normalized_value, view.unit)}")
            st.write(f"**Source text:** {view.source_excerpt}")
            with st.expander("Technical source evidence"):
                st.write(f"**Document:** {view.filename}")
                st.write(f"**Source location:** {format_source_location(view.source_location)}")
                st.write(f"**Source block:** {view.source_block_id}")
                st.write(f"**Confidence:** {view.confidence:.1f} ({view.confidence_band.title()})")


def render_reviews(views):
    updated = list(views)
    rows = comparison_rows(updated)
    st.subheader("Specification comparison")
    st.caption("Existing approved-baseline and Proposed candidate values are aligned by governed parameter. Criticality remains a presentation-only review aid.")
    selected_statuses = st.multiselect("Filter by comparison status", options=list(COMPARISON_STATUSES), default=list(COMPARISON_STATUSES), key="data_upload.comparison_status_filter")
    selected_criticalities = st.multiselect("Filter by parameter criticality", options=list(CRITICALITY_LEVELS), default=list(CRITICALITY_LEVELS), key="data_upload.criticality_filter")
    filtered_rows = filter_comparison_rows(rows, statuses=selected_statuses, criticalities=selected_criticalities)
    st.dataframe(filtered_rows, width="stretch", hide_index=True)
    render_missing_priority_alerts(rows)
    visible_fields = {row["Parameter"] for row in filtered_rows}
    render_baseline_views(updated, visible_fields)

    proposed_views = [(index, view) for index, view in enumerate(updated) if view.document_role is DocumentRole.PROPOSED]
    st.subheader("Proposed specification review")
    total_count = len(proposed_views)
    pending_count = sum(view.state is ReviewState.PENDING for _, view in proposed_views)
    resolved_count = total_count - pending_count
    st.write(f"**Review progress:** {resolved_count} of {total_count} Proposed candidates resolved")
    if total_count:
        st.progress(resolved_count / total_count)
    if pending_count:
        st.warning(f"🟧 {pending_count} Proposed candidates require action. Pending candidates are listed first.")
    else:
        st.success("All Proposed candidate reviews are resolved.")
    show_unresolved_only = st.checkbox("Show unresolved candidates only", value=True, key="data_upload.show_unresolved_only", help="Turn this off to display reviewed Proposed candidates for audit inspection.")
    ordered_views = sorted(proposed_views, key=lambda item: item[1].state is not ReviewState.PENDING)
    for index, view in ordered_views:
        parameter = view.field_name.replace("_", " ").title()
        if parameter not in visible_fields or (show_unresolved_only and view.state is not ReviewState.PENDING):
            continue
        criticality = FIELD_CRITICALITY[view.field_name].value
        heading = f"{REVIEW_STATE_HEADING[view.state]} — Proposed — {parameter} · {criticality}"
        with st.expander(heading):
            st.write(f"**Proposed value:** {display_value(view.normalized_value, view.unit)}")
            st.write(f"**Source text:** {view.source_excerpt}")
            st.caption(f"{view.document_format.upper()} · {view.parser_name} · {view.parser_version}")
            with st.expander("Technical source evidence"):
                st.write(f"**Document:** {view.filename}")
                st.write(f"**Source location:** {format_source_location(view.source_location)}")
                st.write(f"**Source block:** {view.source_block_id}")
                st.write(f"**Confidence:** {view.confidence:.1f} ({view.confidence_band.title()})")
                if view.ambiguity_codes:
                    st.write("**Ambiguities:** " + ", ".join(code.replace("_", " ").title() for code in view.ambiguity_codes))
                if view.warnings:
                    st.write("**Warnings:** " + "; ".join(view.warnings))
            selected_state = ReviewState(st.selectbox("Review action", [state.value for state in ReviewState], index=[state.value for state in ReviewState].index(view.state.value), key=f"review-action-{view.review_id}", format_func=lambda value: value.replace("_", " ").title()))
            corrected_value = corrected_unit = note = None
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
                    updated[index] = apply_review_action(view, selected_state, corrected_value=corrected_value, corrected_unit=corrected_unit, reviewer_note=note)
                    st.session_state[SPEC_REVIEWS_KEY] = tuple(updated)
                    st.rerun()
                except ReviewError as error:
                    st.error(str(error))
    resolved = all_reviews_resolved(updated)
    if resolved:
        st.success("All Proposed candidates are reviewed. Confirmed baseline and accepted Proposed values can continue downstream.")
    else:
        st.warning("Pending Proposed candidates remain. No values can continue downstream.")
    return tuple(updated), resolved


def render_specification_snapshot(pair, views):
    active_project_id = st.session_state.get("active_project_id")
    if not active_project_id:
        st.info("Select an active workspace from the Project Dashboard before generating a canonical draft.")
        return
    project_service, _, snapshot_repository = services()
    try:
        project = project_service.get_project(str(active_project_id))
    except KeyError:
        st.session_state.pop("active_project_id", None)
        st.error("The active project no longer exists.")
        return
    if project["archived_at"] is not None:
        st.error("Archived projects are read-only.")
        return
    try:
        canonical = build_unified_canonical_draft(project=project, pair=pair, views=views, source_repository=SOURCE_REPOSITORY, source_commit=SOURCE_REFERENCE)
        snapshot = build_unified_snapshot(project_id=project["project_id"], pair=pair, views=views, canonical=canonical)
    except ValueError as error:
        st.error(str(error))
        return
    st.subheader("Confirmed-only canonical dataset draft")
    if canonical.is_valid:
        st.success("Canonical validation passed.")
    else:
        st.warning("Canonical validation found issues. Human and engineering controls remain mandatory.")
        if canonical.validation_issues:
            st.dataframe(list(canonical.validation_issues), width="stretch", hide_index=True)
    render_canonical_summary(canonical.canonical_data, "Canonical dataset draft summary")
    st.subheader("Immutable specification snapshot")
    st.dataframe([{"Snapshot ID": snapshot.snapshot_id, "Pair format": snapshot.pair_format.replace("_", " + ").upper(), "Existing": f"{snapshot.existing_document.format.upper()} — {snapshot.existing_document.filename}", "Proposed": f"{snapshot.proposed_document.format.upper()} — {snapshot.proposed_document.filename}", "Confirmed fields": len(snapshot.confirmed_fields), "Canonical valid": snapshot.canonical_validation_valid, "Content hash": snapshot.content_hash}], width="stretch", hide_index=True)
    if st.button("Create immutable specification snapshot", width="stretch"):
        try:
            saved = snapshot_repository.create(snapshot)
            st.success(f"Immutable specification snapshot {saved['specification_snapshot_id']} created.")
            st.dataframe([{"Snapshot ID": saved["specification_snapshot_id"], "Created": saved["created_at"], "Pair format": saved["pair_format"].replace("_", " + ").upper(), "Content hash": saved["content_hash"]}], width="stretch", hide_index=True)
        except DuplicateSpecificationSnapshotError as error:
            st.warning(str(error))
        except (KeyError, PermissionError, ValueError) as error:
            st.error(str(error))


st.set_page_config(page_title="Data Upload", layout="wide")
st.title("Data Upload")
st.caption("Upload project data or packaging specifications. File type and intended workflow are detected automatically.")
st.info("Structured files reuse existing validation. Reviewed DOCX and searchable PDF values can create immutable unified specification snapshots.")
uploaded_files = st.file_uploader("Upload files", type=["xlsx", "csv", "json", "docx", "pdf"], accept_multiple_files=True, help="Supported: XLSX, CSV, JSON, DOCX and searchable PDF.")

if uploaded_files:
    detections = [detect_upload(upload.name, upload.type, upload.getvalue()) for upload in uploaded_files]
    st.subheader("Detection and routing")
    st.dataframe([{"File": detection.filename, "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected", "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None", "Status": detection.status.value.replace("_", " ").title(), "Role confirmation": "Required" if detection.requires_document_role else "Not required", "Reason": detection.reason_code or ""} for detection in detections], width="stretch", hide_index=True)
    rejected = [item for item in detections if item.status is DetectionStatus.REJECTED]
    if rejected:
        for item in rejected:
            st.error(f"{item.filename}: {item.detail or item.reason_code}")
    else:
        structured_files = [StructuredUploadFile(upload.name, upload.getvalue(), detection) for upload, detection in zip(uploaded_files, detections) if detection.workflow is WorkflowKind.STRUCTURED_PROJECT_DATA]
        specification_items = [(upload, detection) for upload, detection in zip(uploaded_files, detections) if detection.workflow is WorkflowKind.SPECIFICATION_COMPARISON]
        if structured_files and specification_items:
            st.warning("This batch contains project data and specification documents. Process one workflow group at a time.")
        elif specification_items:
            if len(specification_items) != 2:
                st.error("Exactly two specification documents are required: one Existing and one Proposed.")
            else:
                st.subheader("Specification roles")
                role_by_hash = {}
                for upload, detection in specification_items:
                    selected = st.selectbox(f"Role for {upload.name}", [role.value for role in DocumentRole], key=f"data_upload.role.{detection.sha256}", format_func=str.title)
                    role_by_hash[detection.sha256] = DocumentRole(selected)
                if set(role_by_hash.values()) != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
                    st.error("Assign exactly one Existing and one Proposed specification.")
                else:
                    inputs = tuple(SpecificationUploadInput(filename=upload.name, mime_type=upload.type, content=upload.getvalue(), detection=detection, role=role_by_hash[detection.sha256]) for upload, detection in specification_items)
                    invalidate_specification_state_on_change(st.session_state, inputs)
                    st.success("Specification pair ready: " + " + ".join(item.detection.file_format.value.upper() for item in inputs))
                    baseline_confirmed = st.checkbox("I confirm that the Existing specification is the approved baseline and may be used as read-only reference evidence.", key=BASELINE_CONFIRMATION_KEY)
                    roles_confirmed = st.checkbox("Confirm roles and run governed extraction", key=SPEC_CONFIRMATION_KEY)
                    if roles_confirmed and not baseline_confirmed:
                        st.warning("Confirm the approved Existing baseline before running governed extraction.")
                    if roles_confirmed and baseline_confirmed:
                        try:
                            pair = parse_specification_pair(inputs)
                            with st.expander("Source document evidence"):
                                st.dataframe(source_block_rows(pair), width="stretch", hide_index=True)
                            if SPEC_REVIEWS_KEY not in st.session_state:
                                st.session_state[SPEC_REVIEWS_KEY] = confirm_existing_baseline(build_common_review_views(pair))
                            else:
                                st.session_state[SPEC_REVIEWS_KEY] = confirm_existing_baseline(st.session_state[SPEC_REVIEWS_KEY])
                            views, resolved = render_reviews(st.session_state[SPEC_REVIEWS_KEY])
                            if resolved:
                                render_specification_snapshot(pair, views)
                        except (ValueError, ReviewError) as error:
                            st.error(str(error))
        elif structured_files:
            invalidate_structured_state_on_change(st.session_state, structured_files)
            try:
                detected_format = validate_structured_batch(structured_files)
                st.success(f"Detected structured project-data workflow: {detected_format.value.upper()}.")
                if st.checkbox("Confirm that these files should be processed as structured project data", key=STRUCTURED_CONFIRMATION_KEY):
                    project_service, upload_service, _ = services()
                    active_project_id = st.session_state.get("active_project_id")
                    if not active_project_id:
                        st.info("Select an active workspace from the Project Dashboard before validating project data.")
                    else:
                        try:
                            project = project_service.get_project(str(active_project_id))
                            if project["archived_at"] is not None:
                                st.error("Archived projects are read-only and cannot receive new uploads.")
                            else:
                                prepared = prepare_structured_upload(upload_service, project, structured_files)
                                render_prepared_upload(upload_service, project, prepared)
                        except (KeyError, UploadParseError) as error:
                            st.error(str(error))
            except UploadParseError as error:
                st.error(str(error))
else:
    st.write("No files uploaded.")

with st.expander("Build U6 scope and limitations"):
    st.write("- Unified snapshots preserve document formats, hashes, parser versions and typed source locations")
    st.write("- Existing values are preserved as explicitly confirmed approved-baseline evidence")
    st.write("- Only reviewed Proposed values continue as candidate changes")
    st.write("- Canonical draft and unchanged canonical-validation result are preserved")
    st.write("- Persistence is additive, append-only and content-addressed")
    st.write("- Duplicate content, updates, deletes, archived projects and cross-project access are rejected")
    st.write("- No OCR, live AI, recommendation or decision automation")
