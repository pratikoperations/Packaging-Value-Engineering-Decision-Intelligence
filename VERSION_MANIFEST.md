# Version Manifest

## Historical Releases
- `0.7.0-qa-interview-release`: completed; original interview-release identity preserved.
- PVE 1.0.1 through PVE 1.0.6: completed and governance-closed.
- PVE 1.1: completed, validated, merged, and governance-closed.
- PVE 1.2: completed, validated, merged, and governance-closed.

## E1 Version Lineage

### E1.7 Implementation Record
- Version identity: `e1.7-governed-approved-specification-consumption`.
- Implementation lineage SHA: `16fe5f755546f99c59bdb67f2e1d0abf2a7908e7`.
- Claim boundary: governed approved-specification consumption envelopes and purpose-specific authorization records only; no autonomous downstream decision approval.

### E1 Governed Product Baseline
- Version identity: `e1-release-candidate-governance-baseline`.
- Governed product baseline SHA: `45f795370a60654050b5dca1ff4789487b3f049e`.
- Status: qualified and historically preserved.

### E1 Final Pre-Promotion Development Record
- Branch: `e1-development`.
- Final retained SHA: `9a3379b0e0cf64b4761c2a8dffac671c41d94f98`.
- Status: retained and unchanged after promotion.

### E1 Promoted Stable Source Baseline
- Version identity: `e1-promoted-stable-source-baseline`.
- Pull request: PR #71 merged and closed.
- Merge method: merge commit.
- Promoted `main` SHA: `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`.
- Original rollback `main` SHA: `300054cceb255e8e1273e8012a3ba0c0a236556d`.
- Post-merge validation run: `30656143928`.
- Validation job: `91240891645`.
- Focused report tests: 4 passed.
- Complete repository suite: 656 passed; 0 failures; 0 errors.
- Artifact: `8803331290`.
- Artifact SHA-256: `943cad0adb2f8f4d20c5c9b0f2e1520655043c2224cfb079ee67d4e5d28e2d39`.
- Status: promoted, exact-SHA validated on `main`, and governance-closed.

## Current Version State
The current governed stable source-code baseline is `main` at `a6803b6156b591ec1fe9587469f6fe7c00ed97f4`. Historical statements that `main` remained at `300054cceb255e8e1273e8012a3ba0c0a236556d` or that promotion remained unauthorized describe pre-promotion states and are not current.

## Mandatory Controls
- Engineering validation and human approval remain mandatory.
- Autonomous approval remains prohibited.
- Deployment, release, tagging, live organizational data, pilot, activation, production use, and production-readiness claims remain separately unauthorized.
- Historical branches and recovery records remain preserved until separate deletion authorization.

## Showcase and Handoff Release
- Programme identity: `pve-showcase-handoff-release-1.0`.
- Current stage: Build 1 governance closure pending integration.
- Total authorized programme budget: 50 hours.
- Builds 2–6 remain unauthorized.
