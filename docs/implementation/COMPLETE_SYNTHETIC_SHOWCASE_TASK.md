# Complete Synthetic Showcase Data Upgrade — Implementation Task

## Status
Temporary Copilot implementation handoff. This file MUST be deleted before the implementation PR is considered complete.

## Exact baseline
- Repository: `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`
- Base branch: `enhancement/browser-data-calculation-programme`
- Exact governed starting SHA: `0260b127f308dfa40c08e2bb95ca5d1f2d26a355`
- Implementation branch: `enhancement/complete-synthetic-showcase-data`

## Objective
Upgrade the single controlled synthetic portfolio project `PVE-DEMO-001` so that the PVE 1.1 Guided Intake / Readiness demo shows a coherent, commercially meaningful, decision-ready corrugated value-engineering case instead of primarily demonstrating missing-data controls.

This is a DATA-CONTRACT RECONCILIATION gate, not a feature rewrite.

## Business story to preserve
Use one synthetic FMCG corrugated shipper right-sizing / cost-optimization case:
- annual volume: 1,200,000 cases/year;
- currency: INR;
- current unit cost: ₹52.40/case;
- preferred proposed unit cost: ₹48.80/case;
- gross annual saving: ₹43.2 lakh/year before any one-time implementation cost;
- baseline finished case weight: 980 g;
- proposed finished case weight: 880 g;
- material reduction: approximately 10.2%;
- baseline cases/pallet: 24;
- proposed cases/pallet: 30;
- freight distance basis: 650 km;
- engineering validation and human approval remain mandatory;
- no autonomous approval claim.

## Verified root cause
The current seed file contains useful legacy portfolio data but lacks the newer PVE 1.1 readiness collections. Specifically:
- `packaging_project` in the uploaded canonical JSON lacks `objective` and `change_type`, causing metadata score 5/7;
- `intake_values` are absent, causing no baseline/proposed specification and no commercial readiness;
- `quality_tests` are absent;
- `document_register` is absent;
- current/proposed costs exist in `cost_inputs` but PVE 1.1 readiness explicitly reads commercial `intake_values`;
- the seeder's scenario identity can conflict if a changed dataset is seeded into an existing demo database.

## Authorized implementation scope
Prefer exactly these files unless a test proves one additional focused file is essential:
1. `data/demo/pve_portfolio_project.json`
2. `src/demo_portfolio/seeder.py`
3. `tests/demo_portfolio/test_portfolio_seed.py`
4. one focused readiness/showcase regression test file, preferably an existing relevant test file if cleanly possible
5. optional interview/demo documentation only if the visible business story changes materially

Do NOT modify:
- readiness scoring logic;
- commercial formulas;
- technical qualification engine;
- recommendation engine;
- scenario engine;
- export engine;
- application page logic;
- browser harness;
- workflows;
- dependencies;
- schemas unless strictly required by an existing validation contract.

## Required seed-data correction
### 1. Packaging project metadata
Ensure uploaded canonical `packaging_project` includes at least:
- `project_id`: `PVE-DEMO-001`
- existing project name unless changing it can be proven migration-safe
- `category`: `corrugated_shipping_case`
- `objective`: `Cost reduction`
- `change_type`: `Size optimization`
- `annual_volume`: 1200000
- `annual_volume_unit`: `cases_per_year`
- `currency`: `INR`
- `status`: `active`

### 2. Alternatives
Prefer one baseline plus one primary proposed alternative for the showcase unless retaining additional screened-out alternatives is proven harmless to deterministic validation.

Baseline:
- `ALT-BASE`
- current 5-ply BC flute shipper
- 600 x 400 x 350 mm internal dimensions
- 980 g
- `5PLY_BC_FLUTE`

Preferred proposal:
- `ALT-A`
- right-sized 5-ply BC flute shipper
- 575 x 385 x 330 mm internal dimensions
- 880 g
- `5PLY_BC_FLUTE`

If ALT-B / ALT-C are retained, they must not cause an `insufficient_data` technical state or create ambiguous recommendation behavior. Simpler is preferred.

### 3. PVE 1.1 `intake_values`
Populate a credible baseline and proposed specification using the existing corrugated registry contract. At minimum populate every mandatory field for both contexts, including:
- legacy length/width/height;
- box style;
- converting profile;
- internal length/width/height;
- ply;
- flute combination;
- paper-layer structure;
- layer GSM profile;
- board grade;
- joint type;
- closure method;
- gross packed weight;
- case pack quantity.

Also populate useful recommended fields where they strengthen the demonstration, such as:
- external dimensions;
- board caliper;
- print process / colour count;
- coating/treatment;
- regulatory markings;
- stack height;
- storage duration;
- humidity;
- ECT;
- BCT;
- burst.

