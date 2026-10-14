from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st

from src.application.runtime import build_project_service, build_specification_snapshot_repository, build_specification_draft_repository, build_upload_service
from src.application.specification_upload import (
    SPEC_CONFIRMATION_KEY,
    SPEC_REVIEWS_KEY,
    SpecificationUploadInput,
    SESSION_SPEC_CACHE,
    SessionSpecificationFile,
    restore_session_specifications,
    serialize_provisional_triage,
    restore_provisional_triage,
    classify_triage_source_support,
    invalidate_specification_state_on_change,
    parse_specification_pair,
    source_block_rows,
)
from src.application.specification_draft_backup import export_specification_draft, import_specification_draft
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
from src.specification_intake.review_view import build_manual_source_candidate
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
DRAFT_REVIEW_RESTORE_KEY = "data_upload.restored_draft_reviews"

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


def save_draft_review_state(views) -> tuple[dict, ...]:
    """Serialize reviewer decisions, never Python objects or executable data."""
    return tuple({
        "review_id": view.review_id,
        "state": view.state.value,
        "corrected_value": view.review.corrected_value,
        "corrected_unit": view.review.corrected_unit,
        "reviewer_note": view.review.reviewer_note,
    } for view in views)


def restore_draft_review_state(views, saved):
    """Match decisions to the re-extracted, source-grounded candidate IDs."""
    saved_by_id = {record["review_id"]: record for record in saved}
    if len(saved_by_id) != len(saved):
        raise ValueError("Duplicate draft review identifiers.")
    known_ids = {view.review_id for view in views}
    if not set(saved_by_id).issubset(known_ids):
        raise ValueError("Saved draft review does not match the specification documents.")
    updated = []
    for view in views:
        record = saved_by_id.get(view.review_id)
        if record is None:
            updated.append(view)
            continue
        state = ReviewState(record["state"])
        if state is ReviewState.PENDING:
            updated.append(view)
        else:
            updated.append(apply_review_action(
                view, state, corrected_value=record.get("corrected_value"),
                corrected_unit=record.get("corrected_unit"),
                reviewer_note=record.get("reviewer_note"),
            ))
    return tuple(updated)


def render_draft_controls(project_id, files, views):
    repository = build_specification_draft_repository(DATABASE_PATH)
    if st.button("Save draft to project", key="save-specification-draft"):
        try:
            draft = repository.save(
                project_id, files[0], files[1],
                save_draft_review_state(views) + serialize_provisional_triage(st.session_state),
            )
        except (ValueError, KeyError) as error:
            st.error(str(error))
        else:
            st.success(f"Unfinished specification review saved: {draft.draft_id}")
    st.caption("Drafts are project-scoped and append-only, and do not approve feasibility.")


def clear_specification_session_pair() -> None:
    """Clear file widgets before next render, avoiding stale pair restoration."""
    for key in (
        "data_upload.existing_specification",
        "data_upload.proposed_specification",
        SESSION_SPEC_CACHE,
        SPEC_REVIEWS_KEY,
        SPEC_CONFIRMATION_KEY,
        BASELINE_CONFIRMATION_KEY,
        "data_upload.specification.batch_fingerprint",
        DRAFT_REVIEW_RESTORE_KEY,
    ):
        st.session_state.pop(key, None)
    for key in tuple(st.session_state):
        if key.startswith(("triage_value_", "triage_evidence_", "manual_source_")):
            st.session_state.pop(key, None)


