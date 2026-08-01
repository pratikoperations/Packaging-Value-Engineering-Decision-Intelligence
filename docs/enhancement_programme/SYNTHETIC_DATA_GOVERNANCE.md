# Governed Synthetic Procurement Data Standard

## Purpose

Define realistic but fictional procurement data that exercises the application without implying real supplier, market or engineering validity.

## Mandatory controls

Every dataset and record must include or inherit:

- `dataset_type: synthetic_demo`;
- fictional supplier identity;
- explicit unit and currency;
- scenario purpose;
- assumption category;
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

## Prohibited content

- actual supplier names or identifiable quotations;
- claims that values represent current market rates;
- inferred SAP extracts;
- fabricated test certificates presented as real;
- realized savings;
- supplier award recommendations without human qualification.

## Acceptance evidence

Schema validation, disclosure tests, scenario completeness tests and export checks must demonstrate continued synthetic status throughout the workflow.
