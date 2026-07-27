from __future__ import annotations

from dataclasses import asdict, replace
from typing import Any

import streamlit as st

from src.application.word_intake_demo import (
    ALIAS_REGISTRY_VERSION,
    EXTRACTION_SCHEMA_VERSION,
    PARSER_VERSION,
    PROVIDER_ID,
    DemoEvaluation,
    build_demo_reviews,
    demo_comparisons,
    demo_groups,
    load_synthetic_pair,
    synthetic_demo_documents,
)
from src.document_intake import DocumentPair, parse_document_pair
from src.intake_mapping import build_canonical_dataset_draft, build_confirmed_snapshot
from src.review_comparison import (
    CandidateReview,
    ReviewError,
    ReviewState,
    confirm,
    correct_and_confirm,
    intentionally_omit,
    reject,
)

SYNTHETIC_PROJECT = {
    "project_id": "PVE2-SYNTHETIC-WORD-DEMO",
    "project_name": "Synthetic Corrugated Word Intake Demonstration",
    "category": "corrugated_shipping_case",
    "annual_volume": 100000,
    "volume_unit": "cases_per_year",
    "currency": "INR",
    "status": "active",
    "archived_at": None,
}


def _review_key(review: CandidateReview) -> str:
    candidate = review.candidate
    return f"{candidate.document_role.value}:{candidate.field_name}:{candidate.source_block_id}"


def _load_documents() -> DocumentPair | None:
    st.subheader("1. Select synthetic documents")
    mode = st.radio(
        "Document source",
        ("Built-in synthetic pair", "Upload two synthetic DOCX files"),
        horizontal=True,
    )
    existing_demo, proposed_demo = synthetic_demo_documents()
    download_columns = st.columns(2)
    download_columns[0].download_button(
        "Download existing synthetic DOCX",
        existing_demo,
        "existing_synthetic.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
    )
    download_columns[1].download_button(
        "Download proposed synthetic DOCX",
        proposed_demo,
        "proposed_synthetic.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        width="stretch",
    )
    try:
        if mode == "Built-in synthetic pair":
            return load_synthetic_pair()
        upload_columns = st.columns(2)
        existing = upload_columns[0].file_uploader(
            "Existing synthetic specification",
            type=["docx"],
            key="pve2_existing_docx",
        )
        proposed = upload_columns[1].file_uploader(
            "Proposed synthetic specification",
            type=["docx"],
            key="pve2_proposed_docx",
        )
        if existing is None or proposed is None:
            st.info("Upload exactly one existing and one proposed synthetic DOCX.")
            return None
        return parse_document_pair(
            existing.name,
            existing.getvalue(),
            proposed.name,
            proposed.getvalue(),
        )
    except ValueError as error:
        st.error(str(error))
        return None


def _document_summary(documents: DocumentPair) -> None:
    rows = []
    for document in (documents.existing, documents.proposed):
        rows.append(
            {
                "Role": document.role.value.title(),
                "Filename": document.filename,
                "SHA-256": document.sha256,
                "Source blocks": len(document.blocks),
                "Unsupported content": len(document.unsupported_content),
            }
        )
    st.dataframe(rows, width="stretch", hide_index=True)
    for document in (documents.existing, documents.proposed):
        with st.expander(f"{document.role.value.title()} parsed source blocks"):
            st.dataframe(
                [
                    {
                        "Block ID": block.block_id,
                        "Type": block.block_type.value,
                        "Text": block.text,
                        "Section": block.location.section_title,
                        "Table": block.location.table_index,
                        "Row": block.location.row_index,
                        "Cell": block.location.cell_index,
                    }
                    for block in document.blocks
                ],
                width="stretch",
                hide_index=True,
            )


