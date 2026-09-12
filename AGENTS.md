# Codex Operating Rules — Packaging Value Engineering & Decision Intelligence

## 1. Purpose

This repository is a governed packaging value-engineering decision-support portfolio project. Codex may assist with bounded implementation, testing, documentation and recovery work, but must preserve the repository's engineering, evidence and human-approval boundaries.

## 2. Authority and recovery order

Before changing anything, read the current authoritative project records. At minimum inspect:

1. `PROJECT_STATUS.md`
2. `README.md`
3. `RECOVERY_MANIFEST.md` when present/relevant
4. the release/build-plan and governance records for the active programme
5. the files, tests and CI workflows directly affected by the task

When documents disagree, do not silently choose the most convenient statement. Prefer current executable behaviour plus the latest accepted exact-SHA/CI evidence, report the contradiction, and reconcile documentation only within the authorised task.

## 3. Release topology

- `main` contains the stable governance-closed public portfolio baseline and must be treated as protected.
- Historical release identities and evidence must remain intact.
- E1 work has its own governed development/release-candidate history. Do not promote E1 or any future programme to `main` merely because it is technically complete.
- Do not rewrite release history, retag historical releases or relabel earlier evidence.

## 4. Business and engineering boundaries

Codex must preserve all of these unless a separately authorised programme explicitly changes them:

- The application provides engineering decision support; it does not autonomously approve a packaging design.
- Engineering validation and explicit human approval remain mandatory.
- Technical/evidence blockers override commercial, economic, logistics, material and sustainability attractiveness.
- Evidence confidence is not probability of technical success.
- Supplier-declared, predicted and assumed values must never be represented as laboratory-tested facts.
- Do not invent engineering properties, test results, tolerances, prices, savings, carbon factors, formulas, thresholds, defaults or evidence.
- Do not add supplier ranking, award authority, procurement allocation or production-system authority to this repository unless an explicitly governed scope authorises it.
- Keep AI Procurement Copilot responsibilities separate from PVE responsibilities.
- Do not claim production readiness, validated production performance, regulatory approval or realized savings from synthetic demonstration data.

## 5. Scope discipline

For every task:

1. identify the authorised objective and acceptance criteria;
2. inspect affected architecture/business-rule/evidence paths before editing;
3. make the smallest coherent change;
4. avoid unrelated formatting, dependency upgrades or refactoring;
5. preserve compatibility and historical evidence unless the task explicitly requires a governed migration;
6. stop and report if the task would cross an architecture, authority, release or data-governance boundary.

## 6. Data and privacy

- Use synthetic or explicitly approved sanitized data for portfolio work.
- Never commit secrets, credentials, tokens, confidential supplier quotations, proprietary specifications, personal data or restricted company information.
- Never transmit repository data to a third party or external model/provider unless the task explicitly authorises that route and its data boundary.
- Do not add telemetry, analytics or external data collection by default.

## 7. Network and dependencies

Network access is exceptional, not assumed.

- Prefer existing dependencies and local repository evidence.
- Do not add or upgrade dependencies unless required by the approved task.
- Before any dependency change, assess necessity, lockfile/manifest impact, licensing/security implications and test impact.
- Do not bypass dependency, security or CI controls to make a build pass.

## 8. Git and branch control

- Never implement directly on `main`.
- Start from the intended exact base and use a focused branch.
- Keep commits scoped and reviewable.
- Never force-push shared history unless a specific recovery instruction explicitly authorises it.
- Do not merge a moved PR head using stale validation evidence.
- Capture the exact PR head SHA before final merge verification.
- Use the repository's established merge method for the active programme.
- Do not create tags, releases, deployments or promotions unless the task specifically authorises them.

## 9. Testing and verification

For code-affecting changes, run the repository's relevant focused tests plus the full governed test/CI gate required by the active programme. The stable repository documents the full Python test suite as:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Also run any programme-specific static verifiers, migration tests, export checks or CI workflows applicable to the changed paths.

A completion report must state:

- exact branch/head tested;
- files changed;
- tests/checks executed;
- pass/fail counts where available;
- warnings or skipped checks;
- business-rule/schema/evidence impact;
- residual risks and rollback method.

Do not say a change is validated when required checks were not executed.

## 10. Immutable and append-only controls

Where the current architecture defines immutable or append-only assessment/decision records:

- preserve immutability and project isolation;
- do not introduce silent update/delete paths;
- migrations must be explicit, tested and backward-safe within the authorised scope;
- do not mutate historical evidence merely to simplify current implementation.

## 11. UI and claim discipline

User-facing changes must preserve the distinction among readiness, screening, evidence confidence, engineering recommendation and human approval. Do not use stronger approval/compliance language than the evidence supports.

## 12. Deployment and external systems

Deployment, production activation, external integration, authentication, live supplier data, ERP integration and production use remain separate governance decisions. Do not activate them as a side effect of ordinary development.

## 13. Codex completion standard

A task is complete only when the implementation is within scope, affected checks pass, the diff is reviewed, documentation is current where materially required, exact-head evidence is captured, and no protected authority boundary has been crossed.
