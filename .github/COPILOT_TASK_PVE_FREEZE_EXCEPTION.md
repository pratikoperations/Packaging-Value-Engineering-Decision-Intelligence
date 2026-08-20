# Bounded PVE stabilization-freeze exception

Repository: pratikoperations/Packaging-Value-Engineering-Decision-Intelligence
Base main SHA: a85bee995e873fe86399c50f6e93865b432246f0
Branch: fix/pve-freeze-exception-demo-sidebar

## Objective
Correct two demonstrated portfolio usability defects only:
1. Controlled Scenarios can continue to display a stale `insufficient_data` evaluation after the PVE demo dataset/threshold changes or before the complete demo seed is refreshed.
2. Expanded Streamlit sidebar is materially oversized on narrow/mobile viewports.

## Required implementation

### Controlled Scenarios
- Preserve immutable dataset/history behavior and existing fail-closed engines.
- Preserve current `PVE-DEMO` latest-dataset default.
- Bind `evaluated_controlled_scenario` display state to the exact current project + dataset_id + threshold_profile_id selection. If selection changes, clear the stale evaluated result before rendering it.
- For the controlled PVE demo, detect when the newest available dataset does not represent the complete showcase seed. Provide a clear, bounded refresh action or guidance that invokes/reuses the existing governed `seed_portfolio_demo()` path; do not silently overwrite immutable records.
- After a successful refresh/reseed, make the new/latest immutable dataset the selected demo dataset and clear any stale evaluated scenario.
- Do not weaken technical qualification, risk completeness, thresholds, engineering validation, human approval, or recommendation governance.
- Do not change scenario/recommendation/risk/qualification engine logic.

### Mobile sidebar
- Keep `st.navigation(..., position="hidden")`, current `st.page_link` navigation, opener semantics and accessibility.
- Add the smallest global responsive presentation rule so expanded `[data-testid="stSidebar"]` on narrow screens uses a materially smaller width (target around `min(82vw, 320px)` or equivalent), rather than consuming ~85-90%+ of the viewport.
- Do not redesign navigation or hide labels.
- Desktop behavior should remain effectively unchanged.

### Tests
Add/update focused deterministic tests proving:
- stale controlled-scenario state is invalidated when dataset/threshold selection changes;
- demo refresh uses the existing governed seeder and does not overwrite history;
- latest PVE demo dataset remains the default;
- mobile sidebar CSS/rule is present with the bounded width contract;
- hidden navigation and page-link contract remain unchanged;
- no engine/governance boundary is weakened.

## Scope boundaries
Expected durable files should be limited to application presentation/state handling and focused tests. No workflow, dependency, engine, business calculation, approval-boundary, production-readiness, release or deployment change.

Delete this temporary task file before finalizing the PR.

Run focused tests locally if possible, but do not rerun GitHub Actions manually. Leave PR Draft for authoritative PR-head CI.