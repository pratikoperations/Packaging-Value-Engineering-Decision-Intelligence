# PVE 1.1 Excel Template Standard

## Purpose

Generate category-specific, macro-free `.xlsx` workbooks for structured project intake. The workbook supports data collection and readiness assessment only; it does not provide engineering approval.

## Required sheets

1. INSTRUCTIONS
2. PROJECT
3. BASELINE
4. PROPOSED
5. COMMERCIAL
6. LOGISTICS
7. QUALITY_TESTS
8. DOCUMENT_REGISTER

## Generation inputs

Every workbook is generated from:

- packaging category
- project objective
- category-specific change type

Unsupported category, objective, or change-type combinations are rejected before workbook generation.

## Requirement display

- Mandatory rows use red highlighting.
- Recommended rows use amber highlighting.
- Optional rows use grey highlighting.

## Structured metadata

Applicable sheets include:

- field key and label
- requirement level
- value and accepted unit
- description and example
- source classification
- evidence reference
- supplier or laboratory
- test date
- validation status

## Source classifications

- uploaded_fact
- manually_entered_fact
- supplier_declared
- laboratory_tested
- predicted
- assumption

Dropdown validation is used where practical for source classification, requirement, context, verification, upload, and validation status.

## Governance

- No macros.
- A filename is not proof of verification.
- Supplier-declared and predicted values are not laboratory-tested values.
- Missing critical evidence remains blocking.
- Engineering validation and human approval remain mandatory.
- Existing JSON and CSV upload workflows are unchanged by Build 4.

## Compatibility

Templates are generated using `openpyxl`. Build 4 adds workbook generation only. Parsing, normalization, upload persistence, and canonical dataset conversion remain deferred to Build 5.
