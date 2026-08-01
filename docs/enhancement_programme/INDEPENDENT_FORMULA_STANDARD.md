# Independent Calculation Evidence Standard

## Objective

Define how Calculation Evidence independently recalculates supported results and reconciles them against the primary engine.

## Independence rule

The evidence engine must independently map raw inputs, normalize units, select a versioned formula, calculate the result, apply documented rounding and compare against the primary result. Primary outputs may be consumed only after independent calculation completes.

## Permitted sharing

- immutable raw input models;
- governed unit and currency enumerations;
- result transport objects;
- non-calculation validation interfaces.

## Prohibited sharing

- primary calculation functions or wrappers;
- calculation or rounding helpers used by the primary engine;
- precomputed intermediate values;
- primary normalized values when raw inputs are available;
- formula constants not independently owned and versioned by the evidence registry;
- copied primary outputs as evidence outputs.

## Numeric standard

- use decimal arithmetic for currency and governed quantities;
- declare precision and quantization per formula;
- define whether rounding occurs at intermediate or final stage;
- use explicit rounding mode;
- define absolute, relative or combined tolerance per calculation;
- zero denominators return a governed error or `NOT SUPPORTED`, never silent infinity;
- negative values are accepted only where the formula and scenario explicitly authorize them;
- unsupported signs or invalid costs fail validation;
- live currency conversion is excluded;
- a fixed synthetic exchange rate may be used only when explicitly authorized, versioned and disclosed.

## Planned supported calculations

- material quantity and cost;
- conversion cost;
- process loss or wastage;
- freight;
- tooling amortization;
- total unit cost;
- annualized cost;
- potential savings;
- percentage variance.

## Formula registry requirements

Every supported calculation declares calculation ID, formula version and expression, required raw inputs, accepted units, output unit, precision, rounding stage and mode, tolerance type and values, sign rules, limitations and effective version date.

## Reconciliation states

- `MATCH`: variance within tolerance;
- `WARNING`: variance exceeds normal tolerance but remains below failure threshold;
- `FAIL`: material unexplained variance;
- `NOT SUPPORTED`: no independent formula is authorized.

## Independent fixtures and proof

Evidence fixtures must be separately owned from primary-engine expected-result fixtures. Static import checks, dependency-boundary tests, deliberately divergent fixtures, mutation tests and reconciliation-state tests must prove that the evidence engine detects mismatches rather than reproducing primary output.

## Evidence output

Each result shows raw input snapshot, formula ID/version, primary result, independent result, absolute and percentage variance, tolerance, reconciliation state, assumptions and synthetic-data limitation where applicable. A match is not commercial, engineering or realized-savings validation.
