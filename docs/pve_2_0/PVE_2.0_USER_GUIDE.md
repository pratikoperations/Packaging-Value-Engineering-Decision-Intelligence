# PVE 2.0 — Synthetic Word Intake User Guide

## Purpose

This page demonstrates a controlled path from one existing and one proposed synthetic corrugated-box DOCX specification to a source-traceable, human-reviewed comparison and canonical dataset draft.

It is a portfolio demonstration. It is not a production document-processing service, packaging approval tool or supplier-qualification system.

## Open the page

Run the Streamlit application and open:

`PVE 2.0 — AI-Assisted Word Specification Intake`

## Workflow

1. Select the built-in synthetic pair or download and re-upload the two supplied synthetic DOCX files.
2. Review file hashes, parsed headings, paragraphs, tables and cells.
3. Review deterministic mocked extraction candidates.
4. Confirm, correct and confirm, intentionally omit or reject each candidate.
5. Review the existing-versus-proposed comparison.
6. Open the canonical-draft tab.
7. Review existing canonical-validation issues.
8. Create and inspect the immutable in-memory confirmed snapshot.
9. Review the synthetic evaluation metrics and claim limitations.

## Review controls

- `Confirm`: accepts the normalized extracted value.
- `Correct and confirm`: preserves the original extraction and records the corrected value.
- `Intentionally omit`: removes the candidate from mapping with a recorded reason.
- `Reject`: rejects the candidate and preserves its source evidence.
- `Pending`: blocks accepted mapping.

## Expected validation outcome

The canonical draft may remain invalid because the historical canonical validator expects one baseline and at least three alternatives. The Word intake demonstration supplies one existing and one proposed specification and does not invent additional alternatives.

## Five-minute demonstration path

### 0:00–0:40 — Problem and boundary

Explain that specifications often arrive in Word tables and free text, creating manual comparison effort and data-lineage risk. State that the demonstration uses only synthetic data and no live AI provider.

### 0:40–1:30 — Controlled intake and parsing

Load the built-in pair. Show document roles, hashes and stable paragraph/table-cell source blocks.

### 1:30–2:20 — Source-grounded extraction

Show field candidates, normalized values, units, confidence and exact source evidence. Explain that the deterministic mock represents the governed provider boundary rather than a production accuracy claim.

### 2:20–3:20 — Human review

Confirm several fields and correct one value. Show that the original extraction is preserved. State that no accepted value bypasses human confirmation.

### 3:20–4:10 — Comparison

Show unchanged dimensions, changed ply/flute construction, lower box weight and changed compression requirement. Do not state that the proposed box is technically acceptable.

### 4:10–4:45 — Canonical draft and snapshot

Show the partial canonical dataset, validation blockers and immutable content hash.

### 4:45–5:00 — Claim boundary

State: the workflow proves governed intake, source traceability, human review, deterministic comparison and immutable evidence handling. It does not prove production-model accuracy, engineering qualification, autonomous approval or realized savings.

## Prohibited use

Do not upload confidential organisational data. Do not use scanned documents, PDFs, image-only specifications or live supplier documentation in this portfolio release. Engineering validation and documented human approval remain mandatory.
