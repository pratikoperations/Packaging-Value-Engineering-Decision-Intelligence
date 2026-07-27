# PVE 2.0 — AI-Assisted Word Specification Intake Architecture

## Status

Planning and architecture only. No runtime implementation is authorized by this document.

- Frozen baseline: `1f6f6ade9bb1370d8aace750b8e0e1cf63441dbe`
- Planning branch: `planning/pve-2-ai-word-intake`
- Main branch modification: prohibited
- Merge, tag, release, deployment and activation: prohibited
- Existing PVE validation, readiness, threshold, scenario and decision logic: unchanged

## Objective

Add a controlled intake adapter that compares one existing and one proposed corrugated-box `.docx` specification, extracts governed fields with source traceability and confidence, requires explicit human confirmation, and maps only confirmed values into the existing PVE canonical workflow.

The capability assists document interpretation. It does not approve a packaging design, replace laboratory evidence, infer missing facts, or authorize supplier or production decisions.

## Architectural principles

1. **Adapter, not rewrite.** Word intake terminates at a confirmed canonical draft. Existing PVE engines remain downstream and unchanged.
2. **Deterministic parsing before AI.** DOCX structure is extracted into ordered paragraphs, headings, tables and cells before model-based field interpretation.
3. **Source-grounded extraction.** Every proposed field must cite a source block, table and cell where applicable.
4. **No source, no acceptance.** A value without retrievable source evidence cannot be confirmed or mapped.
5. **Human confirmation is mandatory.** AI output is always a draft.
6. **Original and corrected values are both retained.** The audit record preserves extraction, correction and confirmation.
7. **Missing means missing.** The AI may not invent, estimate or silently default absent values.
8. **Technical and commercial boundaries remain separate.** Specification extraction cannot establish cost, annual volume, trial success or engineering approval unless separately supplied and governed.

## Target architecture

```text
Existing DOCX + Proposed DOCX
        |
        v
File validation and role assignment
        |
        v
Deterministic DOCX structural parser
(paragraphs, headings, tables, cells, order, source block IDs)
        |
        v
Document normalization
(whitespace, aliases, units, but no value invention)
        |
        v
AI structured extraction
(schema-constrained, source-grounded, ambiguity-aware)
        |
        v
Deterministic validation and confidence policy
        |
        v
Human review and correction interface
        |
        v
Confirmed intake snapshot
        |
        v
Canonical PVE mapping adapter
        |
        v
Existing validation, readiness, thresholds, scenarios and decisions
```

## Document workflow

1. User selects exactly one `existing` document and one `proposed` document.
2. System validates extension, MIME type, size, duplicate content and document readability.
3. Parser creates immutable ordered source blocks.
4. AI extracts candidate fields separately for each document.
5. System normalizes field names and units while preserving raw values.
6. Deterministic validators detect conflicts, unit problems, duplicate candidates and unsupported values.
7. Review interface presents existing and proposed values side by side with source evidence.
8. User confirms, corrects or omits each field.
9. System creates an immutable confirmed intake snapshot.
10. Mapping adapter creates a canonical PVE dataset draft from confirmed values only.
11. Existing PVE validation determines completeness, blockers and output availability.

## Governed field set

The first release supports 25 fields. Presence requirements are defined in the extraction contract.

### Identification

1. specification_number
2. specification_revision
3. item_code
4. item_description
5. supplier_name
6. effective_date

### Dimensions and design

7. box_style
8. internal_length
9. internal_width
10. internal_height
11. external_length
12. external_width
13. external_height
14. dimension_unit
15. joint_type
16. closure_method

### Material construction

17. ply_count
18. flute_combination
19. liner_gsm
20. medium_gsm
21. total_board_gsm
22. paper_grade
23. box_weight
24. box_weight_unit

### Performance

25. compression_requirement

The architecture permits later additions such as ECT, BCT, burst strength, Cobb, print method, coating and test standard, but they are excluded from the first governed contract unless separately authorized.

## Extraction object

Each candidate field must contain:

