# Controlled Enhancement Programme Architecture

## Status

Planning only. No implementation is authorized by this document.

## Frozen source

- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Frozen source branch: `showcase-handoff-development`
- Frozen source SHA: `2954c293ca09882cadd7f23b5862f50334170a11`
- Programme branch: `enhancement/browser-data-calculation-programme`

The frozen branch must not move during programme development. Planning PR #79 is a review comparison only and must never merge into `showcase-handoff-development`; after planning acceptance it must close without merge.

## Programme objective

Improve interview and portfolio credibility through three bounded capabilities:

1. automated browser acceptance using Playwright;
2. governed realistic synthetic procurement data;
3. independent Calculation Evidence reconciliation.

## Architecture boundaries

### Browser acceptance layer

A separate browser-test layer starts the Streamlit application locally at an ephemeral port for CI acceptance and may target the hosted application only for final smoke validation. Tests supplement rather than replace the existing regression suite.

### Synthetic data layer

Synthetic scenarios remain isolated under a dedicated namespace. Every dataset and record must declare or inherit `dataset_type: synthetic_demo`, deterministic governed identifiers, schema and dataset versions, generation method, assumption provenance, explicit units and currency, and prohibited commercial-use metadata.

### Independent Calculation Evidence layer

A separate evidence engine independently maps raw inputs, applies separately owned and versioned formulas, normalizes units, calculates supported results using decimal arithmetic, and reconciles them against primary-engine outputs.

The evidence engine must not import or call primary calculation functions, calculation helpers, rounding helpers, precomputed intermediates or normalized values from the primary engine when raw inputs are available. It may share immutable input models, governed enumerations and transport objects. Primary outputs may be consumed only after independent calculation completes.

## Core calculation scope

- material quantity and cost;
- conversion cost;
- process loss or wastage;
- freight;
- tooling amortization;
- total unit cost;
- annualized cost;
- potential savings;
- percentage variance.

Unsupported calculations must return `NOT SUPPORTED` rather than an inferred result.

## Explicit exclusions

- SAP, Oracle, Ariba or Coupa integration;
- real supplier or quotation data;
- authentication or role management;
- enterprise database or immutable ledger;
- SourceMate redesign;
- production monitoring or security certification;
- autonomous approval, supplier award or negotiation;
- production-readiness claims.

## Target outcome

The programme should improve the showcase rating from approximately 8.8/10 to 9.3–9.4/10 while remaining a governed prototype rather than a production platform.
