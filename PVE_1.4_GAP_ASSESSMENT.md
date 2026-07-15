# PVE 1.4 Pilot-Readiness Gap Assessment

## Assessment status

**Planning assessment: INITIAL BASELINE**

**Deployment readiness: NOT APPROVED**

**Pilot authorization: NOT GRANTED**

**Enterprise production-readiness certification: NOT GRANTED**

## Baseline

PVE 1.3 is a governance-closed reference implementation at commit `b28e6cc7716e1e693f2ca72d534f6e17bfc4ffe6`, released under tag `pve-v1.3`. It provides deterministic packaging decision support, evidence control, trials, changes, supplier-qualification evidence, governed demonstrations and automated regression. It does not provide production operating controls.

## Gap classification

- **Required before pilot:** mandatory for any separately authorized controlled pilot.
- **Required before production:** may be deferred from a limited pilot but is mandatory before production use.
- **Demonstration hardening:** improves interview and stakeholder usability without creating operational authority.
- **Prohibited in PVE 1.4:** outside this planning-only phase.

## Status model

- OPEN
- IN ANALYSIS
- SPECIFIED
- DEFERRED — APPROVED
- PROHIBITED
- CLOSED WITH EVIDENCE

A planning specification may move a gap to SPECIFIED. It does not move an operational gap to CLOSED WITH EVIDENCE.

## Capability-gap register

| ID | Domain | Current PVE 1.3 state | Gap | Classification | Target build | Provisional owner | Planned output | Current status | Required evidence |
|---|---|---|---|---|---:|---|---|---|---|
| P14-G01 | Identity and access | No enterprise authentication or RBAC | Named users, roles, least privilege and access reviews | Required before pilot | 2–3 | Security Owner | Identity and RBAC requirements specification | OPEN | Approved role model, access-control requirements and named-owner appointment evidence |
| P14-G02 | Approval workflow | Human decisions documented, but no enterprise workflow engine | Configurable approvals, delegation, escalation and segregation of duties | Required before pilot | 2 | Business Process Owner | Approval-flow and segregation-of-duties specification | OPEN | Reviewed approval matrix and exception-routing model |
| P14-G03 | Auditability | Strong repository and evidence records | Tamper-evident operational audit log, retention and review process | Required before pilot | 2 | Governance Owner | Audit-event and retention specification | OPEN | Reviewed event catalogue, retention rule and review ownership |
| P14-G04 | Data governance | Governed demo cases and controlled evidence | Data owner, classification, minimization, consent, retention, masking and deletion | Required before pilot | 3 | Data Owner | Pilot data-governance requirements | OPEN | Approved data inventory template, classification model and control requirements |
| P14-G05 | Security | No production security certification | Threat model, security review, secrets, vulnerability and incident controls | Required before pilot | 3 | Security Owner | Security requirements register and threat model | OPEN | Reviewed threat model and security evidence plan |
| P14-G06 | Privacy | No real-user or personal-data processing approved | Privacy impact assessment and approved processing basis | Required before pilot when applicable | 3 | Privacy Owner | Privacy-assessment requirements | OPEN | Approved applicability decision and required processing-basis evidence |
| P14-G07 | Integrations | Draft contracts and conceptual boundaries | Interface ownership, authentication, retries, reconciliation and monitoring | Required before connected pilot | 4 | Integration Owner | Controlled interface and reconciliation specifications | OPEN | Reviewed interface catalogue and no-live-connection confirmation |
| P14-G08 | Environment | Reference implementation only | Segregated pilot environment, configuration control, backups and recovery | Required before pilot | 3–4 | Technology Owner | Environment requirements specification | OPEN | Approved future-state topology and recovery requirements |
| P14-G09 | UAT | Automated tests and governed demonstrations | Named business users, scripted UAT, defect triage and acceptance sign-off | Required before pilot | 5 | UAT Owner | UAT framework | OPEN | Reviewed UAT plan, authority matrix and defect rules |
| P14-G10 | Value validation | Analytical savings and business outputs | Approved baseline, benefit owner, realization rules and finance validation | Required before pilot | 5 | Finance/Value Owner | Value-validation framework | OPEN | Approved formulas, baselines, evidence sources and claim states |
| P14-G11 | Support model | No production support commitment | Support hours, ownership, incident severity, escalation and SLA | Required before production | 6 | Service Owner | Pilot support-requirements section | OPEN | Reviewed support RACI and escalation model |
| P14-G12 | Observability | CI and evidence artifacts | Runtime logs, metrics, alerting, traceability and service health | Required before pilot | 3–4 | Technology Owner | Observability requirements specification | OPEN | Reviewed log, metric, alert and ownership requirements |
| P14-G13 | Scale and resilience | Not certified | Load, concurrency, failover and recovery evidence | Required before production; pilot threshold required | 4–5 | Technology Owner | Test-threshold specification | OPEN | Approved pilot thresholds and future production test requirements |
| P14-G14 | Legal and commercial | No operational terms | Data processing, confidentiality, IP, liability and usage terms | Required before pilot | 3 | Legal/Commercial Owner | Legal and commercial review checklist | OPEN | Reviewed checklist and named approval authority |
| P14-G15 | Change management | Strong source governance | Release calendar, training, communications and adoption ownership | Required before pilot | 5–6 | Change Owner | Change and adoption requirements | OPEN | Reviewed communication, training and ownership plan |
| P14-G16 | Demonstration quality | Strong governed reference implementation | Persona-based narrative, concise script, fallback path and evidence map | Demonstration hardening | 2 and 6 | Demo Owner | Controlled demo package | OPEN | Rehearsal evidence, fallback test and evidence-traceability map |

## Gap closure rules

A gap may be marked SPECIFIED when the required planning output has been reviewed and accepted.

A gap may be marked CLOSED WITH EVIDENCE only when:

1. the required operational control exists;
2. the named accountable owner is appointed;
3. the evidence is linked;
4. the acceptance authority records approval;
5. residual risks are recorded;
6. the closure does not rely solely on planning language.

PVE 1.4 is expected primarily to move gaps from OPEN to SPECIFIED. It does not authorize operational implementation.

## Architecture gaps

1. No approved trust-boundary model for users, systems and data stores.
2. No enterprise identity provider or authorization model.
3. No approved secrets-management or environment-configuration design.
4. No operational audit-event schema and retention design.
5. No production-grade integration runtime, reconciliation queue or dead-letter handling.
6. No approved environment topology for development, test, pilot and production.
7. No runtime monitoring, backup, recovery or service-management design.
8. No approved data residency, privacy or supplier-confidentiality controls.
9. No pilot acceptance, benefit-realization or support operating model.

## Demonstration-hardening opportunities

- Present a role-based scenario covering Packaging Engineer, Procurement Manager, Quality Reviewer and Approver.
- Show evidence traceability from input through analysis, trial, change and final human decision.
- Include a controlled failure scenario with reconciliation and named ownership.
- Add a concise executive decision page and a technical evidence appendix.
- Preserve visible synthetic/non-production labels and limitations throughout the demonstration.

## Planning conclusion

PVE 1.3 remains suitable for controlled demonstrations and architecture review only.

PVE 1.4 may produce complete specifications and an auditable future pilot recommendation. It cannot close operational identity, security, integration, environment, monitoring, support, real-user UAT or deployment gaps through documentation alone.

Deployment readiness remains NOT APPROVED.
Pilot authorization remains NOT GRANTED.
Enterprise production-readiness certification remains NOT GRANTED.
