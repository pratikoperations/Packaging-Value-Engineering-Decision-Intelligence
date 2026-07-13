from __future__ import annotations

SHEET_NAMES = (
    "INSTRUCTIONS",
    "PROJECT",
    "BASELINE",
    "PROPOSED",
    "COMMERCIAL",
    "LOGISTICS",
    "QUALITY_TESTS",
    "DOCUMENT_REGISTER",
)

SOURCE_CLASSIFICATIONS = (
    "uploaded_fact",
    "manually_entered_fact",
    "supplier_declared",
    "laboratory_tested",
    "predicted",
    "assumption",
)

VALIDATION_STATUSES = ("not_reviewed", "valid", "invalid", "missing", "expired")
REQUIREMENT_LEVELS = ("mandatory", "recommended", "optional")
CONTEXT_VALUES = ("baseline", "proposed")

PROJECT_HEADERS = (
    "field_key", "field_label", "requirement", "value", "unit",
    "description", "example", "source_classification", "evidence_reference",
    "supplier_name", "test_date", "validation_status",
)

VALUE_HEADERS = PROJECT_HEADERS

COMMERCIAL_FIELDS = (
    ("annual_volume", "Annual volume", "mandatory", "units/year", "100000"),
    ("current_unit_cost", "Current unit cost", "mandatory", "currency/unit", "12.50"),
    ("proposed_unit_cost", "Proposed unit cost", "recommended", "currency/unit", "11.80"),
    ("realization_percent", "Expected realization percentage", "optional", "%", "85"),
    ("testing_cost", "Testing cost", "optional", "currency", "50000"),
    ("tooling_cost", "Tooling cost", "optional", "currency", "100000"),
    ("implementation_cost", "Implementation cost", "optional", "currency", "25000"),
    ("qualification_cost", "Qualification cost", "optional", "currency", "15000"),
)

LOGISTICS_FIELDS = (
    ("shipment_mode", "Shipment mode", "recommended", "text", "Road"),
    ("route", "Route", "recommended", "text", "Plant A to DC B"),
    ("pallet_pattern", "Pallet pattern", "optional", "text", "10 x 5"),
    ("storage_duration_days", "Storage duration", "recommended", "days", "30"),
    ("temperature_c", "Temperature", "optional", "C", "25"),
    ("humidity_percent", "Humidity", "optional", "%RH", "65"),
)

DOCUMENT_HEADERS = (
    "document_id", "document_type", "document_name", "category", "context",
    "supplier", "document_date", "valid_until", "file_reference",
    "verification_status", "requirement", "upload_status", "reviewer_comments",
)

QUALITY_HEADERS = (
    "test_name", "requirement", "critical", "context", "result_value",
    "unit", "source_classification", "evidence_reference", "test_date",
    "supplier_or_laboratory", "validation_status", "reviewer_comments",
)
