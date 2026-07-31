# Build History

## Historical Release Summary
- PVE-0.1 through PVE-0.7.2: completed and merged.
- PVE 1.0.1 through PVE 1.0.6: completed and governance-closed.
- PVE 1.1: completed, validated, merged, and governance-closed.
- PVE 1.2: completed, validated, merged, and governance-closed.
- E1.1 through E1.7: completed, validated, promoted, and governance-closed.

Detailed historical build records remain preserved in repository history at and before baseline `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.

## E1 Lineage
- Original pre-E1 rollback `main` SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`.
- E1.7 implementation merge lineage: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Governed E1 product baseline: `45f795370a60654050b5dca1ff4789487b3f049e`.
- Final pre-promotion `e1-development` SHA: `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.

## E1 Promotion Build
**Status:** Completed, merge-committed into `main`, exact-SHA validated, and governance-closed.

### Completion Record
- Pull request: PR #71 merged and closed.
- Merge method: merge commit.
- Merge commit and final promoted `main` SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Retained source branch: `e1-development` at `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.
- Promotion scope: 33 commits; 55 changed files; 8,774 additions; 4 deletions.

### Exact Post-Merge Validation
- Workflow run: `30656143928`.
- Job: `91240891645`.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed; 0 failures; 0 errors.
- Artifact: `8803331290`.
- Artifact SHA-256: `943cad0adb2f8f4d20c5c9b0f2e1520655043c2224cfb079ee67d4e5d28e2d39`.

### Governance Boundary
Promotion establishes a stable source-code baseline only. It does not authorize deployment, release, tagging, live organizational data, production use, production-readiness claims, autonomous approval, or autonomous execution of engineering, commercial, sourcing, supplier-award, cost, scenario, risk, material, recommendation, deployment, release, or production decisions.

## Showcase and Handoff Release — Build 1
**Status:** Implemented on the governed feature branch and pending PR validation and merge authorization.

### Implemented Scope
- Reconciled canonical governance and recovery records after PR #71 promotion.
- Corrected the current-state interpretation of pre-promotion statements.
- Preserved all required E1 lineage and rollback points.
- No source code, UI, tests, workflows, dependencies, or data were changed.

### Budget
- Authorized maximum: 5 hours.
- Programme total: 50 hours.
- Builds 2–6 remain unauthorized.
