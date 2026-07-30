from __future__ import annotations

from typing import Any

import streamlit as st
from src.application.presentation import flatten_evidence_rows
from src.application.pdf_intake_demo import (
    ALIAS_REGISTRY_VERSION,
    EXTRACTION_SCHEMA_VERSION,
    PROVIDER_ID,
    PdfDemoEvaluation,
    build_pdf_demo_reviews,
    load_synthetic_pdf_pair,
    synthetic_pdf_documents,
)
from src.document_intake import DocumentRole
from src.pdf_intake import (
    PdfValidationError,
    build_confirmed_pdf_snapshot,
    build_pdf_canonical_dataset_draft,
    compare_pdf_review_groups,
    parse_validated_pdf,
    validate_pdf,
)
from src.review_comparison import ReviewError, confirm, correct_and_confirm, group_reviews, intentionally_omit, reject

PROJECT = {
    "project_id": "PVE21-SYNTHETIC-PDF-DEMO",
    "project_name": "Synthetic Corrugated PDF Intake Demonstration",
    "category": "corrugated_shipping_case",
    "annual_volume": 100000,
    "volume_unit": "cases_per_year",
    "currency": "INR",
    "status": "active",
    "archived_at": None,
}


def _load_documents():
    st.subheader("1. Select searchable synthetic PDFs")
    existing_demo, proposed_demo = synthetic_pdf_documents()
    columns = st.columns(2)
    columns[0].download_button("Download existing synthetic PDF", existing_demo, "existing_synthetic.pdf", "application/pdf", width="stretch")
    columns[1].download_button("Download proposed synthetic PDF", proposed_demo, "proposed_synthetic.pdf", "application/pdf", width="stretch")
    mode = st.radio("Document source", ("Built-in synthetic pair", "Upload two synthetic PDFs"), horizontal=True)
    if mode == "Built-in synthetic pair":
        return load_synthetic_pdf_pair()
    uploads = st.columns(2)
    existing = uploads[0].file_uploader("Existing searchable PDF", type=["pdf"], key="pve21_existing")
    proposed = uploads[1].file_uploader("Proposed searchable PDF", type=["pdf"], key="pve21_proposed")
    if existing is None or proposed is None:
        st.info("Upload exactly one existing and one proposed searchable synthetic PDF.")
        return None
    try:
        existing_doc = parse_validated_pdf(validate_pdf(existing.name, existing.getvalue(), DocumentRole.EXISTING, mime_type=existing.type))
        proposed_doc = parse_validated_pdf(validate_pdf(proposed.name, proposed.getvalue(), DocumentRole.PROPOSED, mime_type=proposed.type))
        return existing_doc, proposed_doc
    except PdfValidationError as error:
        st.error(str(error))
        return None


def _review(reviews):
    updated = []
    for item in reviews:
        review = item.review
        candidate = review.candidate
        key = f"{candidate.document_role.value}:{candidate.field_name}:{candidate.source_block_id}"
        with st.expander(f"{candidate.document_role.value.title()} — {candidate.field_name.replace('_', ' ').title()} — {candidate.raw_value}"):
            metrics = st.columns(4)
            metrics[0].metric("Page", item.page_number)
            metrics[1].metric("Block", item.pdf_block_index)
            metrics[2].metric("Confidence", f"{candidate.confidence:.0f}%")
            metrics[3].metric("Unit", candidate.unit or "Not recorded")
            st.write(f"**Source block:** `{candidate.source_block_id}`")
            st.write(item.raw_source_text)
            if item.layout_warnings:
                st.warning("Layout warnings: " + ", ".join(w.value for w in item.layout_warnings))
            if candidate.ambiguity_codes:
                st.warning("Ambiguities: " + ", ".join(code.value for code in candidate.ambiguity_codes))
            action = st.selectbox("Review action", ("Pending", "Confirm", "Correct and confirm", "Intentionally omit", "Reject"), key=f"pdf-action:{key}")
            try:
                if action == "Confirm":
                    updated.append(confirm(review, reviewer_note="Confirmed in synthetic PDF demonstration"))
                elif action == "Correct and confirm":
                    value: Any = st.text_input("Corrected value", str(candidate.normalized_value), key=f"pdf-value:{key}")
                    unit = st.text_input("Corrected unit", candidate.unit or "", key=f"pdf-unit:{key}") or None
                    note = st.text_input("Correction reason", "Corrected during synthetic PDF review", key=f"pdf-note:{key}")
                    updated.append(correct_and_confirm(review, value, unit, reviewer_note=note))
                elif action == "Intentionally omit":
                    updated.append(intentionally_omit(review, reviewer_note="Omitted during synthetic PDF review"))
                elif action == "Reject":
                    updated.append(reject(review, reviewer_note="Rejected during synthetic PDF review"))
                else:
                    updated.append(review)
            except ReviewError as error:
                st.error(str(error))
                updated.append(review)
    return tuple(updated)


