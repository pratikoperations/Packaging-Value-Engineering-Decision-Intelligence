# PVE 2.1 — Digital PDF Intake User Guide

## Purpose

PVE 2.1 demonstrates controlled intake of exactly one existing and one proposed searchable synthetic PDF. It is a portfolio workflow, not a production document-processing service.

## Supported documents

- searchable digital PDF only;
- one existing and one proposed specification;
- meaningful selectable text;
- up to the governed size and page limits.

The workflow rejects scanned/image-only, encrypted, malformed and insufficient-text PDFs. It does not use OCR.

## Demonstration workflow

1. Open **PVE 2.1 — Digital PDF Specification Intake**.
2. Use the built-in synthetic pair or download and re-upload both PDFs.
3. Inspect file eligibility, hashes, page count and source blocks.
4. Review deterministic extraction candidates with page and block evidence.
5. Confirm, correct and confirm, intentionally omit, or reject each candidate.
6. Inspect the existing-versus-proposed comparison.
7. Review the confirmed-only canonical draft and existing validation issues.
8. Create the immutable in-memory PDF snapshot and inspect its content hash.
9. Review evaluation evidence and explicit limitations.

## Review actions

- **Confirm:** accept the normalized extracted value.
- **Correct and confirm:** preserve the original extraction and record a corrected accepted value.
- **Intentionally omit:** exclude the value with a documented reason.
- **Reject:** reject the candidate with a documented reason.
- **Pending:** blocks snapshot completion.

## Five-minute demonstration path

| Time | Demonstration |
|---|---|
| 0:00–0:40 | Business problem, searchable-PDF scope and governance boundary |
| 0:40–1:25 | Validation, hashes, page-aware parsing and layout warnings |
| 1:25–2:10 | Deterministic source-grounded extraction |
| 2:10–3:10 | Human confirmation and correction |
| 3:10–3:50 | Existing-versus-proposed comparison |
| 3:50–4:35 | Canonical draft, validation issues and immutable snapshot |
| 4:35–5:00 | Evaluation boundary and limitations |

## Mandatory claim boundary

> This demonstration proves governed searchable-PDF intake, page-level traceability, human review, deterministic comparison and immutable evidence handling. It does not prove live-model accuracy, OCR, engineering qualification, autonomous approval, production security or realized savings.