def _apply_review_actions(reviews: tuple[CandidateReview, ...]) -> tuple[CandidateReview, ...]:
    updated: list[CandidateReview] = []
    st.subheader("3. Human review")
    st.caption("Every accepted value requires an explicit confirmation. Original extraction evidence remains preserved.")
    for review in reviews:
        candidate = review.candidate
        key = _review_key(review)
        with st.expander(
            f"{candidate.document_role.value.title()} — {candidate.field_name.replace('_', ' ').title()} — {candidate.raw_value}"
        ):
            evidence_columns = st.columns(3)
            evidence_columns[0].metric("Confidence", f"{candidate.confidence:.0f}%")
            evidence_columns[1].metric("Band", candidate.confidence_band.value)
            evidence_columns[2].metric("Unit", candidate.unit or "Not recorded")
            st.write(f"**Source:** `{candidate.source_block_id}`")
            st.write(candidate.source_excerpt)
            if candidate.ambiguity_codes:
                st.warning(
                    "Ambiguities: "
                    + ", ".join(code.value for code in candidate.ambiguity_codes)
                )
            action = st.selectbox(
                "Review action",
                ("Pending", "Confirm", "Correct and confirm", "Intentionally omit", "Reject"),
                key=f"action:{key}",
            )
            try:
                if action == "Confirm":
                    updated.append(confirm(review, reviewer_note="Confirmed in synthetic demonstration"))
                elif action == "Correct and confirm":
                    corrected_value: Any = st.text_input(
                        "Corrected value", str(candidate.normalized_value), key=f"value:{key}"
                    )
                    corrected_unit = st.text_input(
                        "Corrected unit", candidate.unit or "", key=f"unit:{key}"
                    ) or None
                    note = st.text_input(
                        "Correction reason", "Corrected during synthetic review", key=f"note:{key}"
                    )
                    updated.append(
                        correct_and_confirm(
                            review,
                            corrected_value,
                            corrected_unit,
                            reviewer_note=note,
                        )
                    )
                elif action == "Intentionally omit":
                    updated.append(
                        intentionally_omit(review, reviewer_note="Omitted during synthetic review")
                    )
                elif action == "Reject":
                    updated.append(reject(review, reviewer_note="Rejected during synthetic review"))
                else:
                    updated.append(review)
            except ReviewError as error:
                st.error(str(error))
                updated.append(review)
    return tuple(updated)


def _comparison_rows(groups) -> list[dict[str, Any]]:
    rows = []
    for comparison in demo_comparisons(groups):
        rows.append(
            {
                "Field": comparison.field_name.replace("_", " ").title(),
                "Existing": comparison.existing.effective_value if comparison.existing else None,
                "Existing unit": comparison.existing.effective_unit if comparison.existing else None,
                "Proposed": comparison.proposed.effective_value if comparison.proposed else None,
                "Proposed unit": comparison.proposed.effective_unit if comparison.proposed else None,
                "Status": comparison.status.value,
                "Change": comparison.change,
                "Change %": comparison.change_percent,
            }
        )
    return rows


