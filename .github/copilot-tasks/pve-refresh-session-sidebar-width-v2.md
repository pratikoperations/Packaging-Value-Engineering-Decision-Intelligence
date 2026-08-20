# Bounded task — fix Streamlit demo refresh state and mobile sidebar width

Repository baseline: main SHA 11f389a1030ade727bff0126205c46051d1b3672
Branch: fix/pve-refresh-session-sidebar-width-v2

Reproduced defect 1:
- pages/04_Controlled_Scenarios.py creates selectboxes with keys controlled_scenario_dataset_label and controlled_scenario_threshold_label.
- In the Refresh complete demonstration dataset button path, the code later assigns directly to those same widget-backed session_state keys in the same run.
- Streamlit raises StreamlitAPIException because a widget-owned session_state key cannot be mutated after widget instantiation.

Required correction:
- do not assign to DATASET_SELECT_KEY or THRESHOLD_SELECT_KEY after their selectboxes exist;
- add separate pending/deferred selection keys, e.g. controlled_scenario_pending_dataset_label and controlled_scenario_pending_threshold_label;
- at the start of the page, before selectbox instantiation, consume pending labels into the widget keys only if valid for the current options; otherwise fail closed/fall back deterministically;
- refresh button may set pending keys, stable dataset/threshold IDs, active threshold ID, clear evaluated scenario, set feedback, then st.rerun();
- preserve immutable dataset history and governed seed behavior;
- preserve stale evaluated-scenario invalidation.

Reproduced defect 2:
- app.py mobile CSS only sets min-width/max-width on [data-testid="stSidebar"][aria-expanded="true"], which does not materially constrain the rendered width on the current Streamlit mobile DOM.

Required correction:
- keep the exact Streamlit sidebar and navigation semantics;
- for max-width: 768px, set explicit bounded width and flex-basis as well as min/max width using !important if required by Streamlit CSS specificity;
- target approximately 72vw capped at 280px; minimum readable width may be around 240px, but do not exceed 280px;
- ensure inner sidebar content cannot independently force a wider width; use box-sizing and child width/max-width rules if necessary;
- do not hide, replace, or redesign navigation;
- preserve sidebar opener/collapse behavior.

Tests required:
- prove refresh path never writes widget-owned selectbox keys after widget creation; preferably factor a helper that stores pending selections and unit-test it;
- prove pending selections are consumed before widget rendering and invalid pending values fail closed/deterministically;
- preserve stale-result invalidation tests;
- update sidebar contract test to require explicit width/flex-basis and <= 280px cap on mobile;
- no browser workflow or dependency changes.

Scope ceiling:
- pages/04_Controlled_Scenarios.py
- app.py
- focused tests under tests/application and/or tests/scenario_execution
- this temporary task file, which MUST be deleted before finalization.

Do not modify engines, calculations, thresholds, risk, qualification, recommendation logic, governed data, dependencies, workflows, docs unrelated to the fix, deployment, release, tags, or production-readiness claims.

Run focused tests and full unittest suite. Leave PR Draft. Do not merge.