def render_specification_workspace() -> None:
    """Select or create the project that owns any subsequent immutable snapshot."""
    project_service, _, snapshot_repository = services()
    active_id = st.session_state.get("active_project_id")
    active_project = None
    if active_id:
        try:
            candidate = project_service.get_project(str(active_id))
            if candidate["archived_at"] is None:
                active_project = candidate
        except KeyError:
            st.session_state.pop("active_project_id", None)
    # Provisional triage notes are session-local and must not cross project boundaries.
    project_scope = active_project["project_id"] if active_project is not None else None
    if st.session_state.get("data_upload.triage_project_scope") != project_scope:
        for key in tuple(st.session_state):
            if key.startswith(("triage_value_", "triage_evidence_", "manual_source_")):
                st.session_state.pop(key, None)
        st.session_state["data_upload.triage_project_scope"] = project_scope
    if active_project is not None:
        st.success(
            f"Active project: {active_project['project_code']} — {active_project['project_name']}"
        )
        snapshots = snapshot_repository.list_for_project(active_project["project_id"])
        if snapshots:
            with st.expander(f"Saved specification snapshots ({len(snapshots)})"):
                st.dataframe(
                    [
                        {
                            "Snapshot": item["specification_snapshot_id"],
                            "Created": item["created_at"],
                            "Existing": item["existing_document"]["filename"],
                            "Proposed": item["proposed_document"]["filename"],
                            "Canonical valid": item["canonical_validation_valid"],
                        }
                        for item in snapshots
                    ],
                    width="stretch",
                    hide_index=True,
                )
            st.caption(
                "Saved snapshots are immutable evidence records. They do not restore "
                "an incomplete upload or its correction controls."
            )
    else:
        st.warning(
            "No active project. You can compare files now, but an active project "
            "is required to persist the reviewed snapshot."
        )

    if active_project is not None:
        draft_repository = build_specification_draft_repository(DATABASE_PATH)
        drafts = draft_repository.list_for_project(active_project["project_id"])
        if drafts:
            with st.expander(f"Resume saved specification review ({len(drafts)} drafts)"):
                labels = {
                    f"{item['created_at']} — {item['existing_name']} / {item['proposed_name']} [{item['draft_id']}]": item["draft_id"]
                    for item in drafts
                }
                selected = st.selectbox("Saved draft", list(labels), key="specification-draft-select")
                try:
                    backup_draft = draft_repository.get(
                        labels[selected], project_id=active_project["project_id"]
                    )
                    backup_bytes = export_specification_draft(
                        active_project["project_code"], backup_draft
                    )
                    st.download_button(
                        "Download portable draft backup",
                        data=backup_bytes,
                        file_name=f"{active_project['project_code']}_specification_draft.json",
                        mime="application/json",
                        key="specification-download-draft-backup",
                    )
                except (ValueError, KeyError) as error:
                    st.error(f"Backup unavailable: {error}")
                if st.button("Resume selected draft", key="specification-resume-draft"):
                    try:
                        draft = draft_repository.get(labels[selected], project_id=active_project["project_id"])
                    except (ValueError, KeyError) as error:
                        st.error(str(error))
                    else:
                        files = (
                            SessionSpecificationFile(draft.existing_name, draft.existing_mime, draft.existing_content),
                            SessionSpecificationFile(draft.proposed_name, draft.proposed_mime, draft.proposed_content),
                        )
                        # Uploader widgets retain previous file bytes on reruns.
                        # Remove them before the widgets are rendered below so the
                        # recovered immutable draft remains authoritative.
                        st.session_state.pop("data_upload.existing_specification", None)
                        st.session_state.pop("data_upload.proposed_specification", None)
                        st.session_state[SESSION_SPEC_CACHE] = (active_project["project_id"], files)
                        st.session_state[DRAFT_REVIEW_RESTORE_KEY] = draft.reviews
                        st.session_state.pop(SPEC_REVIEWS_KEY, None)
                        st.session_state.pop("data_upload.specification.batch_fingerprint", None)
                        st.session_state[BASELINE_CONFIRMATION_KEY] = True
                        st.session_state[SPEC_CONFIRMATION_KEY] = True
                        st.rerun()

    if active_project is not None:
        with st.expander("Restore a portable specification draft backup"):
            st.caption(
                "Use a previously downloaded JSON backup. Recreate and select the "
                "same project code if server storage has been reset. Imported "
                "evidence is untrusted until reviewed again."
            )
            incoming = st.file_uploader(
                "Portable draft backup (JSON)", type=["json"],
                key="specification-import-backup",
            )
            if incoming is not None and st.button(
                "Import backup to active project", key="specification-import-submit"
            ):
                try:
                    restored = import_specification_draft(
                        build_specification_draft_repository(DATABASE_PATH),
                        project_id=active_project["project_id"],
                        project_code=active_project["project_code"],
                        content=incoming.getvalue(),
                    )
                except (ValueError, KeyError) as error:
                    st.error(str(error))
                else:
                    st.success(f"Draft imported: {restored.draft_id}. Resume and review it.")
                    st.rerun()

    with st.expander("Start a new project for this specification comparison"):
        st.caption(
            "Create and select a project before saving a reviewed specification snapshot. "
            "Creating a project does not save an unfinished document review."
        )
        with st.form("specification-create-project", clear_on_submit=True):
            code = st.text_input("Project code", placeholder="PVE-COR-001")
            name = st.text_input("Project name", placeholder="Corrugated case material optimization")
            annual_volume = st.number_input("Annual volume (boxes)", min_value=1.0, value=120000.0, step=1000.0)
            currency = st.selectbox("Currency", ("INR", "USD", "EUR"), index=0)
            submitted = st.form_submit_button("Create and select project")
        if submitted:
            try:
                created = project_service.create_project(
                    project_code=code,
                    project_name=name,
                    category="corrugated",
                    currency=currency,
                    annual_volume=annual_volume,
                )
            except ValueError as error:
                st.error(str(error))
            else:
                st.session_state["active_project_id"] = created["project_id"]
                st.success(f"Project {created['project_code']} created and selected.")
                st.rerun()


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


