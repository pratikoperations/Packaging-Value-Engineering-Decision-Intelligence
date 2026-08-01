# Independent Calculation Evidence Standard

## Objective

Define how Calculation Evidence independently recalculates supported results and reconciles them against the primary engine.

## Independence rule

The evidence engine must not import, call or wrap primary calculation functions. It must independently:

1. map the input snapshot;
2. normalize units;
3. select a versioned formula;
4. calculate the result;
5. apply documented rounding;
6. compare against the primary result.

Primary outputs may be consumed only for reconciliation after independent calculation is complete.

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

Every supported calculation must declare:

- calculation ID;
- formula version;
- formula expression;
- required inputs;
- accepted units;
- output unit;
- rounding rule;
- tolerance;
- limitations;
- effective version date.

## Reconciliation states

- `MATCH`: variance within tolerance;
- `WARNING`: variance exceeds normal tolerance but remains below the failure threshold;
- `FAIL`: material unexplained variance;
- `NOT SUPPORTED`: no independent formula is authorized.

## Evidence output

Each result must show the input snapshot, formula ID and version, primary result, independent result, absolute and percentage variance, tolerance, reconciliation state, assumptions and synthetic-data limitation where applicable.

## Prohibited shortcuts

- reusing the primary-engine function;
- copying the primary result into the evidence result;
- silently converting unsupported calculations;
- hiding rounding differences;
- treating a match as commercial or engineering validation.

## Acceptance proof

Static import checks, independent unit tests, deliberately divergent test fixtures and reconciliation-state tests must demonstrate that the evidence engine can detect mismatches rather than merely reproduce the primary output.
