# Master Architecture

## Decision Flow

```text
Packaging Baseline
→ Design Alternatives
→ Cost and Material Analysis
→ Technical Qualification
→ Quality / Supply / Implementation Risk
→ Sustainability and Logistics Indicators
→ Scenario and Sensitivity Analysis
→ Risk-Adjusted Recommendation
→ Validation Requirements
→ Versioned Decision Package Export
```

## Target Components

```text
src/
├── data_models/
├── cost_engine/
├── material_engine/
├── logistics_engine/
├── technical_qualification/
├── risk_engine/
├── sustainability/
├── scenario_engine/
├── recommendation/
├── explainability/
└── exports/
```

## Core Principles
- Packaging engineering logic is category-specific.
- Deterministic calculations are the source of truth.
- AI cannot approve a packaging design.
- Missing mandatory data can produce `Insufficient Data`.
- Status options: Recommended, Conditionally Recommended, Not Recommended, Insufficient Data.
- Every recommendation shows assumptions, gaps, confidence, risks, and validation required.

## Project Boundary
PVE owns the technical-commercial packaging recommendation. AI Procurement Copilot owns RFQ comparison, supplier ranking, negotiation, allocation, Supplier 360, and procurement savings realization.

## Integration
PVE exports a versioned, read-only decision package. Procurement Copilot imports it through a project-local adapter. Neither repository modifies the other's source files.
