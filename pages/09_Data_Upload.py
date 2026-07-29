from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import streamlit as st

from src.application.runtime import (
    build_project_service,
    build_specification_snapshot_repository,
    build_upload_service,
)
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
from src.upload_routing import DetectionStatus, WorkflowKind, detect_upload
from src.uploads import DuplicateDatasetError, UploadParseError

ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = ROOT / "runtime" / "pve_portfolio.sqlite3"
SOURCE_REPOSITORY = "pratikoperations/Packaging-Value-Engineering-Decision-Intelligence"
SOURCE_REFERENCE = "PR-56-DRAFT"


@st.cache_resource
def services():
    return (
        build_project_service(DATABASE_PATH),
        build_upload_service(DATABASE_PATH),
        build_specification_snapshot_repository(DATABASE_PATH),
    )


def issue_rows(prepared):
    return [{"Code": issue.code, "Path": issue.path, "Message": issue.message} for issue in prepared.validation.issues]


def _display_value(value: Any, unit: str | None = None) -> str:
    if value is None or value == "":
        return "Not provided"
    rendered = str(value)
    return f"{rendered} {unit}".strip() if unit else rendered


def _effective_display(view) -> str:
    review = view.review
    if review.state is ReviewState.CORRECTED_CONFIRMED:
        return _display_value(review.corrected_value, review.corrected_unit)
    return _display_value(view.normalized_value, view.unit)


def _comparison_rows(views: Iterable) -> list[dict[str, str]]:
    by_field: dict[str, dict[str, Any]] = {}
    for view in views:
        by_field.setdefault(view.field_name, {})[view.document_role.value] = view

    rows: list[dict[str, str]] = []
    for field_name in sorted(by_field):
        pair = by_field[field_name]
        existing = pair.get(DocumentRole.EXISTING.value)
        proposed = pair.get(DocumentRole.PROPOSED.value)
        existing_value = _effective_display(existing) if existing else "Not provided"
        proposed_value = _effective_display(proposed) if proposed else "Not provided"
        if existing is None or proposed is None:
            status = "Incomplete"
        elif existing_value == proposed_value:
            status = "Unchanged"
        else:
            status = "Changed"
        rows.append({
            "Parameter": field_name.replace("_", " ").title(),
            "Existing": existing_value,
            "Proposed": proposed_value,
            "Comparison Status": status,
        })
    return rows


def _format_source_location(location: dict[str, object]) -> str:
    if location.get("type") == "pdf":
        parts = [f"Page {location.get('page_number', '—')}"]
        if location.get("block_index") is not None:
            parts.append(f"Block {location['block_index']}")
        return " · ".join(parts)

    parts: list[str] = []
    if location.get("section_title"):
        parts.append(f"Section: {location['section_title']}")
    if location.get("paragraph_index") is not None:
        parts.append(f"Paragraph {location['paragraph_index']}")
    if location.get("table_index") is not None:
        parts.append(f"Table {location['table_index']}")
    if location.get("row_index") is not None:
        parts.append(f"Row {location['row_index']}")
    if location.get("cell_index") is not None:
        parts.append(f"Cell {location['cell_index']}")
    return " · ".join(parts) or "Location not available"


def _canonical_summary_rows(data: dict[str, Any]) -> list[dict[str, str]]:
    project = data.get("packaging_project", {})
    alternatives = data.get("packaging_alternatives", [])
    evidence = data.get("decision_evidence", [])
    return [
        {"Item": "Dataset type", "Value": str(data.get("dataset_type", "Not provided"))},
        {"Item": "Schema version", "Value": str(data.get("schema_version", "Not provided"))},
        {"Item": "Project ID", "Value": str(project.get("project_id", "Not provided"))},
        {"Item": "Project name", "Value": str(project.get("project_name", "Not provided"))},
        {"Item": "Category", "Value": str(project.get("category", "Not provided"))},
        {"Item": "Annual volume", "Value": _display_value(project.get("annual_volume"), project.get("annual_volume_unit"))},
        {"Item": "Currency", "Value": str(project.get("currency", "Not provided"))},
        {"Item": "Packaging alternatives", "Value": str(len(alternatives))},
        {"Item": "Evidence references", "Value": str(len(evidence))},
    ]