def attach_triage_source_reference(key: str, block_id: str) -> None:
    """Streamlit callback runs before widget creation on the next rerun."""
    current = st.session_state.get(f"triage_evidence_{key}", "")
    reference = f"Source block {block_id}; reviewer verification required"
    if reference not in current:
        st.session_state[f"triage_evidence_{key}"] = (
            reference + (f"; {current}" if current else "")
        )


def register_manual_source(key: str, document, block_id: str) -> None:
    value = str(st.session_state.get(f"triage_value_{key}", "")).strip()
    field_name = key.rsplit("_", 1)[0]
    build_manual_source_candidate(
        document=document, field_name=field_name,
        source_block_id=block_id, literal_value=value,
    )
    st.session_state["manual_source_" + key] = {
        "block_id": block_id,
        "sha256": document.sha256,
        "value": value,
    }


def add_manual_source_reviews(pair, views):
    """Rebuild source-grounded candidates for matching document roles and hashes."""
    result = list(views)
    known = {(view.document_role, view.field_name) for view in result}
    for key in tuple(st.session_state):
        if not key.startswith("manual_source_"):
            continue
        suffix = key[len("manual_source_"):]
        if not suffix.endswith(("_existing", "_proposed")):
            continue
        field_name, role_name = suffix.rsplit("_", 1)
        role = DocumentRole(role_name)
        if (role, field_name) in known:
            continue
        document = pair.existing if role is DocumentRole.EXISTING else pair.proposed
        mapping = st.session_state[key]
        if not isinstance(mapping, dict) or mapping.get("sha256") != document.sha256:
            continue
        try:
            candidate = build_manual_source_candidate(
                document=document, field_name=field_name,
                source_block_id=mapping["block_id"], literal_value=mapping["value"],
            )
            if role is DocumentRole.EXISTING:
                candidate = apply_review_action(
                    candidate, ReviewState.CONFIRMED,
                    reviewer_note="Reviewer explicitly confirmed source value from approved Existing baseline.",
                )
        except (KeyError, ReviewError, ValueError):
            continue
        result.append(candidate)
        known.add((role, field_name))
    return tuple(result)


