# Controlled Enhancement Effort Plan

## Programme ceiling

- Planned total programme effort: 94 hours
- Contingency: 6 hours
- Absolute maximum: 100 hours
- Planning/governance effort consumed: record actual separately; do not infer from allocation
- Feature implementation effort consumed: 0 hours at this planning stage

All programme work, including planning, corrections, implementation, verification and closure, counts toward the 100-hour maximum unless separately reauthorized.

## Phase budgets

| Phase | Scope | Planned hours |
|---|---|---:|
| 0 | Governance, architecture and baseline | 5 |
| 1 | Playwright browser acceptance | 24 |
| 2 | Governed synthetic procurement data | 25 |
| 3 | Independent Calculation Evidence reconciliation | 32 |
| 4 | Integration, regression and acceptance | 8 |
|  | **Planned total** | **94** |
|  | Contingency | **6** |
|  | **Maximum** | **100** |

## Effort accounting rules

- record actual planning and implementation time separately by task;
- report combined actual and estimate-to-complete at every gate;
- do not automatically consume the full allocation;
- use contingency only for defects blocking mandatory acceptance;
- defer optional polish before using contingency;
- update forecast after every accepted feature PR;
- stop and seek authorization if the combined forecast exceeds 100 hours.

## Cumulative forecast gates

| Gate | Deliverable state | Maximum cumulative forecast |
|---|---|---:|
| Gate 0 | Corrected planning accepted | 7 h |
| Gate 1 | Governed synthetic data accepted | 30 h |
| Gate 2 | Independent reconciliation accepted | 68 h |
| Gate 3 | Browser acceptance completed | 90 h |
| Gate 4 | Integrated acceptance and closure | 100 h |

Crossing a gate threshold triggers immediate scope reduction before further implementation. It does not automatically authorize contingency use.

## Scope-reduction order

1. visual browser assertions and nonessential screenshots;
2. synthetic scenarios beyond the required three;
3. optional Calculation Evidence formulas outside the core whitelist;
4. presentation polish not required for acceptance;
5. browser coverage beyond Chromium desktop and one Android-sized viewport.

Do not reduce synthetic disclosure, evidence-engine independence, core reconciliation states, existing regression protection, exact-SHA/artifact evidence, export-content validation, or desktop and Android-sized smoke coverage.

## Decision gates

- Gate 0: planning acceptance;
- Gate 1: governed synthetic-data acceptance;
- Gate 2: independent reconciliation acceptance;
- Gate 3: browser acceptance;
- Gate 4: integrated hosted acceptance and final freeze.

No feature implementation or feature-branch creation begins until Gate 0 is explicitly authorized. PR #79 remains draft and must close without merge after planning acceptance.
