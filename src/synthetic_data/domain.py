from __future__ import annotations

SYNTHETIC_DISCLOSURE = (
    "Synthetic demonstration data. Not sourced from actual suppliers. "
    "Not suitable for negotiation, supplier award, engineering approval, "
    "regulatory approval or realized-savings claims."
)

AUTHORIZED_UNITS = {
    "mm", "g", "kg", "INR_per_case", "cases_per_year", "km", "days",
    "kgf", "unitless", "cases_per_pallet", "percent",
}
AUTHORIZED_CURRENCIES = {"INR"}
AUTHORIZED_PROVENANCE = {
    "synthetic_cost_assumption",
    "synthetic_technical_assumption",
    "synthetic_logistics_assumption",
    "synthetic_volume_assumption",
    "synthetic_risk_assumption",
    "derived_from_other_synthetic_record",
}


class SyntheticDataError(ValueError):
    """Fail-closed error raised by governed synthetic-data validation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