def main() -> None:
    st.set_page_config(page_title="PVE 2.1 Digital PDF Intake", layout="wide")
    st.title("PVE 2.1 — Digital PDF Specification Intake")
    st.caption("Controlled searchable-PDF demonstration using deterministic mocked extraction")
    st.warning("Synthetic portfolio demonstration only. No confidential documents, OCR, live AI provider, autonomous approval, engineering qualification or realized-savings claim.")
    documents = _load_documents()
    if documents is None:
        st.stop()
    bundle = build_pdf_demo_reviews(documents)
    parse_tab, extraction_tab, review_tab, comparison_tab, mapping_tab, evaluation_tab = st.tabs(["Parse", "Extraction", "Review", "Comparison", "Canonical Draft", "Evaluation & Limits"])
    with parse_tab:
        st.subheader("2. PDF validation and page-aware source blocks")
        st.dataframe([{"Role": d.role.value.title(), "Filename": d.filename, "SHA-256": d.sha256, "Pages": d.page_count, "Blocks": len(d.blocks), "Warnings": ", ".join(w.value for w in d.warnings) or "None"} for d in documents], width="stretch", hide_index=True)
        for document in documents:
            with st.expander(f"{document.role.value.title()} page-aware blocks"):
                st.dataframe([{"Page": b.page_number, "Block": b.block_index, "Order": b.extraction_order, "Block ID": b.block_id, "Raw text": b.raw_text, "Normalized text": b.normalized_text, "Warnings": ", ".join(w.value for w in b.warnings) or "None"} for b in document.blocks], width="stretch", hide_index=True)
    with extraction_tab:
        st.info("Deterministic label recognition only. No external AI call is made.")
        st.dataframe([{"Role": e.review.candidate.document_role.value, "Field": e.review.candidate.field_name, "Raw value": e.review.candidate.raw_value, "Normalized": e.review.candidate.normalized_value, "Unit": e.review.candidate.unit, "Confidence": e.review.candidate.confidence, "Page": e.page_number, "Block": e.pdf_block_index, "Source ID": e.review.source.block_id, "Ambiguity": ", ".join(c.value for c in e.review.candidate.ambiguity_codes) or "None"} for e in bundle.reviews], width="stretch", hide_index=True)
    with review_tab:
        reviewed = _review(bundle.reviews)
        st.session_state["pve21_pdf_reviews"] = reviewed
    reviewed = st.session_state.get("pve21_pdf_reviews", tuple(item.review for item in bundle.reviews))
    groups = group_reviews(reviewed)
    with comparison_tab:
        comparisons, summary = compare_pdf_review_groups(groups, [group.field_name for group in groups])
        st.dataframe([{"Field": c.field_name, "Existing": c.existing.effective_value if c.existing else None, "Existing unit": c.existing.effective_unit if c.existing else None, "Proposed": c.proposed.effective_value if c.proposed else None, "Proposed unit": c.proposed.effective_unit if c.proposed else None, "Status": c.status.value, "Change": c.change, "Change %": c.change_percent} for c in comparisons], width="stretch", hide_index=True)
        if summary.unresolved_fields:
            st.warning("Unresolved fields: " + ", ".join(summary.unresolved_fields))
        else:
            st.success("All extracted PDF candidates have resolved review states.")
    with mapping_tab:
        try:
            draft, issues, valid = build_pdf_canonical_dataset_draft(project=PROJECT, groups=groups, source_repository="pratikoperations/Packaging-Value-Engineering-Decision-Intelligence", source_commit="draft-pr-55")
            st.success("Canonical validation passed.") if valid else st.warning("Canonical draft remains incomplete or invalid, which is expected for a two-PDF demonstration.")
            if issues:
                st.dataframe(list(issues), width="stretch", hide_index=True)
            st.dataframe(flatten_evidence_rows(draft), width="stretch", hide_index=True)
            snapshot = build_confirmed_pdf_snapshot(project_id=PROJECT["project_id"], documents=documents, groups=groups, canonical_dataset_draft=draft, canonical_validation_issues=issues, canonical_validation_valid=valid, extraction_schema_version=EXTRACTION_SCHEMA_VERSION, alias_registry_version=ALIAS_REGISTRY_VERSION, provider_id=PROVIDER_ID)
            st.success("Immutable in-memory PDF snapshot created.")
            metrics = st.columns(3)
            metrics[0].metric("Confirmed fields", len(snapshot.confirmed_fields))
            metrics[1].metric("Canonical valid", "Yes" if valid else "No")
            metrics[2].metric("Snapshot hash", snapshot.content_hash[:12] + "…")
            with st.expander("Snapshot evidence"):
                st.dataframe(flatten_evidence_rows(snapshot), width="stretch", hide_index=True)
        except ValueError as error:
            st.warning(f"Snapshot is blocked until review is complete: {error}")
    with evaluation_tab:
        result = PdfDemoEvaluation()
        metrics = st.columns(4)
        metrics[0].metric("Precision", f"{result.precision:.0%}")
        metrics[1].metric("Recall", f"{result.recall:.0%}")
        metrics[2].metric("Source grounding", f"{result.source_grounding:.0%}")
        metrics[3].metric("Role accuracy", f"{result.role_accuracy:.0%}")
        st.caption("These are deterministic synthetic-reference results, not a live-model benchmark.")
        st.markdown("""
### Rejection demonstrations and limitations
- Scanned or image-only PDFs are rejected; OCR is not attempted.
- Encrypted, malformed, oversized and insufficient-text PDFs are rejected.
- Multi-column and table-like layouts generate warnings; layout reconstruction is not claimed.
- No image, drawing, CAD or handwritten interpretation is performed.
- No autonomous packaging, supplier, test or savings approval is produced.
- Engineering validation and documented human approval remain mandatory.
""")


if __name__ == "__main__":
    main()
