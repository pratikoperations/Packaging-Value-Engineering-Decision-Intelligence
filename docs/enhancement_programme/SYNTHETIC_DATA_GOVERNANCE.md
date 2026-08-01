# Governed Synthetic Procurement Data Standard

## Purpose

Define realistic but fictional procurement data that exercises the application without implying real supplier, market or engineering validity.

## Mandatory controls

Every dataset must provide a manifest containing:

- `dataset_id`;
- `dataset_version`;
- `schema_version`;
- `dataset_type: synthetic_demo`;
- `generated_at`;
- deterministic `generation_method` and seed where applicable;
- `assumption_basis` and assumption-provenance category;
- `currency_basis`;
- `scenario_period`;
- `record_count`;
- `disclosure_version`;
- permitted use and prohibited commercial use.

Every record must include or inherit:

- deterministic governed identifier;
- fictional supplier identity;
- explicit unit and currency;
- scenario purpose;
- assumption category and provenance;
- effective or scenario date;
- permitted use;
- prohibited commercial use.

## Mandatory disclosure

> Synthetic demonstration data. Not sourced from actual suppliers. Not suitable for negotiation, supplier award, engineering approval, regulatory approval or realized-savings claims.

The disclosure must appear in dataset manifests, relevant UI surfaces and exported evidence.

## Planned dataset structure

- dataset manifest;
- fictional suppliers;
- packaging specifications;
- quotations and cost components;
- technical qualification results;
- risk events;
- scenario cases;
- invalid and contradictory cases.

## Minimum scenario set

1. lower price with technical and lead-time risk;
2. material reduction with potential savings and qualification threshold;
3. higher quoted price with lower total annualized cost.

## Minimum negative cases

- missing unit;
- inconsistent currency;
- expired quotation;
- negative cost;
- specification mismatch;
- missing technical result;
- duplicate quotation;
- unsupported unit conversion.

## Referential-integrity controls

Tests must detect duplicate IDs, orphaned supplier/specification/quotation/test references, unsupported currencies and units, cross-file count mismatches, invalid effective dates and non-deterministic fixture regeneration.

## Accidental real-data controls

A governed denylist and review step must detect accidental use of real company names, copied quotation identifiers, identifiable contacts, current-market claims or externally sourced certificates. Detection blocks acceptance until the record is removed or explicitly proven fictional.

## Prohibited content

- actual supplier names or identifiable quotations;
- claims that values represent current market rates;
- inferred SAP extracts;
- fabricated test certificates presented as real;
- realized savings;
- supplier award recommendations without human qualification.

## Acceptance evidence

Schema validation, manifest validation, disclosure tests, deterministic-regeneration checks, referential-integrity checks, accidental-real-name checks, scenario completeness tests and export checks must demonstrate continued synthetic status throughout the workflow.
