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

STARTUP_TIMEOUT_SECONDS = 60
PAGE_TIMEOUT_MILLISECONDS = 30_000
ACTION_TIMEOUT_MILLISECONDS = 10_000

REQUIRED_JSON_KEYS = (
    "metadata", "project", "scenario", "alternatives", "recommendation", "calculation_evidence"
)
REQUIRED_MARKDOWN_TEXT = (
    "# Synthetic Data Disclosure",
    "# Packaging Value Engineering Decision Package",
    "## Independent Calculation Evidence",
)
