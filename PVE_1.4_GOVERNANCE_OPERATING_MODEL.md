# PVE 1.4 Governance and Demonstration Operating Model

## Status and boundary

**Build 2 planning output: COMPLETE — PENDING REVIEW**

This document specifies a future controlled operating model. It does not implement authentication, RBAC, workflow tooling, audit logging, integrations, deployment, real-user access or production controls. All roles below are provisional role placeholders, not appointed people or evidence of operational authority.

System outputs are decision-support records only. They cannot constitute engineering approval, procurement approval, supplier approval, sourcing award, allocation or commercial approval.

## Minimum role model

| Role | Primary accountability | Cannot do alone |
|---|---|---|
| Project Owner | Defines opportunity, scope, objectives and required decision | Approve own final decision without independent review |
| Packaging Engineer | Owns technical requirements, evidence review, validation plan and engineering recommendation | Override technical blockers for commercial benefit |
| Procurement Reviewer | Reviews cost, supply, supplier evidence and commercial assumptions | Rank, award or allocate suppliers through PVE |
| Quality Reviewer | Reviews defects, complaints, test evidence, trial outcomes and quality risks | Approve unresolved evidence conflicts |
| Finance/Value Reviewer | Reviews baselines, formulas and claim state | Present analytical savings as realized value |
| Data Owner | Defines allowed data, classification and evidence ownership | Authorize uncontrolled confidential or personal data |
| Governance Reviewer | Reviews role separation, exceptions, auditability and scope boundaries | Act as sole preparer and final approver |
| Human Approval Authority | Records the final human decision within documented authority | Delegate approval to system output |
| Demo Operator | Runs controlled synthetic demonstrations and fallback evidence | Represent demonstration data as operational evidence |

Security, Privacy, Integration, Service and UAT roles remain provisional dependencies for later PVE 1.4 builds.

## Responsibility matrix

Legend: **A** accountable, **R** responsible, **C** consulted, **I** informed.

| Activity | Project Owner | Packaging Engineer | Procurement Reviewer | Quality Reviewer | Finance/Value Reviewer | Data Owner | Governance Reviewer | Human Approval Authority |
|---|---|---|---|---|---|---|---|---|
| Project intake and objective | A/R | C | C | I | I | I | I | I |
| Technical requirements | C | A/R | I | C | I | I | I | I |
| Evidence submission and classification | C | R | R | C | I | A | C | I |
| Technical assessment | I | A/R | C | C | I | I | C | I |
| Commercial/value assessment | C | C | A/R | I | C | I | I | I |
| Quality and validation review | I | C | I | A/R | I | I | C | I |
| Value-claim review | I | C | C | I | A/R | I | C | I |
| Exception request | R | R | R | R | R | C | A | I |
| Exception acceptance/rejection | I | C | C | C | C | C | R | A |
| Final human decision | I | C | C | C | C | I | C | A/R |
| Immutable decision record | I | R | I | I | I | I | A | C |
| Project archive | A/R | I | I | I | I | I | C | I |

## Human decision flow

```text
Prepare project and evidence
→ Validate completeness and source classification
→ Technical engineering review
→ Procurement and commercial review
→ Quality and validation review
→ Finance/value claim review where applicable
→ Resolve blockers, conflicts and exceptions
→ Human Approval Authority records decision
→ Append-controlled or immutable decision evidence retained
```

Allowed system outcomes remain review-oriented, including criteria met for review, criteria not met, validation required, evidence conflict and insufficient data. `Approved`, `Rejected` and `Conditional` remain named human decisions.

## Segregation-of-duties controls

1. A preparer cannot be the sole final approver.
2. A supplier evidence submitter cannot approve that evidence.
3. Technical or evidence blockers cannot be overridden by commercial benefit.
4. An analyst requesting an exception cannot be its sole acceptance authority.
5. System-generated recommendations cannot approve themselves.
6. Finance or value review is required before an analytical saving is described as validated; realized value requires later evidence outside Build 2.
7. Supplier ranking, award, allocation and negotiation remain outside PVE authority.
8. Archived records cannot be modified to change the historical decision.
9. Delegation must preserve equivalent authority, role separation and traceability.
10. Provisional role names cannot be represented as appointed people.

## Decision states

