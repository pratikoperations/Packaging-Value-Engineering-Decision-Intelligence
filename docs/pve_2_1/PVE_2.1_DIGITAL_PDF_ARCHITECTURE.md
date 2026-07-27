# PVE 2.1 — Digital PDF Specification Intake Architecture

## Baseline

PVE 2.1 starts from merged PVE 2.0 main SHA:

`d7248eccc38f86c2229fb419532fd0076c86afe9`

The original PVE 1.4 portfolio baseline remains historically preserved at:

`1f6f6ade9bb1370d8aace750b8e0e1cf63441dbe`

## Objective

Add controlled intake for exactly one existing and one proposed searchable digital PDF while reusing PVE 2.0 extraction, review, comparison, mapping, persistence and evaluation boundaries.

## Scope

### Supported

- `.pdf` only;
- searchable digital text PDFs;
- exactly one existing and one proposed document;
- page-level text extraction;
- stable page and text-block identifiers;
- page-level source evidence;
- reuse of the governed 25-field registry;
- reuse of confidence, ambiguity, review, comparison, canonical draft and immutable snapshot layers;
- deterministic or mocked extraction initially.

### Excluded

- OCR;
- scanned or image-only PDFs;
- photographs;
- handwritten notes;
- CAD or drawing interpretation;
- image-table interpretation;
- encrypted PDFs requiring passwords;
- live provider integration;
- confidential organisational documents;
- autonomous approval.

## Architecture

```text
Existing digital PDF + Proposed digital PDF
                    ↓
PDF file and security validation
                    ↓
Searchable-text eligibility check
                    ↓
Page-aware deterministic text extraction
                    ↓
Common source-block model
                    ↓
Existing PVE 2.0 extraction contract
                    ↓
Existing source-grounding and confidence controls
                    ↓
Existing human review and comparison
                    ↓
Existing confirmed-only canonical mapping
                    ↓
Existing immutable snapshot boundary
```

## Common source-block contract

The PDF adapter must emit the same conceptual evidence contract used by DOCX intake while adding PDF-specific location metadata:

- document role;
- filename;
- SHA-256 document hash;
- page number;
- block index within page;
- extraction order;
- exact source text;
- stable block ID;
- optional bounding box when provided deterministically by the selected parser;
- parser version.

Stable identifiers must be derived from document hash, role, page number, block index and parser version. Source text alone must not be the identifier.

## Searchable-text eligibility

A PDF is eligible only when:

- at least one page contains extractable text;
- extracted text exceeds a controlled minimum threshold;
- the majority of non-empty pages contain meaningful text;
- text is not limited to headers, watermarks or page numbers;
- the document is not encrypted or malformed.

Documents failing eligibility must be rejected with a clear classification such as:

- `scanned_or_image_only`;
- `insufficient_extractable_text`;
- `encrypted_pdf`;
- `malformed_pdf`;
- `unsupported_pdf_feature`.

No OCR fallback is permitted in PVE 2.1.

## Reuse boundary

PVE 2.1 must reuse without modification wherever possible:

- `config/pve_2_0_word_fields.json` or a format-neutral successor preserving the same 25 fields;
- `src/ai_extraction/`;
- `src/review_comparison/`;
- `src/intake_mapping/`;
- immutable snapshot and persistence controls;
- evaluation thresholds and claim boundaries.

Format-specific logic must remain isolated under a PDF intake adapter.

## Human-control requirements

- every accepted field must retain page-level evidence;
- no unconfirmed value may be mapped;
- low-confidence and ambiguous values remain blocked;
- page/source mismatch rejects the candidate;
- image-only content must be visibly reported as unsupported;
- the interface must not imply that PDF support includes scans or drawings.

## Security boundaries

- no JavaScript or embedded-action execution;
- no attachment execution;
- no password handling;
- bounded file size and page count;
- bounded extracted-text volume;
- temporary session-scoped processing for hosted demonstration;
- no full document content in logs;
- synthetic documents only until separate real-data authorization.

## Evaluation plan

Minimum corpus:

- 10 existing/proposed digital-PDF pairs;
- 20 PDFs;
- single-column, multi-column, table-like and mixed text layouts;
- malformed PDF cases;
- encrypted PDF cases;
- scanned/image-only rejection cases;
- low-text rejection cases;
- prompt-injection text cases;
- page-grounding tests;
- DOCX regression tests.

Acceptance gates remain:

- high-priority precision ≥95%;
- high-priority recall ≥90%;
- accepted-value page grounding =100%;
- document-role accuracy ≥98%;
- accepted invented values =0;
- accepted unsourced values =0;
- unconfirmed values mapped =0;
- PVE 2.0 regression failures =0.

## Estimated effort

| Workstream | Hours |
|---|---:|
| Architecture and parser selection | 4 |
| PDF validation and eligibility | 5–7 |
| Page-aware extraction and source blocks | 7–10 |
| Existing extraction/review integration | 4–6 |
| Streamlit demonstration integration | 4–6 |
| Evaluation, tests and documentation | 5–7 |
| **Total** | **29–40** |

## Release boundary

PVE 2.1 is a controlled digital-PDF intake extension. It must not be described as universal PDF, OCR or drawing support.
