# Recovery Manifest

## Repository
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`.
- Stable branch: `main`.
- Current promoted and validated stable source SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.

## Historical Recovery Lineage
- Original pre-E1 rollback `main` SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`.
- E1.7 implementation lineage: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Governed E1 product baseline: `45f795370a60654050b5dca1ff4789487b3f049e`.
- Final pre-promotion `e1-development` SHA: `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.
- Promoted `main` SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.

## Current Recovery Point
- Recovery branch: `main`.
- Recovery SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Promotion PR: #71 merged and closed.
- Merge method: merge commit.
- Retained development branch: `e1-development` at `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.
- No branch deletion was authorized or performed as part of promotion.

## Recovery Validation Evidence
- Post-merge workflow run: `30656143928`.
- Validation job: `91240891645`.
- Checked-out branch and SHA: `main` at `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed.
- Failures: 0.
- Errors: 0.
- Retained artifact: `8803331290`.
- Artifact SHA-256: `943cad0adb2f8f4d20c5c9b0f2e1520655043c2224cfb079ee67d4e5d28e2d39`.

## Recovery Rules
1. Use `a6803b6156b591ec1fe9587469f6fe7c00ed97f4` to reconstruct the promoted E1 stable source baseline.
2. Use `300054cceb255e8e1273e8012a3ba0c0a236556d` only as the original pre-E1 rollback point.
3. Preserve `16fe5f...`, `45f795...`, and `9a3379...` as historical implementation, product-baseline, and pre-promotion development lineage respectively.
4. Do not rewrite or delete retained branches or historical evidence without separate authorization.
5. Any future build must start from its explicitly authorized and exact validated baseline.

## Current-State Correction
Earlier records stating that `main` remained at `300054cceb255e8e1273e8012a3ba0c0a236556d`, or that E1 promotion remained unauthorized, are historical pre-promotion snapshots. They are superseded as current-state instructions by the validated promoted baseline `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.

## Mandatory Scope Boundary
- Recovery records do not authorize deployment, release, tagging, live organizational data, pilot, activation, production use, or production-readiness claims.
- Human authorization remains mandatory.
- Autonomous approval and autonomous execution of engineering, commercial, sourcing, supplier-award, cost, scenario, risk, material, recommendation, deployment, release, or production decisions remain prohibited.

## Showcase and Handoff Build 1 Recovery
- Integration branch: `showcase-handoff-development`, created from `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Feature branch: `showcase/build-1-governance-closure`, created from the same SHA.
- If Build 1 is rejected, discard the feature branch and retain the integration branch at the exact promoted baseline.
- Builds 2–6 require separate authorization.