def _alternative_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for alternative in data.get("packaging_alternatives", []):
        rows.append({
            "Alternative": alternative.get("name", alternative.get("alternative_id", "Unnamed")),
            "Status": str(alternative.get("status", "Not provided")).title(),
            "Length (mm)": alternative.get("length_mm"),
            "Width (mm)": alternative.get("width_mm"),
            "Height (mm)": alternative.get("height_mm"),
            "Weight (g)": alternative.get("case_weight_g"),
            "Board grade": alternative.get("board_grade", "Not provided"),
        })
    return rows


def render_canonical_summary(data: dict[str, Any], title: str) -> None:
    with st.expander(title):
        st.dataframe(_canonical_summary_rows(data), width="stretch", hide_index=True)
        alternatives = _alternative_rows(data)
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


def render_reviews(views):
    updated = list(views)
    st.subheader("Specification comparison")
    st.caption("Existing and proposed values are aligned by governed parameter. Comparison Status shows whether the extracted values differ.")
    st.dataframe(_comparison_rows(updated), width="stretch", hide_index=True)

    st.subheader("Governed extraction review")
    st.caption("Review only the parameters requiring confirmation, correction, omission or rejection. Technical evidence is available on demand.")
    for index, view in enumerate(updated):
        with st.expander(f"{view.document_role.value.title()} — {view.field_name.replace('_', ' ').title()}"):
            st.write(f"**Extracted value:** {_display_value(view.normalized_value, view.unit)}")
            st.write(f"**Source text:** {view.source_excerpt}")
            st.caption(f"{view.document_format.upper()} · {view.parser_name} · {view.parser_version}")
            with st.expander("Technical source evidence"):
                st.write(f"**Document:** {view.filename}")
                st.write(f"**Source location:** {_format_source_location(view.source_location)}")
                st.write(f"**Source block:** {view.source_block_id}")
                st.write(f"**Confidence:** {view.confidence:.1f} ({view.confidence_band.title()})")
                if view.ambiguity_codes:
                    st.write("**Ambiguities:** " + ", ".join(code.replace("_", " ").title() for code in view.ambiguity_codes))
                if view.warnings:
                    st.write("**Warnings:** " + "; ".join(view.warnings))
            selected_state = ReviewState(st.selectbox(
                "Review action",
                [state.value for state in ReviewState],
                index=[state.value for state in ReviewState].index(view.state.value),
                key=f"review-action-{view.review_id}",
                format_func=lambda value: value.replace("_", " ").title(),
            ))
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
        st.success("All candidates are reviewed. Only confirmed and corrected-confirmed values continue.")
    else:
        st.warning("Pending candidates remain. No values can continue downstream.")
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
        canonical = build_unified_canonical_draft(
            project=project,
            pair=pair,
            views=views,
            source_repository=SOURCE_REPOSITORY,
            source_commit=SOURCE_REFERENCE,
        )
        snapshot = build_unified_snapshot(
            project_id=project["project_id"],
            pair=pair,
            views=views,
            canonical=canonical,
        )
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
    st.dataframe([{
        "Snapshot ID": snapshot.snapshot_id,
        "Pair format": snapshot.pair_format.replace("_", " + ").upper(),
        "Existing": f"{snapshot.existing_document.format.upper()} — {snapshot.existing_document.filename}",
        "Proposed": f"{snapshot.proposed_document.format.upper()} — {snapshot.proposed_document.filename}",
        "Confirmed fields": len(snapshot.confirmed_fields),
        "Canonical valid": snapshot.canonical_validation_valid,
        "Content hash": snapshot.content_hash,
    }], width="stretch", hide_index=True)
    if st.button("Create immutable specification snapshot", width="stretch"):
        try:
            saved = snapshot_repository.create(snapshot)
            st.success(f"Immutable specification snapshot {saved['specification_snapshot_id']} created.")
            st.dataframe([{
                "Snapshot ID": saved["specification_snapshot_id"],
                "Created": saved["created_at"],
                "Pair format": saved["pair_format"].replace("_", " + ").upper(),
                "Content hash": saved["content_hash"],
            }], width="stretch", hide_index=True)
        except DuplicateSpecificationSnapshotError as error:
            st.warning(str(error))
        except (KeyError, PermissionError, ValueError) as error:
            st.error(str(error))


