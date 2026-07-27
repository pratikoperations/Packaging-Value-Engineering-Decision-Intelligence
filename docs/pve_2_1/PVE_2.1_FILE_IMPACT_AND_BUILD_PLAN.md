# PVE 2.1 — Exact File Impact and Build Plan

## Planning-only status

This document authorizes no implementation. It defines the proposed repository impact for owner review.

## Proposed new files

### PDF intake adapter

```text
src/pdf_intake/__init__.py
src/pdf_intake/models.py
src/pdf_intake/file_validation.py
src/pdf_intake/searchability.py
src/pdf_intake/pdf_parser.py
src/pdf_intake/source_blocks.py
```

Purpose:

- validate digital PDFs;
- detect encrypted, malformed, scanned and image-only content;
- extract page-aware text;
- create stable PDF source blocks;
- return format-neutral parsed-document objects.

### Application integration

```text
src/application/pdf_intake_demo.py
pages/08_PVE_2_1_Digital_PDF_Intake.py
```

Purpose:

- provide a separate synthetic demonstration page;
- avoid modifying the approved PVE 2.0 Word page;
- reuse existing extraction, review, comparison, mapping and snapshot services.

### Evaluation corpus and metrics

```text
evaluation/pve_2_1_pdf/corpus_manifest.json
tests/fixtures/pve_2_1_pdf/
tests/pdf_intake/__init__.py
tests/pdf_intake/test_pdf_validation.py
tests/pdf_intake/test_pdf_parser.py
tests/pdf_intake/test_pdf_source_grounding.py
tests/application/test_pdf_intake_demo.py
tests/evaluation/test_pdf_intake_evaluation.py
```

Purpose:

- test searchable text extraction;
- test page ordering and block identity;
- test rejection of scanned/image-only, encrypted and malformed PDFs;
- test page-level grounding;
- preserve DOCX and existing PVE regressions.

### Documentation

```text
docs/pve_2_1/PVE_2.1_USER_GUIDE.md
docs/pve_2_1/PVE_2.1_EVALUATION_REPORT.md
docs/pve_2_1/PVE_2.1_LIMITATIONS.md
docs/pve_2_1/PVE_2.1_DEMO_GUIDE.md
```

## Proposed files to modify

### Dependency declaration

One existing dependency file may require an additive PDF parser dependency, selected only after a controlled comparison of candidates.

Potential choices:

- `pypdf` for text-first extraction and page access;
- `pdfplumber` when deterministic layout/bounding-box support is required.

Selection rule:

- prefer the smallest dependency that satisfies page-aware extraction and safe eligibility checks;
- do not add both unless evaluation proves both are required;
- no OCR dependency;
- no vision-model dependency.

### Format-neutral metadata

The following files may require additive, backward-compatible changes if the existing DOCX-specific names prevent clean PDF reuse:

```text
src/document_intake/document_models.py
src/intake_mapping/models.py
src/intake_mapping/snapshot.py
src/persistence/word_intake_migration.py
src/persistence/word_intake_repository.py
```

Preferred approach:

- avoid destructive renames;
- add generic document-format fields or a parallel PDF snapshot table;
- preserve all PVE 2.0 Word records and tests;
- use additive migration only.

The exact persistence choice must be approved before implementation:

1. **Parallel PDF table** — lowest regression risk, some duplication.
2. **Generic document-intake table** — cleaner long-term model, higher migration and compatibility risk.

Recommended first release: **parallel PDF snapshot table**.

## Files explicitly protected from modification

```text
src/data_models/validator.py
src/readiness/
src/thresholds/
src/scenarios/
src/technical_assessment/
src/decision/
```

Equivalent existing decision-engine modules are also protected even if directory names differ.

No PVE 2.1 work may alter:

- canonical validation rules;
- readiness scoring;
- business thresholds;
- scenario calculations;
- recommendation logic;
- approval logic;
- decision snapshots.

## Build groups

| Group | Scope | Hours |
|---|---|---:|
| A | Architecture, parser decision, security and eligibility contract | 4 |
| B | PDF validation, hashing, role assignment and scan/image-only detection | 5–7 |
| C | Page-aware deterministic parser and stable source blocks | 7–9 |
| D | Reuse existing extraction, review and comparison layers | 4–5 |
| E | Confirmed-only mapping and additive PDF snapshot persistence | 3–5 |
| F | Streamlit synthetic demonstration | 3–5 |
| G | Corpus, evaluation, regression and documentation | 3–5 |
| **Total** |  | **29–40** |

## Gate sequence

Each group requires owner approval before the next begins.

Mandatory gates:

- keep the PDF PR draft and unmerged;
- full regression suite after every implementation group;
- no live provider;
- no OCR;
- no image or drawing interpretation;
- no production or confidential-data claims;
- no tag, release or deployment without separate approval.

## Rollback

Before merge:

- close the draft PR;
- delete the PDF branch;
- merged PVE 2.0 main remains unchanged.

After any later authorized merge:

- revert the single squash merge;
- retain the PVE 2.0 Word feature independently;
- do not alter historical PVE 1.4 or PVE 2.0 SHAs.
