"""Governed synthetic procurement data loading and compatibility utilities."""

from .compatibility_adapter import build_legacy_dataset
from .domain import SYNTHETIC_DISCLOSURE, SyntheticDataError
from .loader import load_governed_package

__all__ = [
    "SYNTHETIC_DISCLOSURE",
    "SyntheticDataError",
    "build_legacy_dataset",
    "load_governed_package",
]
