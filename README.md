# Packaging Value Engineering & Decision Intelligence

**Stable Release on `main`:** PVE 1.1 — All-Category Project Intake and Validation Readiness  
**Completed Release Awaiting Separate Merge Decision:** PVE 1.2 — Corrugated Packaging Engineering and Validation Intelligence  
**PVE 1.2 Status:** Builds 1–8 complete; 74 of 74 planned hours; 100% complete; 0 hours and 0% pending  
**Pull Request:** PR #26 remains draft and unmerged  
**Canonical Repository:** `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`

The historical PVE-0.7 QA and Interview Release remains preserved as the original interview-release identity required by repository CI.

## Live Portfolio Demo

[Open the live Streamlit application](https://packaging-value-engineering-decision-intelligence.streamlit.app/)

The public application uses synthetic demonstration data only. Its recommendations are decision-support outputs and remain subject to engineering validation and documented evidence. It is not represented as production-ready enterprise software.

## What This Project Does

This is an explainable packaging value-engineering decision-support application. It compares packaging baselines and proposed alternatives across intake completeness, cost, material use, technical qualification, quality risk, supply risk, implementation risk, evidence, scenario assumptions, and immutable decision records.

PVE 1.2 adds corrugated-specific specification, evidence, compression, stacking, environment, packing-line, pallet, logistics, physical sustainability, should-cost, failure-cost, implementation-economics, recommendation, and immutable technical-assessment capabilities.

The system produces traceable readiness and engineering-review outputs. It never autonomously approves a packaging design.

## Current Release State

### PVE 1.1 — Stable

PVE 1.1 added all-category project intake, category-specific requirements, Excel templates and uploads, readiness scoring, blockers, output availability, source traceability, commercial and ROI extensions, guided workflow, reports, immutable readiness assessments, and release QA.

- Final PR: #25
- Squash merge commit: `37f4ae58e0d57c4531293371e423d771ada7ae50`
- Final pre-merge CI: PVE CI #735, run `29302903427`
- Total executions: 225
- Failures: 0
- Errors: 0

### PVE 1.2 — Complete on draft PR #26

PVE 1.2 is corrugated-only and has completed all eight controlled builds.

- Planned and completed effort: 74 hours
- Completion: 100%
- Pending: 0 hours, 0%
- Controlled contingency used: 0 of 2 hours
- Functional Build 8 head: `9465d9d6292a9d65834cfc11f27d1f056b9408a4`
- Functional Build 8 validation: PVE CI #849, run `29309701227`
- Functional full suite: 300 passed, 0 failures, 0 errors
- PR #26 remains draft, unmerged, and not ready for review

See:

- [`PVE_1.2_ARCHITECTURE.md`](PVE_1.2_ARCHITECTURE.md)
- [`PVE_1.2_BUILD_PLAN.md`](PVE_1.2_BUILD_PLAN.md)
- [`PVE_1.2_GOVERNANCE_AND_RISK.md`](PVE_1.2_GOVERNANCE_AND_RISK.md)
- [`PVE_1.2_RELEASE_NOTES.md`](PVE_1.2_RELEASE_NOTES.md)
- [`PVE_1.2_RELEASE_QA.md`](PVE_1.2_RELEASE_QA.md)
- [`PVE_1.2_RELEASE_CHECKLIST.md`](PVE_1.2_RELEASE_CHECKLIST.md)
- [`data/pve_1_2_corrugated_demonstration_cases.json`](data/pve_1_2_corrugated_demonstration_cases.json)

## Business Value

- Makes packaging cost, material, pallet, logistics, damage, and implementation trade-offs visible.
- Prevents technically weak alternatives from appearing financially attractive.
- Separates readiness, technical screening, evidence confidence, engineering recommendation, and human approval.
- Shows missing evidence, risk, constraints, and validation requirements.
- Converts analysis into reusable, append-only technical-assessment records.

## Decision Flow

```text
Packaging Project Intake
→ Canonical Validation and Source Classification
→ Readiness and Blocking Assessment
→ Corrugated Specification and Evidence Matching
→ Technical, Environment, Warehouse and Packing-Line Screening
→ Material, Pallet, Logistics and Physical Sustainability Analysis
→ Should-Cost, Failure-Cost and Implementation Economics
→ Engineering Recommendation for Review
→ Immutable Technical Assessment
→ Engineering Validation and Human Approval
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Run automated tests:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Core Components

| Component | Purpose |
|---|---|
| `src/data_models/` | Canonical data validation |
| `src/category_registry/` | Corrugated specifications, evidence, screening, analysis, economics, and recommendation |
| `src/intake/` | Project intake and output availability |
| `src/templates/` | Excel template generation |
| `src/uploads/` | JSON, CSV-compatible, and Excel normalization |
| `src/validation_readiness/` | Readiness, blockers, source traceability, and stage status |
| `src/persistence/` | Project-scoped immutable and append-only records, including technical assessments |
| `src/reports/` | Readiness and executive summaries |
| `src/exports/` | Deterministic JSON and Markdown decision packages |

## Interview Demonstration

Use [`docs/INTERVIEW_DEMO_GUIDE.md`](docs/INTERVIEW_DEMO_GUIDE.md) for the historical 8–12 minute demonstration and [`PVE_1.1_INTERVIEW_DEMO.md`](PVE_1.1_INTERVIEW_DEMO.md) for the stable PVE 1.1 walkthrough. PVE 1.2 synthetic cases are provided for controlled corrugated demonstrations only.

## Data and Evidence

Included demonstration datasets are synthetic and intended only for testing and portfolio demonstration. They must not be represented as validated supplier, production, laboratory, regulatory, or commercial data.

Source classifications remain distinct:

- uploaded fact
- manually entered fact
- supplier-declared value
- laboratory-tested value
- predicted value
- assumption

Supplier-declared, predicted, or assumed values must never be presented as laboratory-tested facts.

## Scope and Limitations

This project:

- supports packaging decision preparation and engineering review;
- requires engineering validation and documented evidence;
- does not approve packaging designs autonomously;
- does not rank or allocate suppliers;
- does not provide production external-system integration;
- does not claim production readiness.

PVE 1.2 excludes advanced universal BCT prediction, structural simulation, CAD, OCR, AI document reading, machine learning, mixed-SKU palletisation, truck-load optimisation, supplier ranking, ERP integration, authentication, deployment, pilot, activation, and production use. Carbon output remains unavailable without separately governed and authorized methodology.

The AI Procurement Copilot remains a separate repository and owns RFQ comparison, supplier ranking, negotiation, allocation, Supplier 360, and procurement savings realization.

## Integration Status

The integration contract remains draft. PVE exports a read-only internal decision package, but no live external integration is included or authorized.

## Historical Releases

| Release | Outcome | Status |
|---|---|---|
| PVE-0.1 to PVE-0.7 | Foundation through QA and interview release | Completed |
| PVE 1.0.1 to PVE 1.0.6 | Persistent projects, datasets, scenarios, thresholds, and immutable decision snapshots | Completed and governance-closed |
| PVE 1.1 | All-category intake and validation readiness | Completed and governance-closed |
| PVE 1.2 | Corrugated engineering and validation intelligence | 100% complete on draft PR #26; separate merge decision pending |

## Recovery

Read [`RECOVERY_MANIFEST.md`](RECOVERY_MANIFEST.md), [`PROJECT_STATUS.md`](PROJECT_STATUS.md), and the PVE 1.2 release records to reconstruct the stable releases and current draft release from GitHub alone.