def render_missing_field_triage(rows, pair) -> None:
    """Collect provisional missing-field evidence without changing canonical values."""
    missing = [row for row in rows if row["Comparison Status"] == "Incomplete"]
    if not missing:
        return
    st.subheader("Missing parameter triage")
    st.caption(
        "Enter a provisional value and evidence note to document an extraction gap. "
        "These entries are NOT confirmed specification values, are NOT used by "
        "canonical mapping or feasibility, and do not replace governed review."
    )
    for row in missing:
        name = row["Parameter"]
        with st.expander(f"{name} — {row['Criticality']}"):
            for role in ("Existing", "Proposed"):
                if row[role] != "Not provided":
                    continue
                key = name.lower().replace(" ", "_") + "_" + role.lower()
                st.text_input(
                    f"{role} provisional value — {name}",
                    key=f"triage_value_{key}",
                )
                st.text_input(
                    f"{role} evidence reference or follow-up — {name}",
                    key=f"triage_evidence_{key}",
                )
                document = pair.existing if role == "Existing" else pair.proposed
                source_rows = [
                    (block.block_id, block.normalized_text, block.source_location)
                    for block in document.source_blocks
                    if block.normalized_text.strip()
                ]
                with st.expander("Inspect actual source blocks for this missing value"):
                    st.caption(
                        "Use these exact extracted blocks to find a missed value. "
                        "A block reference does not validate the numerical or technical claim."
                    )
                    if source_rows:
                        st.dataframe([
                            {
                                "Block ID": block_id,
                                "Source text": text,
                                "Location": str(location),
                            }
                            for block_id, text, location in source_rows
                        ], width="stretch", hide_index=True)
                        chosen_block = st.selectbox(
                            "Attach source block reference",
                            options=[""] + [block_id for block_id, _, _ in source_rows],
                            key=f"triage_source_select_{key}",
                        )
                        if chosen_block:
                            classification = classify_triage_source_support(
                                document=document,
                                source_block_id=chosen_block,
                                proposed_value=st.session_state.get(f"triage_value_{key}", ""),
                            )
                            if classification == "literal_value_present":
                                st.info(
                                    "The entered value appears literally in the selected source block. "
                                    "Reviewer confirmation and technical validation are still required."
                                )
                            elif classification == "source_block_requires_manual_verification":
                                st.warning(
                                    "The entered value is not an exact text match in this block. "
                                    "Confirm against the original specification before correction."
                                )
                            elif classification == "value_missing":
                                st.warning("Enter the provisional value before assessing source support.")
                            else:
                                st.error("The selected source block is not valid for this document.")
                        if chosen_block and classification == "literal_value_present":
                            if st.button(
                                "Confirm missing approved-baseline source value" if role == "Existing" else "Create pending Proposed review candidate",
                                key=f"manual_create_{key}",
                            ):
                                try:
                                    register_manual_source(key, document, chosen_block)
                                except (ReviewError, ValueError) as error:
                                    st.error(str(error))
                                else:
                                    st.success("Source-backed value recorded. Existing uses approved-baseline confirmation; Proposed remains pending review.")
                                    st.rerun()
                        st.button(
                            "Use selected source reference",
                            key=f"triage_attach_{key}",
                            disabled=not chosen_block,
                            on_click=attach_triage_source_reference,
                            args=(key, chosen_block),
                        )
                    else:
                        st.info("No searchable text blocks were extracted from this document.")
                st.warning(
                    "Unverified entry only. Correct source extraction or supply "
                    "an approved specification revision before feasibility assessment."
                )


def render_reviews(views, pair):
    updated = list(views)
    rows = comparison_rows(updated)
    st.subheader("Specification comparison")
    st.caption("Existing approved-baseline and Proposed candidate values are aligned by governed parameter. Criticality remains a presentation-only review aid.")
    selected_statuses = st.multiselect("Filter by comparison status", options=list(COMPARISON_STATUSES), default=list(COMPARISON_STATUSES), key="data_upload.comparison_status_filter")
    selected_criticalities = st.multiselect("Filter by parameter criticality", options=list(CRITICALITY_LEVELS), default=list(CRITICALITY_LEVELS), key="data_upload.criticality_filter")
    filtered_rows = filter_comparison_rows(rows, statuses=selected_statuses, criticalities=selected_criticalities)
    st.dataframe(filtered_rows, width="stretch", hide_index=True)
    render_missing_priority_alerts(rows)
    render_missing_field_triage(rows, pair)
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
    st.subheader("Project Feasibility Gate")
    priority_gaps = missing_priority_summary(comparison_rows(views))
    data_ready = canonical.is_valid and not priority_gaps.has_high_priority_gap
    if data_ready:
        st.success(
            "READY FOR DOWNSTREAM FEASIBILITY ASSESSMENT — the reviewed Existing-versus-Proposed "
            "specification pair has passed the canonical data-readiness gate."
        )
        st.caption(
            "This status means the specification comparison is data-ready for downstream commercial, "
            "risk and technical assessment. It is not engineering approval, supplier approval or a production-release decision."
        )
    else:
        st.warning(
            "FEASIBILITY ASSESSMENT BLOCKED — the reviewed specification pair is not yet complete enough "
            "to pass the canonical data-readiness gate."
        )
        if priority_gaps.has_high_priority_gap:
            st.error(
                "Unresolved critical/major source parameters: "
                + ", ".join(priority_gaps.critical + priority_gaps.major)
                + ". Provisional triage notes do not satisfy source evidence requirements."
            )
        st.caption(
            "Resolve source-parameter gaps and canonical validation issues before downstream feasibility assessment."
        )

    st.subheader("Confirmed-only canonical dataset draft")
    if canonical.is_valid:
        st.success("Canonical validation passed.")
    else:
        st.warning("Canonical validation found issues. Human and engineering controls remain mandatory.")
        if canonical.validation_issues:
            st.dataframe(list(canonical.validation_issues), width="stretch", hide_index=True)
    render_canonical_summary(canonical.canonical_data, "Canonical dataset draft summary")
    st.subheader("Immutable specification snapshot")
    if priority_gaps.has_high_priority_gap:
        st.warning("Snapshot creation is blocked until critical and major parameters are present in both source specifications.")
    st.dataframe([{"Snapshot ID": snapshot.snapshot_id, "Pair format": snapshot.pair_format.replace("_", " + ").upper(), "Existing": f"{snapshot.existing_document.format.upper()} — {snapshot.existing_document.filename}", "Proposed": f"{snapshot.proposed_document.format.upper()} — {snapshot.proposed_document.filename}", "Confirmed fields": len(snapshot.confirmed_fields), "Canonical valid": snapshot.canonical_validation_valid, "Content hash": snapshot.content_hash}], width="stretch", hide_index=True)
    if st.button("Create immutable specification snapshot", width="stretch", disabled=priority_gaps.has_high_priority_gap):
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
st.caption("Compare Existing and Proposed packaging specifications or upload structured project data.")
st.info(
    "The specification workflow uses exactly one Existing approved baseline and one Proposed candidate. "
    "Reviewed DOCX and searchable PDF values can create immutable unified specification snapshots."
)

