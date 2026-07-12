# Packaging Value Engineering & Decision Intelligence

**Current Build:** PVE-0.7 — QA and Interview Release  
**Status:** Release implementation complete — CI and final QA pending  
**Canonical Repository:** `pratikoperations/Packaging-Value-Engineering-Decision-Intelligence`

## What This Project Does

This is an interview-ready packaging value-engineering decision-support application. It compares a packaging baseline with proposed design alternatives across cost, material use, technical qualification, quality risk, supply risk, implementation risk, and scenario assumptions.

The system produces explainable recommendation statuses and exports a traceable decision package for management review.

## Business Value

- Makes packaging cost and material trade-offs visible
- Prevents technically weak alternatives from appearing financially attractive
- Separates recommendation status from engineering approval
- Shows missing evidence, risk, constraints, and validation requirements
- Converts analysis into a reusable executive decision record

## Decision Flow

```text
Synthetic Packaging Dataset
→ Canonical Validation
→ Cost and Material Analysis
→ Technical Qualification
→ Quality / Supply / Implementation Risk
→ Scenario Assumptions
→ Explainable Recommendation
→ JSON and Markdown Decision Package
```

## Quick Start

### Requirements
- Python 3.12
- pip

### Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Run automated tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Application Workflow

1. Review the synthetic corrugated shipping-case dataset.
2. Adjust annual volume.
3. Apply explicit cost or material-weight assumptions by alternative.
4. Compare cost, material, qualification, risk, and recommendation outputs.
5. Review rationale, constraints, and validation requirements.
6. Download the machine-readable JSON decision package.
7. Download the human-readable Markdown executive report.

## Core Components

| Component | Purpose |
|---|---|
| `src/data_models/` | Canonical data validation |
| `src/cost_engine/` | Unit and annual cost analysis |
| `src/material_engine/` | Case weight and annual material analysis |
| `src/technical_qualification/` | Requirement and evidence-based qualification |
| `src/risk_engine/` | Quality, supply, and implementation risk |
| `src/scenario_engine/` | Explicit volume, cost, and material assumptions |
| `src/recommendation/` | Explainable recommendation gates and ordering |
| `src/exports/` | Deterministic JSON and Markdown decision packages |
| `app.py` | Streamlit interview demonstration UI |

## Recommendation Statuses

- `recommended`
- `conditionally_recommended`
- `not_recommended`
- `insufficient_data`

Recommendation logic is deterministic and transparent. It does not use an opaque weighted score.

## Interview Demonstration

Use [`docs/INTERVIEW_DEMO_GUIDE.md`](docs/INTERVIEW_DEMO_GUIDE.md) for an 8–12 minute walkthrough covering the business problem, scenario demonstration, recommendation logic, decision-package export, and production limitations.

Use [`docs/FINAL_RELEASE_CHECKLIST.md`](docs/FINAL_RELEASE_CHECKLIST.md) for the release acceptance gate.

## Data

The included dataset is synthetic and intended only for demonstration and automated testing. It must not be represented as validated supplier, production, laboratory, or commercial data.

## Scope and Limitations

This project:
- supports packaging design comparison and decision preparation
- requires engineering validation and documented evidence
- does not approve packaging designs autonomously
- does not rank or allocate suppliers
- does not own negotiation or procurement savings realization
- does not provide external-system integration
- does not claim production readiness

The AI Procurement Copilot remains a separate repository and owns procurement-specific workflows such as RFQ ranking, supplier allocation, negotiation, Supplier 360, and savings realization.

## Integration Status

The integration contract remains draft. PVE exports a read-only internal decision package, but no live external integration is included in this release.

## Project Builds

| Build | Outcome | Status |
|---|---|---|
| PVE-0.1 | Repository Foundation | Completed |
| PVE-0.2 | Data Model and Demo Data | Completed |
| PVE-0.3 | Cost and Material Engine | Completed |
| PVE-0.4 | Technical Qualification and Risk | Completed |
| PVE-0.5 | Scenario and Recommendation UI | Completed |
| PVE-0.6 | Decision Package Export | Completed |
| PVE-0.7 | QA and Interview Release | Active |

## Recovery

Read [`RECOVERY_MANIFEST.md`](RECOVERY_MANIFEST.md) to reconstruct project status, validation evidence, file-reading order, test commands, and restart steps from GitHub alone.

## Governance

GitHub is the source of truth. Every meaningful update must be tested, documented, committed, re-verified from GitHub, and supported by project-local QA evidence.
