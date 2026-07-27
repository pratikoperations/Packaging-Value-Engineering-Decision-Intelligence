# Unified Data Upload — Build U1

## Baseline

- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Base main SHA: `ed5627e44686d88025136afb44f017d1e170b249`
- Branch: `feature/unified-data-upload-u1`

## Scope

Build U1 introduces the navigation, detection and format-neutral model foundation only.

It does not invoke the existing structured-data, DOCX or PDF processing workflows.

## User-facing navigation

Primary labels are task-based:

- Home
- Project Dashboard
- Guided Workflow
- Data Upload
- Business Rules & Thresholds
- Scenario Analysis
- Decision Records

Historical version-labelled Word and PDF pages remain preserved in the repository but are not registered in the explicit public navigation.

## Detection contract

The Data Upload page accepts:

- XLSX
- CSV
- JSON
- DOCX
- searchable PDF

Detection uses:

1. extension;
2. MIME compatibility;
3. binary or package signature;
4. structural validation;
5. searchable-text eligibility for PDF.

## Routing preview

- XLSX, CSV and JSON → structured project-data workflow
- DOCX and searchable PDF → specification-comparison workflow

The page displays detected format, intended workflow, status and whether an existing/proposed role will be required.

## Mixed-format specification contract

Approved pair classifications:

- PDF + PDF
- DOCX + DOCX
- PDF existing + DOCX proposed
- DOCX existing + PDF proposed

The format-neutral document and source-block models preserve:

- document role;
- document format;
- SHA-256;
- parser name and version;
- raw and normalized source text;
- format-specific source location;
- warnings.

## Restrictions retained

- no OCR;
- no live AI provider;
- no workflow execution in U1;
- no snapshot migration;
- no changes to the 25-field registry;
- no changes to canonical validation, readiness, thresholds, scenarios, recommendation or decision logic;
- no tag, release, deployment or merge.
