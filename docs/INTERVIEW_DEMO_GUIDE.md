# Interview Demonstration Guide

## Purpose

Demonstrate how packaging engineering, cost, risk, evidence and decision logic are combined into transparent decision support without autonomous approval, supplier allocation or unsupported production-readiness claims.

The application uses synthetic demonstration data. State this before discussing any commercial, technical or savings result.

## Current Governed Application

The current experience includes:

- Home
- Showcase & Handoff
- Project Dashboard
- Guided Workflow
- Specification Review
- Data Upload
- Business Rules & Thresholds
- Scenario Analysis
- Decision Records
- SourceMate
- Calculation Evidence
- Decision Evidence Ledger
- Capabilities & Limits

The Showcase & Handoff Hub provides the controlled journey, timing, speaker guidance, proof statements, limitation statements and recovery instructions. It does not calculate or persist business results.

## Demo Flow

The controlled demonstration routes are defined below.

## Five-minute executive route

1. **Home — 40 seconds:** frame the packaging value-engineering opportunity and disclose synthetic data.
2. **Project Dashboard — 40 seconds:** show project state, blockers and pending validation.
3. **Scenario Analysis — 50 seconds:** show cost, material, qualification, risk and recommendation.
4. **SourceMate — 40 seconds:** answer one predefined question about why the outcome exists.
5. **Calculation Evidence — 40 seconds:** trace one stored numeric result through assumptions, units and rounding.
6. **Decision Evidence Ledger — 45 seconds:** show chronology, revisions, hashes and unresolved controls.
7. **Capabilities & Limits — 35 seconds:** close with human approval, validation and production boundaries.

The route must remain within 330 seconds and six page transitions.

## Ten-minute detailed route

1. Frame the business problem on Home.
2. Show the controlled sequence in Guided Workflow.
3. Show specification differences, revisions and blockers in Specification Review.
4. Explain source classification and validation state in Data Upload.
5. Explain transparent controls in Business Rules & Thresholds.
6. Show the deterministic comparison in Scenario Analysis.
7. Show persisted rationale and validation requirements in Decision Records.
8. Use SourceMate for one supported “why” question.
9. Use Calculation Evidence for one supported stored result.
10. Use Decision Evidence Ledger for lifecycle and record lineage.
11. Close on Capabilities & Limits.

## Role-specific emphasis

### Procurement leader

Emphasize commercial opportunity, technical blockers, supplier-discussion readiness, evidence gaps, decision rationale and the distinction between potential and realized savings.

### Packaging specialist

Emphasize specification quality, material change, technical qualification, validation requirements, assumptions and approved-snapshot limitations.

### Technical and governance reviewer

Emphasize deterministic logic, project isolation, revisions, source hashes, fail-closed controls, canonical exports and human approval boundaries.

## Controlled explanation layers

- **SourceMate:** explains why a governed status or outcome exists.
- **Calculation Evidence:** shows how a supported stored numeric result was constructed.
- **Decision Evidence Ledger:** shows chronology and governed record relationships.

Do not describe SourceMate as an unrestricted chatbot. Do not describe Calculation Evidence as a recalculation engine. Do not describe the Evidence Ledger as a newly persisted audit event.

## What this proves

- Deterministic cost, material, qualification, risk and recommendation logic can be demonstrated reproducibly.
- Assumptions, rules, evidence gaps and claim limitations can be made visible.
- Stored results can be traced through numeric evidence.
- Governed records can be shown chronologically with revision and integrity references.
- The repository can be tested and handed over with repeatable commands.

## What this does not prove

- Production readiness or enterprise deployment.
- Validated supplier, laboratory, trial or production data.
- Realized savings or completed value capture.
- Engineering approval, regulatory approval or supplier award.
- Autonomous approval, allocation, negotiation or workflow execution.
- Authentication, enterprise integration, security certification or operational support.

## Application start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## New-user handoff

1. Confirm the governed repository and exact commit.
2. Confirm Python 3.12 and install `requirements.txt`.
3. Start the application with `streamlit run app.py`.
4. Disclose synthetic data before presenting results.
5. Select one governed journey in Showcase & Handoff.
6. Review blockers and pending validation before discussing benefits.
7. Use SourceMate, Calculation Evidence and Decision Evidence Ledger only for their defined responsibilities.
8. Run the complete test suite.
9. Review Capabilities & Limits before closing the handoff.

## Live-demo recovery

Use this short path during an interview or executive review:

1. Refresh the browser if the current page stops responding.
2. Return to Home and reopen Showcase & Handoff.
3. Select the five-minute executive journey and use the approved synthetic demonstration project.
4. Skip optional drill-downs when time is limited.
5. Close on Capabilities & Limits so governance boundaries remain explicit.

This live-demo path does not replace technical diagnosis and does not modify any governed record.

## Demo Recovery

If technical recovery is required:

1. Return to Home.
2. Confirm Python 3.12.
3. Reinstall `requirements.txt`.
4. Confirm the synthetic demo JSON is unchanged and valid.
5. Run:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

6. Restart Streamlit.
7. Use Capabilities & Limits as the fallback closing page if a governed record page is unavailable.

## Productionization answer

A production programme would separately require real category data, authenticated users, authorization controls, formal UAT, security and privacy controls, governed integrations, operational monitoring, audit design and validated value-realization tracking. None of those capabilities is claimed by this showcase release.
