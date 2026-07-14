# PVE 1.1 Excel Upload and Normalization

## Scope

Build 5 adds a controlled `.xlsx` preparation path alongside the existing JSON and CSV upload paths. Existing upload behavior and canonical dataset handling remain unchanged.

## Processing sequence

1. Open the workbook safely with `openpyxl`.
2. Require all eight approved sheets.
3. Convert worksheet rows into structured dictionaries.
4. Normalize project, baseline, proposed, commercial, logistics, quality-test, and document-register records.
5. Validate category, objective, change type, required values, units, numeric ranges, and source classifications.
6. Require a populated baseline and at least one populated proposal.
7. Return field-level validation issues.
8. Save only when no validation issues remain.

## Blocking controls

Invalid workbooks cannot be persisted as dataset versions. Blocking conditions include missing sheets or columns, category mismatch, unsupported objective/change type, missing mandatory values, missing baseline/proposal data, invalid numeric values, invalid units, and unsupported or absent source classifications for populated facts.

## Canonical compatibility

Excel intake produces a versioned `1.1-excel-intake` canonical envelope and reuses the existing immutable dataset repository. It retains the active project identity, adds structured intake values, test records, and document-register metadata, and keeps the recommendation status at `insufficient_data`. No autonomous approval or full technical-feasibility conclusion is produced.

## Explicit exclusions

This build does not add OCR, PDF/Word/image extraction, AI document interpretation, readiness scoring, commercial decision logic, deployment, Power BI, PostgreSQL reporting, ERP integration, or autonomous approval.
