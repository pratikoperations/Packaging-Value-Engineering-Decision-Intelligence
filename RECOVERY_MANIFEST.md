# Recovery Manifest

## Stable release
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Stable branch: `main`
- Stable release: PVE 1.0.6
- Stable merge: `4fc7f8a7a8b6764d80df7341cdb9b2ce39678213`
- Stable CI: PVE CI #520, run `29223657516`
- Stable tests: 179 passed

## Active PVE 1.1 recovery point
- Branch: `feature/pve-1.1-all-category-intake`
- Pull request: PR #25
- PR state: open, draft, unmerged
- Latest validated implementation head before recovery update: `f5733de3890c51b25f0574694aa03cceb0895dc0`
- Latest CI: PVE CI #635
- Run ID: `29255248902`
- Result: success
- Expected tests: 208

## Completed builds
- Build 1: complete, 6 hours
- Build 2: complete, 7 hours
- Build 3: complete, 14 hours
- Build 4: complete, 10 hours
- Build 5: complete, 10 hours
- Build 6: complete, 9 hours

Total consumed: 56 hours.
Remaining under the 80-hour cap: 24 hours.

## Build 6 recovery evidence
- weighted readiness scoring
- blockers override percentage
- readiness stages
- output availability with reasons
- source traceability
- append-only readiness snapshots
- archived-project and project-isolation controls
- no automatic approval

## Next increment
Build 7 — Commercial and ROI Extension — requires separate authorization. Builds 8 and 9 are not authorized.

## Recovery rule
Resume from the active branch and PR. Treat Builds 1–6 as complete. Keep PR #25 draft and unmerged. Do not begin Build 7 without explicit authorization.

## Scope boundary
Power BI, PostgreSQL reporting integration, ERP integration, OCR, AI document reading, deployment, activation, pilot, production, authentication, supplier ranking or allocation, cloud database, machine learning, live pricing, and autonomous approval remain excluded.
