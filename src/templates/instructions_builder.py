from __future__ import annotations


def build_instructions(category_name: str, objective: str, change_type: str) -> list[tuple[str, str]]:
    return [
        ("Template purpose", "Collect structured intake data for PVE 1.1 readiness assessment."),
        ("Packaging category", category_name),
        ("Project objective", objective),
        ("Change type", change_type),
        ("How to complete", "Complete mandatory fields first, then recommended fields. Optional fields improve context."),
        ("Source classification", "Classify each value as uploaded_fact, manually_entered_fact, supplier_declared, laboratory_tested, predicted, or assumption."),
        ("Evidence", "Enter a filename or reference. A filename alone does not mean the evidence was verified."),
        ("Governance", "Supplier-declared and predicted values must not be presented as laboratory-tested values."),
        ("Approval limitation", "This workbook supports intake and readiness only. Engineering validation and human approval remain mandatory."),
        ("Macros", "No macros are used or required."),
    ]
