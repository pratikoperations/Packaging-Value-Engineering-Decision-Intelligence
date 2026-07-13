# Power BI Dashboard Specification

## Audience
Procurement managers, category managers, packaging engineers, procurement excellence leads, and executives.

## Pages
1. **Executive Overview** — portfolio KPIs, potential savings, risk, qualification, and actions.
2. **Cost and Savings** — baseline versus proposed cost, annualized savings, cost waterfall, and sensitivity.
3. **Alternative Comparison** — side-by-side cost, qualification, risk, threshold, and decision status.
4. **Technical Qualification** — pass/fail evidence, gaps, blocked alternatives, and engineering-review requirements.
5. **Risk Dashboard** — severity, category, critical risks, mitigation status, and project drill-through.
6. **Scenario Analysis** — assumptions, scenario comparison, volume sensitivity, and threshold outcomes.
7. **Decision History** — immutable snapshots, source references, status, and control evidence.
8. **Interview Story** — problem, method, controls, outcome, and business value in a seven-minute narrative.

## Design Rules
- executive summary first, evidence on drill-through
- no unsupported AI claims
- recommendation-for-review must never be labelled approval
- show dataset and scenario version context
- disclose synthetic demonstration data where applicable
- use consistent KPI definitions from the approved dictionary

## Acceptance Criteria
- every KPI reconciles to authoritative PVE output
- filters preserve project isolation
- baseline cannot appear as preferred recommendation
- archived-project history remains visible but read-only
- all pages work in Power BI Desktop before publishing is considered