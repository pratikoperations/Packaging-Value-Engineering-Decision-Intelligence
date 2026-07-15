# PVE 1.4 Value Validation Framework

## Status and boundary

**Build 5 planning output: COMPLETE — PENDING REVIEW**

This document defines future KPI, baseline, formula, evidence, ownership and claim-state requirements only. It does not validate an operational baseline, measure production performance, execute a pilot, establish ROI, certify adoption, confirm productivity improvement or record realized benefit.

All examples are synthetic or explicitly controlled. No actual personal, supplier-confidential, pricing, contractual, drawing, test or commercial data is included.

## Explicit non-claim record

- Production KPI results claimed: 0
- Validated operational baselines: 0
- Pilot-observed results: 0
- Finance-validated benefits: 0
- Realized savings claims: 0
- ROI claims: 0
- Adoption claims: 0
- Productivity claims: 0
- Operational benefits recorded: 0

## Preserved governance boundaries

1. Finance/Value review is mandatory before value may be described as validated.
2. Analytical estimates cannot be represented as realized savings.
3. System-generated calculations are decision-support records, not commercial approval.
4. Technical, quality, data, privacy, security and reconciliation blockers cannot be overridden by value.
5. Supplier ranking, award, allocation and commercial approval remain outside PVE authority.
6. Build 3 classification, synthetic-data, no-personal-data and privacy requirements govern every value input.
7. Build 4 system-of-record, provenance, safe-failure and reconciliation requirements govern future data sources.
8. Build 6 retains final readiness, pilot recommendation and executive decision scope.

## Value claim-state model

| State | Meaning | Minimum future evidence | Build 5 example permission |
|---|---|---|---|
| Conceptual opportunity | Potential source of value identified | Business rationale and assumptions | Permitted with synthetic label |
| Analytical estimate | Formula applied to synthetic or approved assumptions | Variables, units, formula, source class and limitations | Permitted with synthetic label |
| Reviewed estimate | Analytical estimate independently reviewed for arithmetic and assumptions | Reviewer, review date, findings and controlled version | Permitted as a framework example only |
| Validated baseline | Baseline independently approved for future comparison | Approved scope, period, normalization and system-of-record evidence | Definition only; no Build 5 claim |
| Pilot-observed result | Separately authorized pilot has executed evidence | Approved pilot record, scenario evidence and measured result | Definition only; no Build 5 claim |
| Finance-validated benefit | Finance has reviewed executed evidence and calculation | Approved baseline, result, formula, exclusions and Finance decision | Definition only; no Build 5 claim |
| Realized value | Benefit appears in approved operational or financial records | Finance or operational ledger evidence, ownership and effective period | Definition only; prohibited as Build 5 claim |

A claim cannot skip states. Review of a synthetic estimate does not create a validated baseline, pilot result, Finance-validated benefit or realized value.

## Claim language controls

Allowed Build 5 wording:

- conceptual opportunity;
- synthetic analytical estimate;
- reviewed synthetic estimate;
- potential value subject to validation;
- future evidence required;
- not measured;
- not realized.

Prohibited Build 5 wording unless explicitly negated or described as a future state:

- saved;
- achieved;
- delivered;
- realized;
- validated benefit;
- proven ROI;
- production improvement;
- adoption achieved;
- productivity increased;
- Finance approved.

## Compact KPI catalogue

| KPI ID | Category | KPI | Business question | Build 5 status |
|---|---|---|---|---|
| KPI-01 | Procurement | Synthetic analytical material-cost opportunity | What theoretical unit-cost difference exists under stated assumptions? | Definition only |
| KPI-02 | Procurement | Normalized landed-cost difference | How would synthetic alternatives compare after stated cost components? | Definition only |
| KPI-03 | Packaging | Evidence completeness rate | Are required technical and commercial evidence fields available? | Definition only |
| KPI-04 | Packaging | Specification conflict rate | How often do controlled specification references conflict? | Definition only |
| KPI-05 | Quality | Validation-required rate | What proportion of synthetic assessments require further validation? | Definition only |
| KPI-06 | Quality | Technical-blocker detection rate | Are mandatory blockers surfaced rather than overridden? | Definition only |
| KPI-07 | Productivity | Future review cycle time | What future elapsed time would be measured from controlled intake to review-ready state? | Future baseline required |
| KPI-08 | Productivity | Manual review-step count | How many defined human review steps are required? | Definition only |
| KPI-09 | Governance | Decision-package completeness | Are required evidence, assumptions, limitations and review records present? | Definition only |
| KPI-10 | Governance | Traceability completeness | Are requirements, scenarios, evidence and decisions linked? | Definition only |
| KPI-11 | Governance | Reconciliation exception rate | How often do future source and destination records disagree? | Future connected evidence required |
| KPI-12 | Governance | Unresolved exception count | How many controlled exceptions remain without authorized disposition? | Definition only |

