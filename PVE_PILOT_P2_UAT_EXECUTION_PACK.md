# PVE Pilot P2 — UAT Execution Pack

## Status

**Synthetic-only controlled portfolio UAT**

This pack authorizes no organizational pilot and no production use.

## Entry controls

Before execution:
- use only synthetic/sanitized approved evidence;
- confirm canonical Streamlit app;
- record source commit/version shown by the app where available;
- create/select a dedicated pilot project;
- no confidential/personal data;
- record start time before task execution;
- keep engineering approval separate from PVE recommendation.

## Mandatory scenarios

| ID | Scenario | Expected result | Severity if failed |
|---|---|---|---|
| UAT-01 | Create/select pilot project | dedicated project boundary established | S2 |
| UAT-02 | Upload Existing spec | Existing role fixed and evidence retained | S2 |
| UAT-03 | Upload Proposed spec | Proposed role fixed and evidence retained | S2 |
| UAT-04 | Review all 25 fields | every governed field present/missing is visible | S2 |
| UAT-05 | Correct one controlled field | correction requires human action and remains auditable | S2 |
| UAT-06 | Inspect provenance | changed technical value has source reference | S2 |
| UAT-07 | Commercially weak alternative | system does not force recommendation | S3 |
| UAT-08 | Commercially attractive + engineering blocker | blocker prevents approval implication | S1 |
| UAT-09 | Feasibility/readiness gate | readiness does not imply engineering approval | S1 |
| UAT-10 | Switch projects | no stale specification evidence crosses projects | S1 |
| UAT-11 | Scenario/commercial analysis | deterministic assumptions visible | S2 |
| UAT-12 | Export decision package | read-only package produced with boundaries | S2 |
| UAT-13 | Immutable history | accepted decision/evidence history not silently overwritten | S1 |
| UAT-14 | Resume project | retained state belongs to correct project | S2 |
| UAT-15 | Record final human disposition | human decision remains distinct from PVE recommendation | S1 |

## Defect severity

- **S1 Critical:** approval/governance breach, evidence leakage, immutable-history failure, material decision corruption.
- **S2 Major:** mandatory workflow cannot complete or evidence is materially incomplete.
- **S3 Moderate:** non-critical usability/clarity problem.
- **S4 Minor:** cosmetic/non-material issue.

Exit requires zero open S1/S2 defects.

## Human-authority comprehension questions

Participant must answer all correctly:

1. Does a PVE feasibility/readiness PASS technically approve a package? **No.**
2. Can PVE award or allocate a supplier? **No.**
3. Who owns technical approval? **Human packaging/engineering authority.**
4. Can estimated savings be called realized savings? **No.**
5. May missing evidence be ignored because savings are attractive? **No.**

## Rating questions

1–5 scale:
- workflow is understandable;
- missing evidence is visible;
- technical/commercial trade-offs are clear;
- source evidence is easy to inspect;
- final recommendation boundaries are clear;
- decision package is useful for review.

## Execution record

For each scenario capture:
- PASS/FAIL;
- start/end;
- evidence reference;
- defect ID if failed;
- observation;
- retest result;
- reviewer.