st.set_page_config(page_title="Data Upload", layout="wide")
st.title("Data Upload")
st.caption("Upload project data or packaging specifications. File type and intended workflow are detected automatically.")
st.info("Structured files reuse existing validation. Reviewed DOCX and searchable PDF values can create immutable unified specification snapshots.")

uploaded_files = st.file_uploader(
    "Upload files", type=["xlsx", "csv", "json", "docx", "pdf"],
    accept_multiple_files=True, help="Supported: XLSX, CSV, JSON, DOCX and searchable PDF.",
)

if uploaded_files:
    detections = [detect_upload(upload.name, upload.type, upload.getvalue()) for upload in uploaded_files]
    st.subheader("Detection and routing")
    st.dataframe([{
        "File": detection.filename,
        "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected",
        "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None",
        "Status": detection.status.value.replace("_", " ").title(),
        "Role confirmation": "Required" if detection.requires_document_role else "Not required",
        "Reason": detection.reason_code or "",
    } for detection in detections], width="stretch", hide_index=True)

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
            (upload, detection) for upload, detection in zip(uploaded_files, detections)
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
                        f"Role for {upload.name}", [role.value for role in DocumentRole],
                        key=f"data_upload.role.{detection.sha256}", format_func=str.title,
                    )
                    role_by_hash[detection.sha256] = DocumentRole(selected)
                if set(role_by_hash.values()) != {DocumentRole.EXISTING, DocumentRole.PROPOSED}:
                    st.error("Assign exactly one Existing and one Proposed specification.")
                else:
                    inputs = tuple(SpecificationUploadInput(
                        filename=upload.name, mime_type=upload.type, content=upload.getvalue(),
                        detection=detection, role=role_by_hash[detection.sha256],
                    ) for upload, detection in specification_items)
                    invalidate_specification_state_on_change(st.session_state, inputs)
                    st.success("Specification pair ready: " + " + ".join(item.detection.file_format.value.upper() for item in inputs))
                    if st.checkbox("Confirm roles and run governed extraction", key=SPEC_CONFIRMATION_KEY):
                        try:
                            pair = parse_specification_pair(inputs)
                            with st.expander("Source document evidence"):
                                st.dataframe(source_block_rows(pair), width="stretch", hide_index=True)
                            if SPEC_REVIEWS_KEY not in st.session_state:
                                st.session_state[SPEC_REVIEWS_KEY] = build_common_review_views(pair)
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
                                render_prepared_upload(upload_service, project, prepare_structured_upload(upload_service, project, structured_files))
                        except (KeyError, UploadParseError) as error:
                            st.error(str(error))
            except UploadParseError as error:
                st.error(str(error))
else:
    st.write("No files uploaded.")

with st.expander("Build U6 scope and limitations"):
    st.write("- Unified snapshots preserve document formats, hashes, parser versions and typed source locations")
    st.write("- Only Confirmed and Corrected Confirmed values are persisted")
    st.write("- Canonical draft and unchanged canonical-validation result are preserved")
    st.write("- Persistence is additive, append-only and content-addressed")
    st.write("- Duplicate content, updates, deletes, archived projects and cross-project access are rejected")
    st.write("- Existing Word and PDF snapshot tables are not migrated or deleted")
    st.write("- No OCR, live AI, recommendation or decision automation")
