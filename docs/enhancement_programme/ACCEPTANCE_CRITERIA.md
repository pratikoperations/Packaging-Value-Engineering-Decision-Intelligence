# Controlled Enhancement Acceptance Criteria

## Baseline preservation

- frozen source SHA remains `2954c293ca09882cadd7f23b5862f50334170a11`;
- `main` remains unchanged;
- original frozen showcase branch is not moved;
- existing regression baseline does not regress;
- primary business-engine outputs do not change without separate authorization.

## Browser acceptance

- all 13 pages are accessible;
- direct navigation and four sidebar groups remain correct;
- five-minute route completes;
- synthetic disclosure and Capabilities & Limits remain visible;
- Markdown and JSON downloads complete;
- desktop and Android-sized viewport tests pass;
- no visible uncaught Streamlit exception;
- CI retains useful browser artifacts.

## Synthetic-data acceptance

- every dataset is explicitly synthetic;
- no real supplier identity or implied current market rate;
- three complete positive scenarios;
- at least five invalid or contradictory cases;
- units, currencies, assumptions and dates are explicit;
- schemas and disclosure tests pass;
- exports preserve synthetic limitations.

## Calculation Evidence acceptance

- evidence implementation is independent of primary calculation functions;
- formula registry is versioned;
- supported and unsupported calculations are explicit;
- unit normalization, rounding and tolerances are tested;
- MATCH, WARNING, FAIL and NOT SUPPORTED states are demonstrated;
- deliberate mismatches are detected;
- primary and independent results and variance are visible;
- no engineering, commercial or realized-savings validation claim is made.

## Programme acceptance

- total actual effort does not exceed 100 hours;
- complete existing regression passes;
- all new feature-specific tests pass;
- hosted desktop and Android acceptance passes;
- exact final SHA and artifacts are recorded;
- original frozen branch and evidence history remain retained;
- enhanced version is published through a separate accepted branch;
- production readiness is not claimed.

## Stop rule

Failure of any mandatory acceptance criterion blocks final programme acceptance unless a documented scope reduction is separately authorized.
