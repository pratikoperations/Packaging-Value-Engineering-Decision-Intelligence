# Controlled Enhancement Effort Plan

## Programme ceiling

- Planned effort: 94 hours
- Contingency: 6 hours
- Absolute maximum: 100 hours
- Implementation status: not started

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

- record actual time by phase and task;
- do not automatically consume the full allocation;
- use contingency only for defects blocking mandatory acceptance;
- optional polish must be deferred before contingency is used;
- update forecast after every accepted feature PR;
- stop and seek authorization if forecast exceeds 100 hours.

## Scope-reduction order

If effort pressure develops, reduce scope in this order:

1. visual browser assertions and nonessential screenshots;
2. additional synthetic scenarios beyond the required three;
3. optional Calculation Evidence formulas outside the core whitelist;
4. presentation polish not required for acceptance.

Do not reduce:

- synthetic-data disclosure;
- evidence-engine independence;
- core reconciliation states;
- existing regression protection;
- exact-SHA and artifact evidence;
- desktop and Android-sized smoke coverage.

## Decision gates

- Gate 0: planning acceptance;
- Gate 1: governed synthetic-data acceptance;
- Gate 2: independent reconciliation acceptance;
- Gate 3: browser acceptance;
- Gate 4: integrated hosted acceptance and final freeze.

No feature implementation begins until Gate 0 is explicitly authorized.
