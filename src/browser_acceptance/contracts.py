from __future__ import annotations

PAGE_CONTRACTS = (
    ("Home", "Packaging Value Engineering Decision Intelligence", None),
    ("Showcase & Handoff", "Showcase", None),
    ("Project Dashboard", "Project Dashboard", "Workspace"),
    ("Guided Workflow", "Guided Workflow", "Workspace"),
    ("Specification Review", "Specification Review", "Inputs & Governance"),
    ("Data Upload", "Data Upload", "Inputs & Governance"),
    ("Business Rules & Thresholds", "Business Rules", "Inputs & Governance"),
    ("Scenario Analysis", "Scenario", "Analysis & Decision"),
    ("Decision Records", "Decision", "Analysis & Decision"),
    ("SourceMate", "SourceMate", "Evidence & Explanation"),
    ("Calculation Evidence", "Calculation Evidence", "Evidence & Explanation"),
    ("Decision Evidence Ledger", "Decision Evidence Ledger", "Evidence & Explanation"),
    ("Capabilities & Limits", "Capabilities", None),
)

SIDEBAR_GROUPS = {
    "Workspace": ("Project Dashboard", "Guided Workflow"),
    "Inputs & Governance": ("Specification Review", "Data Upload", "Business Rules & Thresholds"),
    "Analysis & Decision": ("Scenario Analysis", "Decision Records"),
    "Evidence & Explanation": ("SourceMate", "Calculation Evidence", "Decision Evidence Ledger"),
}

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "narrow": {"width": 412, "height": 915},
}

BROWSER_TEST_GROUPS = (
    "startup_and_home",
    "desktop_inputs_and_exports",
    "route_inventory",
    "sidebar_group_inventory",
    "narrow_responsive_smoke",
    "runtime_diagnostics",
)

VIEWPORT_RESPONSIBILITIES = {
    "desktop": {
        "startup_and_home",
        "desktop_inputs_and_exports",
        "route_inventory",
        "sidebar_group_inventory",
        "runtime_diagnostics",
    },
    "narrow": {
        "startup_and_home",
        "route_inventory",
        "sidebar_group_inventory",
        "narrow_responsive_smoke",
        "runtime_diagnostics",
    },
}

APP_ROOT_SELECTOR = '[data-testid="stAppViewContainer"]'
SIDEBAR_SELECTOR = '[data-testid="stSidebar"]'
STARTUP_TIMEOUT_SECONDS = 60
PAGE_TIMEOUT_MILLISECONDS = 30_000
ACTION_TIMEOUT_MILLISECONDS = 10_000

DIAGNOSTIC_FIELDS = (
    "test_group",
    "current_url",
    "target_title",
    "target_href",
    "visible",
    "bounding_box",
    "viewport",
    "sidebar_scroll_top",
    "sidebar_scroll_height",
)

MATRIX_REQUIRED_KEYS = (
    "status",
    "viewport",
    "groups",
    "route_inventory",
    "runtime_events",
)

REQUIRED_JSON_KEYS = (
    "metadata",
    "executive_summary",
    "project",
    "scenario",
    "baseline",
    "alternatives",
    "decision_controls",
    "calculation_evidence",
)
REQUIRED_MARKDOWN_TEXT = (
    "# Synthetic Data Disclosure",
    "# Packaging Value Engineering Decision Package",
    "## Independent Calculation Evidence",
)