No KPI is represented as currently measured or achieved.

## KPI definition template

| Field | Requirement |
|---|---|
| KPI ID and version | Unique controlled reference |
| Business question | Decision the KPI supports |
| Definition | Unambiguous description |
| Numerator | Defined quantity and source |
| Denominator | Defined quantity and source where applicable |
| Unit | Currency, percentage, count, time or controlled unit |
| Scope | Included category, project, site, material or process |
| Baseline period | Future approved period |
| Comparison period | Future approved period |
| Data source and system of record | Authoritative future source class |
| Owner | Provisional benefit or process owner |
| Reviewer | Finance/Value or relevant independent reviewer |
| Formula | Controlled equation |
| Exclusions | Explicit exclusions and rationale |
| Assumptions | Visible and versioned assumptions |
| Normalization | Volume, mix, currency, specification and timing treatment |
| Frequency | Future measurement frequency |
| Evidence requirement | Minimum controlled evidence |
| Claim state | One permitted claim-state value |
| Confidence/uncertainty | Defined limitation or range |

## Baseline requirements

A future baseline must be:

1. relevant to the same business scope and decision;
2. time-bound and version-controlled;
3. sourced from an approved system of record or approved controlled evidence;
4. independently reviewed;
5. normalized for material volume, mix, currency, specification and timing where applicable;
6. protected from selective inclusion or exclusion;
7. distinguished from target, forecast, budget and supplier quotation;
8. linked to a named Baseline Owner and Finance/Value Reviewer;
9. approved before any value is described as validated;
10. accompanied by exclusions, assumptions, limitations and confidence.

Build 5 approves no operational baseline.

## Baseline record template

- baseline ID and version;
- business scope;
- category, packaging component or process;
- period;
- source and system-of-record owner;
- classification and privacy applicability;
- included and excluded records;
- currency and conversion basis;
- volume and mix normalization;
- specification and quality basis;
- one-time and recurring components;
- preparation owner;
- independent reviewer;
- approval status;
- evidence references;
- limitations and expiry/review date.

During Build 5, approval status remains `NOT VALIDATED — FUTURE EVIDENCE REQUIRED`.

## Formula-control requirements

Every value calculation must:

- expose all variables and units;
- identify each source or assumption;
- use consistent periods, currency and volume basis;
- separate gross and net value;
- separate one-time and recurring value;
- include implementation and transition cost where applicable;
- prevent double counting across projects and benefit categories;
- identify sensitivity and uncertainty;
- distinguish actual, forecast, target and assumption;
- show the applicable claim state;
- require independent Finance/Value review before validation;
- preserve technical, quality and governance blockers.

## Synthetic illustrative formulas

### Synthetic analytical material opportunity

```text
(synthetic current unit cost − synthetic proposed unit cost)
× synthetic annual volume
```

### Synthetic net analytical opportunity

```text
synthetic gross analytical opportunity
− synthetic implementation cost
− synthetic transition cost
```

### Synthetic avoided-cost opportunity

```text
synthetic forecast cost without action
− synthetic forecast cost with action
```

### Synthetic future cycle-time opportunity

```text
synthetic baseline processing time
− synthetic proposed processing time
```

These formulas create analytical examples only. They do not demonstrate actual savings, productivity or ROI.

## Value calculation record template