workflow_mode = st.radio(
    "Choose upload workflow",
    [
        "Compare Existing vs Proposed specifications",
        "Upload structured project data",
    ],
    horizontal=True,
    key="data_upload.workflow_mode",
)

if workflow_mode == "Compare Existing vs Proposed specifications":
    st.subheader("Existing vs Proposed Specification Comparison")
    st.caption(
        "Upload the approved Existing specification and the Proposed specification separately. "
        "Roles are fixed by the upload slot so they cannot be accidentally reversed."
    )
    st.info("Exactly two specification documents are required: one Existing and one Proposed.")
    render_specification_workspace()

    existing_upload = st.file_uploader(
        "Existing specification — approved baseline",
        type=["docx", "pdf"],
        key="data_upload.existing_specification",
        help="Upload one approved Existing specification in DOCX or searchable PDF format.",
    )
    proposed_upload = st.file_uploader(
        "Proposed specification — candidate change",
        type=["docx", "pdf"],
        key="data_upload.proposed_specification",
        help="Upload one Proposed specification in DOCX or searchable PDF format.",
    )

    recovered_files, recovered = restore_session_specifications(
        st.session_state, existing_upload, proposed_upload
    )
    st.button(
        "Clear current session specification pair",
        key="clear-session-spec-pair",
        on_click=clear_specification_session_pair,
    )
    if recovered_files is None:
        st.info("Upload exactly one Existing specification and one Proposed specification to begin the governed comparison.")
    else:
        if recovered:
            st.info(
                "Restored the Existing and Proposed files from this browser session. "
                "This is not a persisted draft: create an immutable snapshot when eligible."
            )
        specification_uploads = (
            (recovered_files[0], DocumentRole.EXISTING),
            (recovered_files[1], DocumentRole.PROPOSED),
        )
        detections = [
            detect_upload(upload.name, upload.type, upload.getvalue())
            for upload, _ in specification_uploads
        ]
        st.subheader("Detection and routing")
        st.dataframe(
            [
                {
                    "Role": role.value.title(),
                    "File": detection.filename,
                    "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected",
                    "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None",
                    "Status": detection.status.value.replace("_", " ").title(),
                    "Reason": detection.reason_code or "",
                }
                for (upload, role), detection in zip(specification_uploads, detections)
            ],
            width="stretch",
            hide_index=True,
        )

        rejected = [
            detection
            for detection in detections
            if detection.status is DetectionStatus.REJECTED
            or detection.workflow is not WorkflowKind.SPECIFICATION_COMPARISON
        ]
        if rejected:
            for item in rejected:
                st.error(f"{item.filename}: {item.detail or item.reason_code or 'File is not eligible for specification comparison.'}")
        else:
            inputs = tuple(
                SpecificationUploadInput(
                    filename=upload.name,
                    mime_type=upload.type,
                    content=upload.getvalue(),
                    detection=detection,
                    role=role,
                )
                for (upload, role), detection in zip(specification_uploads, detections)
            )
            invalidate_specification_state_on_change(st.session_state, inputs)
            if DRAFT_REVIEW_RESTORE_KEY in st.session_state:
                st.session_state[SPEC_CONFIRMATION_KEY] = True
            st.success(
                "Specification pair ready: "
                + " + ".join(item.detection.file_format.value.upper() for item in inputs)
            )
            baseline_confirmed = st.checkbox(
                "I confirm that the Existing specification is the approved baseline and may be used as read-only reference evidence.",
                key=BASELINE_CONFIRMATION_KEY,
            )
            roles_confirmed = st.checkbox(
                "Confirm files and run governed extraction",
                key=SPEC_CONFIRMATION_KEY,
            )
            if roles_confirmed and not baseline_confirmed:
                st.warning("Confirm the approved Existing baseline before running governed extraction.")
            if roles_confirmed and baseline_confirmed:
                try:
                    pair = parse_specification_pair(inputs)
                    with st.expander("Source document evidence"):
                        st.dataframe(source_block_rows(pair), width="stretch", hide_index=True)
                    if SPEC_REVIEWS_KEY not in st.session_state:
                        st.session_state[SPEC_REVIEWS_KEY] = confirm_existing_baseline(
                            build_common_review_views(pair)
                        )
                    else:
                        st.session_state[SPEC_REVIEWS_KEY] = confirm_existing_baseline(
                            st.session_state[SPEC_REVIEWS_KEY]
                        )
                    st.session_state[SPEC_REVIEWS_KEY] = add_manual_source_reviews(
                        pair, st.session_state[SPEC_REVIEWS_KEY]
                    )
                    restored_review = st.session_state.pop(DRAFT_REVIEW_RESTORE_KEY, None)
                    if restored_review is not None:
                        try:
                            candidate_reviews = restore_provisional_triage(
                                st.session_state, restored_review
                            )
                            st.session_state[SPEC_REVIEWS_KEY] = restore_draft_review_state(
                                add_manual_source_reviews(pair, st.session_state[SPEC_REVIEWS_KEY]),
                                candidate_reviews,
                            )
                        except (ValueError, ReviewError, KeyError) as error:
                            st.error(f"Saved review could not be restored safely: {error}")
                            st.stop()
                    views, resolved = render_reviews(st.session_state[SPEC_REVIEWS_KEY], pair)
                    active_for_draft = st.session_state.get("active_project_id")
                    if active_for_draft:
                        render_draft_controls(active_for_draft, recovered_files, views)
                    if resolved:
                        render_specification_snapshot(pair, views)
                except (ValueError, ReviewError) as error:
                    st.error(str(error))

