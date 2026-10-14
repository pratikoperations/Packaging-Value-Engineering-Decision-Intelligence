# PVE Pilot Validation & Enterprise Readiness — P1 RACI

## Status

This RACI governs the bounded portfolio pilot. It does not imply organizational authority where none has been independently established.

| Activity | Portfolio Pilot Owner | Procurement Lead | Packaging Engineer | Finance / Value | Data / Governance | Security / Technology | UAT Owner | Deployment Authority |
|---|---|---|---|---|---|---|---|---|
| Pilot scope | A/R | C | C | C | C | C | C | I |
| Existing specification selection | C | R | A for technical baseline | I | C | I | I | I |
| Proposed specification review | C | C | A/R | I | I | I | C | I |
| Commercial assumptions | C | A/R | C | C | I | I | I | I |
| Evidence classification | C | C | C | I | A/R | C | I | I |
| Technical blocker disposition | I | C | A/R | I | I | I | C | I |
| Baseline KPI method | A | R | C | A/R for monetary validation | C | I | C | I |
| UAT execution | A | C | C | I | I | I | R | I |
| Defect disposition | A | C | C | I | C | C | R | I |
| Pilot value synthesis | A | R | C | A/R when Finance validation claimed | I | I | C | I |
| Enterprise-readiness review | A | C | C | C | C | A/R | C | I |
| Deployment decision | I | I | I | I | I | C | I | A/R |

Legend:
- **R** Responsible
- **A** Accountable
- **C** Consulted
- **I** Informed

## Separation rules

1. Procurement cannot substitute for packaging engineering approval.
2. Portfolio ownership cannot be presented as independent Finance validation.
3. UAT coordination cannot be presented as independent real-user acceptance.
4. Security/technology readiness cannot be self-certified without a qualified reviewer if enterprise claims are made.
5. Deployment authority remains separate from pilot success.

## Current named-role limitation

For the portfolio pilot, Pratik Patil may coordinate scope, procurement interpretation, synthetic evidence governance and UAT execution. Independent engineering, Finance/value and enterprise-security sign-off remain **TBD** unless explicitly supplied later.

That limitation does not block synthetic portfolio validation but it blocks claims of organizational pilot acceptance, Finance-validated benefit, enterprise production readiness or deployment authorization.
