# PVE 2.0 — Extraction and Canonical Mapping Contract

## Status

Architecture contract only. No implementation is authorized.

## Supported document contract

- Format: `.docx` only
- Documents per intake: exactly two
- Roles: one `existing`, one `proposed`
- Language: English
- Content: digitally generated paragraphs and Word tables
- Excluded: `.doc`, PDF, scanned pages, OCR, embedded-image-only specifications, CAD drawings, handwriting and bulk intake

## Required structural parser output

```json
{
  "document_id": "uuid",
  "document_role": "existing",
  "filename": "existing_spec.docx",
  "sha256": "...",
  "paragraph_count": 42,
  "table_count": 3,
  "blocks": [
    {
      "block_id": "existing:p1",
      "block_type": "paragraph",
      "order": 1,
      "heading_context": "General",
      "text": "Specification No: CB-101"
    }
  ]
}
```

The structural parser performs no engineering interpretation.

## Field definitions

| Field | Type | Unit | Initial requirement | Canonical destination |
|---|---|---|---|---|
| specification_number | string | — | Optional | specification identity |
| specification_revision | string | — | Optional | specification identity |
| item_code | string | — | Required | item identity |
| item_description | string | — | Required | item identity |
| supplier_name | string | — | Optional | source context only |
| effective_date | date | ISO-8601 | Optional | specification identity |
| box_style | enum/string | — | Required | corrugated specification |
| internal_length | decimal | mm | Required | dimensions |
| internal_width | decimal | mm | Required | dimensions |
| internal_height | decimal | mm | Required | dimensions |
| external_length | decimal | mm | Optional | dimensions |
| external_width | decimal | mm | Optional | dimensions |
| external_height | decimal | mm | Optional | dimensions |
| dimension_unit | enum | mm/cm/in | Required | dimensions |
| joint_type | enum/string | — | Optional | converting profile |
| closure_method | enum/string | — | Optional | converting profile |
| ply_count | integer | ply | Required | material construction |
| flute_combination | string | — | Required | material construction |
| liner_gsm | structured list | gsm | Conditionally required | material construction |
| medium_gsm | structured list | gsm | Conditionally required | material construction |
| total_board_gsm | decimal | gsm | Optional | material construction |
| paper_grade | structured list/string | — | Optional | material construction |
| box_weight | decimal | g | Required for material comparison | physical analysis |
| box_weight_unit | enum | g/kg | Required when box_weight exists | physical analysis |
| compression_requirement | decimal/string | governed source unit | Conditionally required | performance requirement |

## Alias policy

Aliases may help identify candidates but must not change the source text. Example aliases:

- `L`, `Length`, `Internal Length`, `ID Length`
- `W`, `Width`, `Internal Width`, `ID Width`
- `H`, `Height`, `Internal Height`, `ID Height`
- `Board GSM`, `Total GSM`, `Grammage`
- `Flute`, `Fluting`, `Flute Combination`
- `Case Weight`, `Box Weight`, `Unit Weight`

The alias registry must be versioned, reviewable and tested. User corrections do not automatically modify the registry.

## AI extraction response contract

The AI response must conform to a strict JSON schema and may return only:

- candidate fields;
- source references;
- confidence;
- ambiguity codes;
- missing-field list;
- unsupported-content list.

It may not return:

- approval decisions;
- inferred missing values;
- supplier rankings;
- cost or savings assumptions;
- laboratory conclusions;
- ungrounded recommendations.

## Unit normalization

Normalization rules must be deterministic and reversible.

Examples:

- cm to mm: conversion permitted with original value retained;
- kg to g: conversion permitted with original value retained;
- inch to mm: conversion permitted with original unit retained;
- missing unit: do not assume; flag `unit_missing`;
- conflicting units: block and flag `unit_conflict`.

## Comparison contract

The comparison layer outputs, per field:

```json
{
  "field_name": "box_weight",
  "existing": {"value": 780, "unit": "g", "review_status": "confirmed"},
  "proposed": {"value": 650, "unit": "g", "review_status": "confirmed"},
  "change": -130,
  "change_percent": -16.6667,
  "comparison_status": "changed",
  "technical_interpretation": "not_generated"
}
```

Allowed comparison statuses:

- `unchanged`
- `changed`
- `existing_missing`
- `proposed_missing`
- `both_missing`
- `unit_conflict`
- `not_comparable`

## Confirmation and snapshot contract

A confirmed intake snapshot must include:

- both document identities and hashes;
- parser version;
- extraction schema version;
- model/provider identifier where applicable;
- alias registry version;
- every candidate and source reference;
- every user correction;
- final review state;
- canonical mapping result;
- content hash;
- creation timestamp.

The snapshot is append-only. Reprocessing creates a new snapshot rather than mutating an accepted record.

## Canonical mapping rules

1. Map only `confirmed` or `corrected_confirmed` fields.
2. Preserve raw source values and normalized values separately.
3. Preserve source classification as uploaded document evidence, not laboratory-tested fact.
4. Do not convert supplier declarations into validated evidence.
5. Do not populate commercial inputs from specification documents unless a future governed contract explicitly authorizes them.
6. Do not populate human approval fields.
7. Do not bypass existing canonical validation.
8. Any missing required field remains visible as a downstream blocker.

## Decision boundary

The output of this adapter is a **confirmed canonical dataset draft**. It is not:

- an approved specification;
- a technical qualification;
- an engineering recommendation;
- a production release;
- a supplier decision;
- a realized-savings record.