Use traceable synthetic source classifications and explicit units. Do not present supplier-declared BCT/ECT/burst as laboratory-tested.

Commercial context MUST include:
- annual_volume = 1200000;
- current_unit_cost = 52.4;
- proposed_unit_cost = 48.8.

Logistics context should include a coherent route/lane basis and baseline/proposed palletization where compatible with the current intake contract.

### 4. Quality tests
Add a controlled synthetic quality-test record set. BCT must have a valid laboratory-tested result and no missing mandatory test blocker. Additional recommended tests may be populated for demonstration credibility.

Use a technically coherent unit convention. Prefer BCT in N throughout the new PVE 1.1 readiness evidence, e.g. a requirement around 5000 N and a synthetic tested proposed result around 5400 N, while preserving clear synthetic labeling.

### 5. Document register
Populate the mandatory documents as uploaded and valid with synthetic references:
- current specification;
- proposed specification;
- supplier quotation.

Also include useful recommended records such as drawing, laboratory report and trial report where appropriate. References must clearly remain synthetic and non-production.

### 6. Technical qualification / validation
The preferred ALT-A must not remain `not_assessed` or `insufficient_data` in the portfolio dataset.
Provide traceable synthetic evidence and a qualified or conditionally qualified status consistent with the existing governed engine contract.

Validation requirements for the preferred proposal may be `passed` only when backed by explicit synthetic test/trial evidence. Preserve the statement that real engineering validation remains mandatory outside this demo.

### 7. Uploaded recommendation boundary
Do NOT pre-approve the uploaded recommendation. `validate_user_dataset()` requires the uploaded `decision_recommendation.status` to remain `insufficient_data`. The persisted governed scenario/decision snapshot must continue to be generated by existing deterministic services.

## Seeder migration / idempotence requirement
A changed seed payload must work both:
1. on a clean database; and
2. when the existing `PVE-DEMO-001` project and old demo dataset/scenario already exist.

Do not overwrite immutable historical records.
Do not break append-only/recovery behavior.
The current `_find_scenario()` raises a conflict when the same scenario name points to an older dataset. Correct this with the smallest explicit versioned scenario identity or equivalent non-destructive migration-safe approach.

The outcome on an existing demo DB should create a new dataset/scenario/decision lineage for the upgraded showcase without mutating the prior immutable records.

Repeated seeding after the upgraded lineage exists must be idempotent.

## Required visible acceptance outcome
On a clean seeded showcase, `assess_readiness()` should produce:
- no blocking issues from missing baseline specification;
- no blocking issue from missing proposed specification;
- no missing current cost;
- commercial analysis available;
- readiness stage preferably `Ready for Approval Review` if the data contract genuinely supports >=95% with no blockers, otherwise the highest defensible non-insufficient stage;
- technical feasibility remains unavailable where the PVE 1.1 product boundary says final engineering feasibility is not provided;
- approval decision remains unavailable and human approval remains mandatory.

The Commercial & ROI tab must show meaningful outputs based on ₹52.40 -> ₹48.80 and 1.2M cases/year.
The Testing & Evidence tab must show actual controlled synthetic evidence rather than `No quality-test evidence` / `No document-register entries`.
The Executive Report must show the commercial opportunity and preserved approval limitation.

## Required tests
Add deterministic tests proving at least:
1. clean seed creates one coherent upgraded linked chain;
2. repeated upgraded seed is idempotent;
3. migration from an already-seeded legacy demo creates the upgraded immutable lineage without overwriting history;
4. canonical seeded data has baseline + proposed PVE 1.1 intake values;
5. commercial intake has current and proposed unit cost;
6. readiness has no missing baseline/proposed/current-cost blockers;
7. commercial analysis is available;
8. mandatory document records are uploaded/valid;
9. mandatory quality test evidence is present and valid;
10. human approval / non-autonomy boundaries remain preserved;
11. gross annual saving implied by 52.4 -> 48.8 at 1.2M volume is ₹4,320,000;
12. material reduction from 980 g -> 880 g is approximately 10.2%;
13. no business engine or workflow change is needed.

Run relevant focused tests and the complete existing suite locally if available.

## CI-efficiency rule
Do not modify CI merely for this gate. Keep implementation on this `enhancement/**` branch. After final implementation, exact-head validation will be triggered once using the existing approved `feature/**` push mechanism so routine user commands remain zero.

## Final cleanup
Before reporting implementation complete:
- DELETE this file `docs/implementation/COMPLETE_SYNTHETIC_SHOWCASE_TASK.md`;
- ensure the final PR diff contains only durable product/test/documentation changes;
- do not change main;
- do not deploy or release;
- do not claim production readiness.
