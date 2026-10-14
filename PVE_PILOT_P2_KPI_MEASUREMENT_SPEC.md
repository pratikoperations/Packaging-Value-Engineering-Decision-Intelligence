# PVE Pilot P2 — KPI Measurement Specification

## Status

KPI definitions are frozen before pilot execution.

## Productivity KPIs

| KPI | Formula | Target |
|---|---|---:|
| Decision-preparation effort reduction | (baseline hands-on min - PVE hands-on min) / baseline hands-on min | >=25% |
| Executive-summary time reduction | (baseline summary min - PVE summary min) / baseline summary min | >=30% |
| Manual-transfer reduction | (baseline transfers - PVE transfers) / baseline transfers | >=40% |
| Rework reduction | (baseline rework - PVE rework) / baseline rework | target >=20%; must not increase |

Zero denominators must be reported as NOT COMPUTABLE, never forced to 0% or 100%.

## Governance / quality KPIs

| KPI | Numerator | Denominator | Target |
|---|---|---|---:|
| Specification completeness visibility | governed fields explicitly present/missing | 25 governed fields per document | 100% |
| Evidence traceability | material claims with explicit source/provenance | all material decision claims | >=95% |
| High-priority blocker detection | seeded/known high-priority blockers surfaced before recommendation | all seeded/known high-priority blockers | 100% |
| Human-authority comprehension | mandatory approval-boundary questions answered correctly | mandatory questions | 100% |
| Cross-project isolation | evidence leakage events | project-switch isolation attempts | 0 events |
| Unsupported approval claims | autonomous/implied approval outputs | reviewed outputs | 0 events |

## UAT KPIs

- mandatory scenario completion: 100%;
- open Severity-1 defects at exit: 0;
- open Severity-2 defects at exit: 0;
- workflow clarity: >=4/5 average;
- evidence visibility usefulness: >=4/5 average.

## Claim-state controls

Allowed:
- ESTIMATE
- VALIDATED BASELINE
- PILOT-MEASURED
- FINANCE-VALIDATED

Rules:
- baseline cannot become VALIDATED BASELINE without comparable evidence;
- pilot result cannot become PILOT-MEASURED without raw measurement evidence;
- monetary result cannot become FINANCE-VALIDATED without an independent Finance/Value reviewer;
- no phase result may be described as realized production savings without implementation evidence.

## KPI integrity controls

- preserve raw values;
- calculate deltas deterministically;
- never overwrite baseline measurements;
- document exclusions;
- separate elapsed from hands-on time;
- report target failures as failures, not narrative qualifications;
- do not average away a critical governance failure.