| Field | Requirement |
|---|---|
| Calculation ID and version | Controlled identifier |
| Opportunity/KPI ID | Linked KPI or value opportunity |
| Claim state | Current controlled state |
| Formula | Full equation |
| Variables and units | Each variable defined |
| Source or assumption | Evidence class for each input |
| Baseline reference | Approved future baseline or synthetic placeholder |
| Gross value | Before implementation and transition costs |
| Implementation cost | Future approved cost evidence |
| Transition cost | Future approved cost evidence |
| Net value | Gross less approved costs |
| One-time/recurring | Explicit classification |
| Period | Relevant calculation period |
| Sensitivity | Scenario or range where applicable |
| Double-counting check | Linked portfolio or project comparison |
| Technical/quality conditions | Required feasibility and validation conditions |
| Prepared by | Provisional role |
| Reviewed by | Independent Finance/Value Reviewer |
| Limitations | Missing or uncertain evidence |

## Evidence hierarchy

| Level | Evidence class | Permitted use |
|---|---|---|
| E1 | Approved operational or Finance record | Future realized-value evidence only |
| E2 | Approved system-of-record data | Future baseline or measured-result evidence |
| E3 | Validated pilot, trial or test evidence | Future observed-result evidence |
| E4 | Controlled analytical calculation | Analytical estimate |
| E5 | Supplier-declared information | Input requiring provenance and review |
| E6 | Explicit assumption | Scenario analysis only |
| E7 | Unavailable | No claim; result blocked or qualified |

A lower evidence class cannot be silently represented as a higher class.

## Provisional value ownership

| Role | Accountability | Cannot do alone |
|---|---|---|
| Opportunity Owner | Defines business opportunity and scope | Validate own benefit |
| Baseline Owner | Prepares and maintains future baseline evidence | Approve own baseline without review |
| Finance/Value Owner | Reviews formula, baseline, evidence and claim state | Establish realized value without operational evidence |
| Procurement Reviewer | Reviews commercial assumptions and sourcing boundary | Convert estimate into supplier award or allocation |
| Packaging Engineer | Reviews technical feasibility and required validation | Approve value when technical blocker remains |
| Data Owner | Reviews classification, provenance and allowed use | Approve uncontrolled data |
| Governance Reviewer | Reviews traceability, exceptions and double counting | Act as sole preparer and approver |
| Human Approval Authority | Records explicit business decision | Delegate decision to calculation or system output |

All roles remain provisional placeholders, not appointed people.

## Future review and sign-off sequence

```text
Define opportunity and scope
→ establish controlled baseline requirement
→ define KPI and formula
→ classify evidence and assumptions
→ perform technical, procurement and quality review
→ perform independent Finance/Value review
→ resolve conflicts, blockers and double counting
→ assign permitted claim state
→ named Human Approval Authority records decision
→ later operational evidence may support realization
```

Build 5 executes none of these future reviews or approvals.

## Claim-state transition controls

- Conceptual opportunity → analytical estimate requires a transparent formula and synthetic or approved assumptions.
- Analytical estimate → reviewed estimate requires independent review evidence.
- Reviewed estimate → validated baseline requires separately approved operational baseline evidence.
- Validated baseline → pilot-observed result requires separately authorized executed pilot evidence.
- Pilot-observed result → Finance-validated benefit requires Finance review of executed evidence.
- Finance-validated benefit → realized value requires approved operational or financial record evidence.

No transition beyond reviewed synthetic estimate is available from Build 5 evidence.

## Prohibited implementation and claims

Build 5 prohibits:

- production KPI claims;
- realized-savings or realized-benefit claims;
- proven ROI or adoption claims;
- measured productivity-improvement claims;
- real-user or pilot execution;
- live systems, endpoints, credentials, connectors or integrations;
- dashboards, telemetry or monitoring implementation;
- application code, tests, schemas, migrations, workflows, infrastructure, deployment, dependencies or datasets;
- actual confidential or personal data;
- supplier ranking, award, allocation or commercial approval;
- marking any operational gap or risk `CLOSED WITH EVIDENCE`.

## Build 5 limitations carried forward

- No operational baseline is validated.
- No KPI is measured in production.
- No pilot or user evidence exists.
- No Finance-validated or realized benefit exists.
- No benefit owner is appointed.
- No live data source or integration is authorized.
- Build 6 retains final readiness and pilot-decision scope.

## Acceptance intent

This framework is acceptable only as a synthetic, requirements-level value-validation package aligned primarily to P14-G10 and selected planning contributions to P14-G13 and P14-G15. It grants no value validation, pilot, deployment, production or commercial authority and closes no operational gap or risk with evidence.