def main() -> None:
    st.set_page_config(page_title="PVE 2.0 AI-Assisted Word Intake", layout="wide")
    st.title("PVE 2.0 — AI-Assisted Word Specification Intake")
    st.caption("Controlled synthetic demonstration using deterministic mocked extraction")
    st.warning(
        "Synthetic portfolio demonstration only. No confidential documents, live AI provider, autonomous approval, engineering qualification or realized-savings claim."
    )

    documents = _load_documents()
    if documents is None:
        st.stop()

    parse_tab, extraction_tab, review_tab, comparison_tab, mapping_tab, evaluation_tab = st.tabs(
        ["Parse", "Extraction", "Review", "Comparison", "Canonical Draft", "Evaluation & Limits"]
    )

    reviews = build_demo_reviews(documents)
    with parse_tab:
        st.subheader("2. Deterministic parsing")
        _document_summary(documents)

    with extraction_tab:
        st.subheader("Mocked source-grounded extraction")
        st.info("This page uses deterministic label recognition. No external model or provider call is made.")
        st.dataframe(
            [
                {
                    "Role": review.candidate.document_role.value,
                    "Field": review.candidate.field_name,
                    "Raw value": review.candidate.raw_value,
                    "Normalized value": review.candidate.normalized_value,
                    "Unit": review.candidate.unit,
                    "Confidence": review.candidate.confidence,
                    "Ambiguity": ", ".join(code.value for code in review.candidate.ambiguity_codes) or "None",
                    "Source block": review.source.block_id,
                    "Source excerpt": review.source.excerpt,
                }
                for review in reviews
            ],
            width="stretch",
            hide_index=True,
        )

    with review_tab:
        reviewed = _apply_review_actions(reviews)
        st.session_state["pve2_reviewed_candidates"] = reviewed

    reviewed = st.session_state.get("pve2_reviewed_candidates", reviews)
    groups = demo_groups(reviewed)

    with comparison_tab:
        st.subheader("Existing versus proposed comparison")
        st.dataframe(_comparison_rows(groups), width="stretch", hide_index=True)
        unresolved = [
            f"{group.document_role.value}:{group.field_name}"
            for group in groups
            if group.selected_review is None
        ]
        if unresolved:
            st.warning("Unresolved fields: " + ", ".join(unresolved))
        else:
            st.success("All extracted candidates have a selected accepted value.")

    with mapping_tab:
        st.subheader("Confirmed-only canonical dataset draft")
        try:
            draft, issues, valid = build_canonical_dataset_draft(
                project=SYNTHETIC_PROJECT,
                groups=groups,
                source_repository="pratikoperations/Packaging-Value-Engineering-Decision-Intelligence",
                source_commit="draft-pr-54",
            )
            if valid:
                st.success("Canonical validation passed.")
            else:
                st.warning("Canonical draft remains incomplete or invalid. This is expected for a two-document intake demonstration.")
            if issues:
                st.dataframe(list(issues), width="stretch", hide_index=True)
            st.json(draft)
            snapshot = build_confirmed_snapshot(
                project_id=SYNTHETIC_PROJECT["project_id"],
                documents=documents,
                groups=groups,
                canonical_dataset_draft=draft,
                canonical_validation_issues=issues,
                canonical_validation_valid=valid,
                parser_version=PARSER_VERSION,
                extraction_schema_version=EXTRACTION_SCHEMA_VERSION,
                alias_registry_version=ALIAS_REGISTRY_VERSION,
                provider_id=PROVIDER_ID,
            )
            st.success("Immutable in-memory confirmed snapshot created.")
            snapshot_columns = st.columns(3)
            snapshot_columns[0].metric("Confirmed fields", len(snapshot.confirmed_fields))
            snapshot_columns[1].metric("Canonical valid", "Yes" if snapshot.canonical_validation_valid else "No")
            snapshot_columns[2].metric("Snapshot hash", snapshot.content_hash[:12] + "…")
            with st.expander("Snapshot evidence"):
                st.json(asdict(snapshot))
        except ValueError as error:
            st.warning(f"Snapshot is blocked until review is complete: {error}")

    with evaluation_tab:
        result = DemoEvaluation()
        st.subheader("Synthetic reference evaluation")
        metric_columns = st.columns(4)
        metric_columns[0].metric("Precision", f"{result.precision:.0%}")
        metric_columns[1].metric("Recall", f"{result.recall:.0%}")
        metric_columns[2].metric("Source grounding", f"{result.source_grounding:.0%}")
        metric_columns[3].metric("Role accuracy", f"{result.document_role_accuracy:.0%}")
        st.caption("Reference metrics apply to deterministic synthetic predictions, not a live AI model benchmark.")
        st.subheader("Limitations")
        st.markdown(
            """
- No live AI provider is connected.
- Only normal digital DOCX paragraphs and Word tables are supported.
- PDF, OCR, scanned content and image interpretation are excluded.
- The workflow does not approve packaging, suppliers, tests or savings.
- Confidential organisational documents are outside this portfolio demonstration.
- Engineering validation and documented human approval remain mandatory.
"""
        )


if __name__ == "__main__":
    main()