```json
{
  "field_name": "internal_length",
  "document_role": "existing",
  "raw_value": "420",
  "normalized_value": 420.0,
  "unit": "mm",
  "confidence": 0.97,
  "source_block_id": "existing:p18",
  "source_section": "Dimensions",
  "source_table": 2,
  "source_row": 4,
  "source_column": 2,
  "source_text": "Internal Length (mm) 420",
  "ambiguity_codes": [],
  "validation_status": "valid",
  "review_status": "pending"
}
```

## Source traceability model

Each parsed source block receives a stable identifier formed from:

- document role;
- document content hash;
- block type;
- ordered block index;
- table, row and column indexes where applicable.

A confirmed field must retain:

- original filename;
- SHA-256 document hash;
- document role;
- source block ID;
- section or heading context;
- table and cell coordinates where applicable;
- exact source excerpt;
- extraction timestamp;
- extraction engine and schema versions;
- reviewer action.

## Confidence and ambiguity policy

Confidence is extraction confidence, not probability of engineering correctness.

| Band | Policy |
|---|---|
| 0.90–1.00 | Candidate may be pre-filled; explicit human confirmation still required. |
| 0.70–0.89 | Review required and visually emphasized. |
| Below 0.70 | Blocked from canonical mapping until corrected and confirmed. |
| Conflicting candidates | Blocked until user selects or enters the governed value. |
| Missing source | Rejected. |
| Unsupported unit | Blocked until corrected. |

Mandatory ambiguity codes include:

- `multiple_candidates`
- `internal_external_unclear`
- `requirement_result_unclear`
- `unit_missing`
- `unit_conflict`
- `existing_proposed_role_unclear`
- `table_header_unclear`
- `embedded_image_only`
- `source_not_found`

## Human confirmation controls

Allowed review states:

- `pending`
- `confirmed`
- `corrected_confirmed`
- `intentionally_omitted`
- `rejected`

Canonical mapping accepts only `confirmed` and `corrected_confirmed` fields. An intentionally omitted mandatory field remains a readiness blocker.

The review record must preserve:

- candidate value;
- reviewer-entered value, if changed;
- reviewer action;
- action timestamp;
- correction reason where provided;
- source reference.

## Canonical PVE mapping boundary

The intake layer may:

- map confirmed specification identity, dimensions, construction and performance fields;
- preserve source classifications and document references;
- create a canonical dataset draft;
- invoke existing validation after mapping.

The intake layer may not:

- alter readiness scoring;
- change threshold profiles;
- change technical formulas;
- create or modify scenario logic;
- generate human approval;
- infer price, annual volume, supplier capability, laboratory results or realized savings;
- override evidence conflicts or technical blockers.

## Security, privacy and retention boundaries

Initial portfolio scope uses synthetic documents only.

Required controls:

1. Reject password-protected, macro-enabled or non-DOCX files.
2. Enforce configurable file-size and page/paragraph/table limits.
3. Compute a document hash before processing.
4. Do not execute embedded objects, links or macros.
5. Treat extracted text as untrusted input.
6. Prevent prompt injection in document text from altering extraction rules.
7. Do not log full document content in application logs.
8. Keep model credentials outside source control.
9. Default to session-scoped temporary storage for documents.
10. Persist only approved snapshots and minimum required source excerpts.
11. Publish a deletion and retention statement before any real organisational use.
12. Require an approved model provider and data-processing agreement before confidential data use.

## Failure handling

The workflow must fail closed when:

- either document is missing;
- both roles use the same file;
- DOCX structure cannot be parsed;
- source evidence cannot be linked;
- candidate values conflict materially;
- required units are unavailable;
- model output does not conform to schema;
- extraction provider is unavailable;
- the user has not completed confirmation.

Failure states must not create a canonical dataset or downstream decision record.

## Adoption boundary

This release is a controlled document-intelligence pilot for portfolio demonstration and evaluation. It is not production-ready and excludes authentication, enterprise storage, role-based approvals, confidential-data authorization, OCR, image interpretation, CAD interpretation, bulk processing and automated engineering approval.
