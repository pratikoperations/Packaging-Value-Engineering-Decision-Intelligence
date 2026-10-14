# PVE Pilot P2 — Baseline Measurement Pack

## Status

**P2 planning status: CONTROLLED MEASUREMENT METHOD**

**Pilot execution:** NOT YET STARTED

**Permitted evidence:** synthetic-only or explicitly sanitized evidence

## Purpose

Freeze the baseline measurement method before any PVE-assisted pilot execution so productivity or value results cannot be selected retrospectively.

## Comparison design

Two executions of the same bounded corrugated lightweighting case are required:

1. **Manual baseline** — analyst prepares the decision package without using PVE decision-support outputs.
2. **PVE-assisted run** — analyst uses the governed PVE Existing-versus-Proposed workflow and current deterministic analysis.

Both runs must use the same synthetic/sanitized:
- Existing specification;
- Proposed specification;
- annual volume;
- unit-cost inputs;
- technical requirements;
- evidence set;
- scenario assumptions.

## Timing rules

Record separately:
- wall-clock elapsed time;
- active analyst hands-on time;
- waiting/idle time;
- correction/rework time.

Start event:
- analyst receives the complete permitted pilot evidence pack.

Stop event:
- review-ready decision summary and evidence package are produced.

Do not include repository build/development time in either baseline.

## Baseline measures

| Measure | Definition |
|---|---|
| Elapsed decision-preparation time | minutes from start event to stop event |
| Hands-on analyst time | active working minutes |
| Source-document count | unique evidence documents used |
| Manual transfer count | values copied/retyped between sources/tools |
| Reconciliation count | fields needing explicit comparison/correction |
| Clarification loops | discrete returns to source evidence for missing/unclear inputs |
| Calculation rework events | recalculation caused by data/assumption correction |
| Time to first high-priority blocker | minutes until first known critical/major blocker is identified |
| Executive-summary preparation time | active minutes spent creating final review summary |
| Claims with explicit evidence | material decision claims with source/provenance linkage |
| Unresolved assumptions | assumptions still open at review-ready state |

## Fair-comparison rules

- identical case scope;
- identical permitted evidence;
- same analyst unless documented otherwise;
- same definitions and counting rules;
- no post-hoc removal of inconvenient observations;
- every excluded interval requires a reason;
- PVE execution cannot use information unavailable to the manual baseline;
- manual baseline may use common office tools but not PVE outputs.

## Evidence record

Every measurement record must contain:
- run ID;
- mode: MANUAL_BASELINE or PVE_ASSISTED;
- start/end timestamp;
- analyst identifier or controlled portfolio role;
- case identifier;
- evidence-pack version;
- each raw metric;
- observation notes;
- anomalies/exclusions;
- reviewer status.

## Baseline acceptance

Baseline is VALIDATED BASELINE only when:
- measurement record is complete;
- definitions above were followed;
- evidence-pack version is fixed;
- no confidential/personal data entered;
- anomalies are disclosed;
- reviewer confirms comparability.

Otherwise it remains ESTIMATE.
