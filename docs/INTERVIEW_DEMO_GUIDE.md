# Interview Demonstration Guide

## Purpose
Demonstrate how packaging engineering, cost, risk, and decision logic are combined into a transparent management recommendation without autonomous approval or supplier allocation.

## Recommended Demo Length
8–12 minutes.

## Demo Flow

### 1. Frame the business problem
Explain that the synthetic case compares a current corrugated shipping case with proposed design alternatives. The objective is to identify value-engineering opportunities while protecting technical performance, supply continuity, and implementation readiness.

### 2. Show the data foundation
Open `data/demo/corrugated_shipping_cases.json` and highlight:
- baseline and proposed alternatives
- annual volume and currency
- cost inputs and material weights
- technical requirements and evidence
- quality, supply, and implementation risks

State clearly that the dataset is synthetic and the logic is deterministic.

### 3. Run the application

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### 4. Demonstrate a scenario
- Change annual volume.
- Apply a visible cost adjustment to one alternative.
- Apply a visible material-weight adjustment.
- Explain that every assumption is explicit and bounded.

### 5. Explain the comparison
Use the comparison table to discuss:
- unit and annual cost
- annual savings versus baseline
- material change versus baseline
- technical qualification status
- risk level and data completeness
- recommendation status

### 6. Explain the recommendation gate
Show that:
- technical failure or critical risk blocks recommendation
- missing technical evidence produces insufficient data
- conditional qualification or open validation produces a conditional recommendation
- the preferred alternative is ordered transparently without an opaque score

### 7. Export the decision package
Download:
- `pve_decision_package.json` for machine-readable review
- `pve_decision_report.md` for human-readable management review

Explain that both exports include assumptions, results, qualification, risk, rationale, constraints, validation requirements, provenance, and fixed decision controls.

### 8. Close with governance boundaries
State that the tool:
- does not approve packaging autonomously
- does not rank or allocate suppliers
- does not replace engineering trials or evidence
- does not finalize the draft integration contract
- provides decision support, traceability, and repeatable analysis

## Interview Questions and Suggested Answers

### What business value does this create?
It reduces manual comparison effort, makes savings assumptions visible, prevents technically weak alternatives from appearing financially attractive, and creates a reusable decision record for management review.

### Why use deterministic rules instead of an LLM?
Cost, material, qualification, risk, and recommendation gates require repeatability and auditability. Generative AI can help explain results later, but it should not replace the controlled calculation and approval logic.

### How would this move toward production?
Add real category data, authenticated users, workflow approvals, audit logs, formal UAT, security controls, governed integrations, and validated value-realization tracking.

### What is intentionally excluded?
Supplier allocation, negotiation, autonomous approval, predictive claims, and enterprise integration are outside this interview-release scope.

## Demo Recovery
If the demo fails:
1. Confirm Python 3.12.
2. Reinstall `requirements.txt`.
3. Run `python -m unittest discover -s tests -p "test_*.py" -v`.
4. Confirm the synthetic demo JSON is unchanged and valid.
5. Restart Streamlit.
