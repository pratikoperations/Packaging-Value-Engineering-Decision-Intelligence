# Recovery Manifest

## Stable Release Recovery

- Project: Packaging Value Engineering & Decision Intelligence
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Stable branch: `main`
- Stable release: PVE-1.0.6 — Decision Snapshot and Final Release Closure
- Stable release status: completed, validated, merged, and governance-closed
- Stable PR: #22
- Stable merge commit: `4fc7f8a7a8b6764d80df7341cdb9b2ce39678213`
- Stable CI: PVE CI #520, run `29223657516`
- Stable tests: 179 passed, 0 failed, 0 errors

## Active PVE 1.1 Recovery Point

- Release: PVE 1.1 — All-Category Project Intake and Validation Readiness
- Branch: `feature/pve-1.1-all-category-intake`
- Pull request: PR #25
- PR state: open, draft, unmerged
- Latest validated implementation head before recovery synchronization: `4bf93a6ad7d8e6ba153857383a3b44e5386198e2`
- Latest CI: PVE CI #577
- CI run ID: `29235897461`
- CI conclusion: success
- Automated-test step: success

## Completed PVE 1.1 Builds

1. Build 1 — Architecture and Scope Lock — complete — 6 hours.
2. Build 2 — Project Creation Expansion — complete — 7 hours.
3. Build 3 — Category Input Definitions — complete — 14 hours.

Recorded consumed allocation: 27 hours.
Remaining allocation under the 80-hour cap: 53 hours.

## Current and Next Increment

- Current authorized increment: Build 4 — Excel Template Generation.
- Authorized ceiling: 10 hours.
- Implementation status: not started.
- Build 5 is not authorized.

## Completed Acceptance Evidence

- Eight packaging categories registered through configuration.
- Objectives and category-specific change types validated.
- Additive schema version 2 applied without rewriting historical evidence.
- All eight categories create projects.
- Legacy `corrugated_shipping_case` values remain supported.
- Archived-project writes remain blocked.
- Mandatory, recommended, and optional field/document definitions exist for all categories.
- Units, types, ranges, criticality, warnings, blockers, tests, available analyses, and unavailable analyses are configuration-driven.
- PVE CI #577 succeeded.

## Outstanding Recovery Sequence

1. Complete and validate Build 4 only.
2. Do not begin Build 5 without separate authorization.
3. Keep PR #25 draft.
4. Preserve current JSON/CSV uploads and canonical dataset behavior.
5. Preserve historical datasets, thresholds, scenarios, decision snapshots, archive protection, and project isolation.
6. Do not merge until all PVE 1.1 release acceptance criteria pass.

## Scope Boundary

Excluded: Power BI, PostgreSQL reporting integration, ERP integration, OCR, AI document reading, deployment, activation, pilot, production, authentication, supplier ranking or allocation, cloud database, machine learning, live pricing, autonomous approval, and full all-category technical feasibility.

## Recovery Rule

Resume only from the branch and PR state above. Treat Builds 1–3 as completed. Treat Build 4 as authorized but not started. Do not infer later-build completion from chat history.