| State | Meaning | Required exit evidence |
|---|---|---|
| Draft | Work in preparation | Complete required inputs or documented unavailable inputs |
| Review required | Ready for named review roles | Review record and findings |
| Blocked | Mandatory evidence, technical condition or authority missing | Blocker resolution or documented closure decision |
| Exception pending | Controlled deviation requested | Exception authority decision and rationale |
| Human decision pending | Reviews complete; approval not recorded | Named human decision |
| Approved / Rejected / Conditional | Explicit human decision only | Decision authority, rationale, timestamp and evidence references |
| Archived | Historical record protected | Archive authority and effective date |

## Exception and escalation model

| Trigger | Immediate response | Escalation owner | Required evidence | Prohibited response |
|---|---|---|---|---|
| Missing mandatory evidence | Mark output unavailable or validation required | Packaging Engineer | Missing-evidence list and validation plan | Assume a passing result |
| Conflicting evidence | Stop affected conclusion | Quality Reviewer | Conflict record, source comparison and resolution | Select convenient evidence silently |
| Expired or superseded evidence | Mark evidence invalid for current decision | Data Owner / Quality Reviewer | Validity and supersession record | Present as current evidence |
| Technical blocker | Block recommendation or require validation | Packaging Engineer | Requirement, result and blocker rationale | Override for savings |
| Commercial assumption dispute | Hold value claim | Procurement and Finance/Value Reviewers | Baseline, formula and source record | Present disputed savings as validated |
| Trial failure | Stop implementation recommendation | Quality Reviewer | Trial protocol, result and corrective action | Authorize implementation |
| Change-control deviation | Require controlled exception | Governance Reviewer | Deviation, impact and authority decision | Modify specification informally |
| Approval authority unavailable | Use documented delegate or keep pending | Governance Reviewer | Delegation evidence | Self-approve |
| Prohibited action attempted | Stop work and record scope breach | Governance Reviewer | Event and disposition | Implement or conceal request |

Exceptions cannot convert missing evidence into tested fact, authorize uncontrolled data, approve deployment, activate integrations or grant autonomous authority.

## Audit-event specification

This is a requirements catalogue only. No production audit logging is implemented.

### Minimum event fields

- event ID;
- project ID;
- UTC timestamp;
- actor role and, when later authorized, named actor identity;
- action;
- previous and resulting state;
- evidence or source reference;
- reason and rationale;
- reviewer or approver role;
- exception reference where applicable;
- immutable or append-controlled record reference;
- data-classification marker;
- synthetic/controlled-data marker for demonstrations.

### Minimum auditable events

| Event | Required record |
|---|---|
| Project created or scoped | Owner, objective, category and change type |
| Dataset uploaded or manually entered | Source, classification and content reference |
| Evidence classified | Evidence type, validity and reviewer |
| Evidence rejected, expired or superseded | Reason, effective date and replacement reference |
| Assessment generated | Inputs, rules, result, blockers and content hash |
| Blocker raised or resolved | Trigger, owner, evidence and resolution |
| Recommendation generated | Review-only outcome and rationale |
| Review completed | Role, findings and disposition |
| Exception requested | Requester, condition, impact and proposed treatment |
| Exception accepted or rejected | Authority, rationale, conditions and expiry |
| Human decision recorded | Decision, authority, rationale and evidence links |
| Project archived | Archive authority, date and protected state |

## Demonstration operating controls

- Use synthetic or explicitly controlled data only.
- State that recommendations are deterministic decision support.
- Show at least one blocker, evidence conflict or required validation outcome.
- End with named human decision responsibility.
- Keep non-production limitations visible.
- Use the fallback evidence package if the live application is unavailable.
- Do not claim pilot authorization, security certification, production readiness or realized savings.

## Build 2 limitations carried forward

- No named people are appointed.
- No production identity or access controls are implemented.
- No runtime audit infrastructure exists.
- No real-user UAT has occurred.
- No production service model or deployment authorization exists.
- Detailed data, security, privacy and access requirements remain Build 3 scope.
- Integration specifications remain Build 4 scope.
- UAT and value-validation execution models remain Build 5 scope.

## Acceptance intent

This operating model is acceptable only when reviewed as internally consistent, human-governed, documentation-only and aligned to Build 1 gaps P14-G01, P14-G02, P14-G03 and P14-G16. It does not close any operational gap with evidence.