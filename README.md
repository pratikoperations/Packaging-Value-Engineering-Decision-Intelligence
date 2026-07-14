# Packaging Value Engineering & Decision Intelligence

**Stable Release:** PVE 1.1 — All-Category Project Intake and Validation Readiness  
**Stable Status:** Completed, validated, merged, and governance-closed  
**Active Planning Release:** PVE 1.2 — Corrugated Packaging Engineering and Validation Intelligence  
**Active Build:** Build 1 — Architecture, Governance and Engineering Boundary Lock  
**Canonical Repository:** `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`

The historical PVE-0.7 QA and Interview Release remains preserved as the original interview-release identity required by repository CI.

## Live Portfolio Demo

[Open the live Streamlit application](https://packaging-value-engineering-decision-intelligence.streamlit.app/)

The public application uses synthetic demonstration data only. Its recommendations are decision-support outputs and remain subject to engineering validation and documented evidence. It is not represented as production-ready enterprise software.

## What This Project Does

This is an explainable packaging value-engineering decision-support application. It compares packaging baselines and proposed alternatives across intake completeness, cost, material use, technical qualification, quality risk, supply risk, implementation risk, evidence, and scenario assumptions.

The system produces traceable readiness and recommendation outputs for management and engineering review. It never autonomously approves a packaging design.

## Current Release State

### PVE 1.1 — Stable

PVE 1.1 added all-category project intake, category-specific requirements, Excel templates and uploads, readiness scoring, blockers, output availability, source traceability, commercial and ROI extensions, guided workflow, reports, immutable readiness assessments, and release QA.

- Final PR: #25
- Final feature head: `dc85db49afee46bde3118684761c0a176dd32194`
- Squash merge commit: `37f4ae58e0d57c4531293371e423d771ada7ae50`
- Final pre-merge CI: PVE CI #735, run `29302903427`
- Complete unittest suite: 221 passed
- Focused report tests: 4 passed
- Total executions: 225
- Failures: 0
- Errors: 0

### PVE 1.2 — Active planning

PVE 1.2 is corrugated-only. Build 1 defines architecture, governance, model boundaries, risks, dependencies, acceptance gates, and a controlled 74-hour plan with a 2-hour contingency. Build 1 does not implement production technical formulas or begin Build 2.

See:

- [`PVE_1.2_ARCHITECTURE.md`](PVE_1.2_ARCHITECTURE.md)
- [`PVE_1.2_BUILD_PLAN.md`](PVE_1.2_BUILD_PLAN.md)
- [`PVE_1.2_GOVERNANCE_AND_RISK.md`](PVE_1.2_GOVERNANCE_AND_RISK.md)

## Business Value

- Makes packaging cost and material trade-offs visible.
- Prevents technically weak alternatives from appearing financially attractive.
- Separates readiness, technical screening, engineering recommendation, and human approval.
- Shows missing evidence, risk, constraints, and validation requirements.
- Converts analysis into reusable, immutable decision records.

## Decision Flow

```text
Packaging Project Intake
→ Canonical Validation
→ Readiness and Blocking Assessment
→ Cost and Material Analysis
→ Technical Qualification
→ Quality / Supply / Implementation Risk
→ Explicit Scenario Assumptions
→ Explainable Recommendation for Review
→ JSON and Markdown Decision Package
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
| `src/category_registry/` | Configuration-driven packaging categories and requirements |
| `src/intake/` | Project intake and output availability |
| `src/templates/` | Excel template generation |
| `src/uploads/` | JSON, CSV, and Excel normalization |
| `src/validation_readiness/` | Readiness, blockers, source traceability, and stage status |
| `src/cost_engine/` | Unit and annual cost analysis |
| `src/material_engine/` | Packaging weight and annual material analysis |
| `src/commercial/` | Savings, implementation economics, and payback |
| `src/technical_qualification/` | Requirement and evidence-based qualification |
| `src/risk_engine/` | Quality, supply, and implementation risk |
| `src/scenario_engine/` | Explicit volume, cost, and material assumptions |
| `src/recommendation/` | Explainable recommendation gates and ordering |
| `src/persistence/` | Project-scoped immutable and append-only records |
| `src/reports/` | Readiness and executive summaries |
| `src/exports/` | Deterministic JSON and Markdown decision packages |

## Interview Demonstration

Use [`docs/INTERVIEW_DEMO_GUIDE.md`](docs/INTERVIEW_DEMO_GUIDE.md) for the historical 8–12 minute demonstration and [`PVE_1.1_INTERVIEW_DEMO.md`](PVE_1.1_INTERVIEW_DEMO.md) for the current stable PVE 1.1 walkthrough. Use [`docs/FINAL_RELEASE_CHECKLIST.md`](docs/FINAL_RELEASE_CHECKLIST.md) and [`PVE_1.1_RELEASE_CHECKLIST.md`](PVE_1.1_RELEASE_CHECKLIST.md) for preserved release evidence.

## Data and Evidence

Included demonstration datasets are synthetic and intended only for testing and portfolio demonstration. They must not be represented as validated supplier, production, laboratory, or commercial data.

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

PVE 1.2 planning keeps advanced BCT prediction, structural simulation, CAD, OCR, AI document reading, machine learning, supplier ranking, ERP integration, authentication, deployment, pilot, activation, and production use excluded.

The AI Procurement Copilot remains a separate repository and owns RFQ comparison, supplier ranking, negotiation, allocation, Supplier 360, and procurement savings realization.

## Integration Status

The integration contract remains draft. PVE exports a read-only internal decision package, but no live external integration is included or authorized.

## Historical Releases

| Release | Outcome | Status |
|---|---|---|
| PVE-0.1 to PVE-0.7 | Foundation through QA and interview release | Completed |
| PVE 1.0.1 to PVE 1.0.6 | Persistent projects, datasets, scenarios, thresholds, and immutable decision snapshots | Completed and governance-closed |
| PVE 1.1 | All-category intake and validation readiness | Completed and governance-closed |
| PVE 1.2 | Corrugated engineering and validation intelligence | Build 1 planning active |

## Recovery

Read [`RECOVERY_MANIFEST.md`](RECOVERY_MANIFEST.md) and [`PROJECT_STATUS.md`](PROJECT_STATUS.md) to reconstruct the completed stable releases and current planning state from GitHub alone.