else:
    st.subheader("Structured Project Data")
    st.caption("Upload XLSX, JSON, or the governed two-file CSV project-data contract.")
    uploaded_files = st.file_uploader(
        "Upload structured project data",
        type=["xlsx", "csv", "json"],
        accept_multiple_files=True,
        key="data_upload.structured_project_data",
        help="Supported: XLSX, JSON, or the governed project.csv + alternatives.csv pair.",
    )

    if uploaded_files:
        detections = [detect_upload(upload.name, upload.type, upload.getvalue()) for upload in uploaded_files]
        st.subheader("Detection and routing")
        st.dataframe(
            [
                {
                    "File": detection.filename,
                    "Detected format": detection.file_format.value.upper() if detection.file_format else "Rejected",
                    "Intended workflow": detection.workflow.value.replace("_", " ").title() if detection.workflow else "None",
                    "Status": detection.status.value.replace("_", " ").title(),
                    "Reason": detection.reason_code or "",
                }
                for detection in detections
            ],
            width="stretch",
            hide_index=True,
        )
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
            if len(structured_files) != len(uploaded_files):
                st.error("This workflow accepts structured project data only. Use the specification comparison workflow for DOCX or PDF files.")
            else:
                invalidate_structured_state_on_change(st.session_state, structured_files)
                try:
                    detected_format = validate_structured_batch(structured_files)
                    st.success(f"Detected structured project-data workflow: {detected_format.value.upper()}.")
                    if st.checkbox(
                        "Confirm that these files should be processed as structured project data",
                        key=STRUCTURED_CONFIRMATION_KEY,
                    ):
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
        st.write("No structured project data uploaded.")

with st.expander("Build U6 scope and limitations"):
    st.write("- Unified snapshots preserve document formats, hashes, parser versions and typed source locations")
    st.write("- Existing values are preserved as explicitly confirmed approved-baseline evidence")
    st.write("- Only reviewed Proposed values continue as candidate changes")
    st.write("- Canonical draft and unchanged canonical-validation result are preserved")
    st.write("- Persistence is additive, append-only and content-addressed")
    st.write("- Duplicate content, updates, deletes, archived projects and cross-project access are rejected")
    st.write("- No OCR, live AI, recommendation or decision automation")
