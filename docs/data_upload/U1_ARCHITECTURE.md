# Unified Data Upload Architecture — Builds U1–U6

## Baseline

- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Base main SHA: `ed5627e44686d88025136afb44f017d1e170b249`
- Draft branch: `feature/unified-data-upload-u1`
- Draft PR: `#56`

## User-facing navigation

The public navigation is task-based:

1. Home
2. Project Dashboard
3. Guided Workflow
4. Data Upload
5. Business Rules & Thresholds
6. Scenario Analysis
7. Decision Records
8. Capabilities & Limits

Historical version-labelled upload, Word-intake and PDF-intake pages remain in the repository for compatibility and regression evidence, but are not registered in public navigation.

## Unified upload flow

```text
Upload
→ detect file type
→ validate structure and eligibility
→ identify intended workflow
→ request lightweight confirmation
→ route to the existing governed backend
```

Supported inputs:

- XLSX
- CSV
- JSON
- DOCX
- searchable PDF

Detection uses extension, MIME compatibility, binary/package signature, structural validation and searchable-text eligibility for PDF.

## Structured project-data route

- XLSX routes to the existing Excel upload service.
- JSON routes to the existing JSON upload service.
- CSV retains the governed `project.csv` + `alternatives.csv` contract.
- Existing canonical validation, readiness and immutable dataset-save behaviour are reused.
- Structured state is invalidated when the uploaded file set changes.

## Specification route

Exactly two documents are required:

- one Existing specification;
- one Proposed specification.

Supported combinations:

- PDF + PDF
- DOCX + DOCX
- PDF + DOCX
- DOCX + PDF

Each document preserves format, filename, SHA-256, parser name, parser version, warnings and format-specific source locations.

## Governed extraction and review

- Extraction is deterministic and limited to the existing 25-field registry.
- Existing aliases, grounding, confidence, ambiguity and review controls are reused.
- Review states are Pending, Confirmed, Corrected Confirmed, Intentionally Omitted and Rejected.
- Corrected numeric values are typed before mapping.
- File, role and pair-format changes invalidate confirmation and review state.

## Confirmed-only canonical mapping

Only Confirmed and Corrected Confirmed values enter the existing canonical mapping boundary.

Pending, Rejected and Intentionally Omitted values are excluded. The existing canonical validator runs unchanged and may return invalid or insufficient-data outcomes where supporting business and engineering evidence is absent.

## Unified immutable snapshot

The additive unified snapshot preserves:

- exactly one Existing and one Proposed document;
- pair format;
- document format, filename, hash and parser metadata;
- accepted raw, normalized, corrected and effective field values;
- source excerpt, block ID and typed PDF/DOCX location;
- extraction schema and alias-registry versions;
- canonical draft and validation result;
- deterministic content hash.

Persistence uses the additive `unified_specification_snapshots` table. It does not migrate or delete historical Word or PDF snapshot tables.

Controls include:

- append-only repository API;
- database update/delete triggers;
- duplicate project/content-hash rejection;
- foreign-key and archived-project protection;
- cross-project read protection.

## Mobile presentation boundary

The Data Upload journey uses a single-column control flow with full-width tables and action buttons. No nested column layout is used on the upload page. This reduces horizontal control compression on mobile, although hosted-device verification remains a separate release gate.

## Restrictions retained

- no OCR or image-only PDF support;
- no drawing, chart or embedded-image interpretation;
- no live AI provider;
- no autonomous approval or supplier award;
- no changes to the 25-field registry;
- no changes to canonical validation, readiness, thresholds, scenarios, recommendations or decision logic;
- no migration or deletion of existing snapshot tables;
- no tag, release, deployment or merge without separate authorization.
