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

APP_ROOT_SELECTOR = '[data-testid="stAppViewContainer"]'
SIDEBAR_SELECTOR = '[data-testid="stSidebar"]'
HOME_HEADING = "Packaging Value Engineering Decision Intelligence"
STARTUP_TIMEOUT_SECONDS = 60
PAGE_TIMEOUT_MILLISECONDS = 30_000
ACTION_TIMEOUT_MILLISECONDS = 10_000

EXCEPTION_TEXT = (
    "StreamlitAPIException",
    "StreamlitPageNotFoundError",
    "Traceback (most recent call last)",
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
    "Engineering validation",
)

ACCEPTANCE_REPORT_KEYS = (
    "schema_version",
    "source_repository",
    "source_commit",
    "tested_branch",
    "generated_at_utc",
    "python_version",
    "playwright_version",
    "chromium_version",
    "desktop_viewport",
    "narrow_viewport",
    "scenario_id",
    "route_count",
    "unique_route_count",
    "json_export_valid",
    "markdown_export_valid",
    "calculation_evidence_visible",
    "physical_navigation_passed",
    "narrow_smoke_passed",
    "visible_exception_count",
    "page_error_count",
    "console_error_count",
    "tracked_files_unchanged",
    "overall_disposition",
)
