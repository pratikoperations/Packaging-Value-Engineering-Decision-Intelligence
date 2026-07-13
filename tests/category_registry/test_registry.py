import pytest

from src.category_registry import default_registry


def test_default_registry_contains_all_eight_categories():
    registry = default_registry()
    assert registry.keys() == (
        "closures",
        "corrugated",
        "flexible_packaging",
        "folding_carton",
        "glass",
        "labels",
        "metal",
        "rigid_plastic",
    )


def test_each_category_has_objectives_and_change_types():
    for category in default_registry().list():
        assert category.objectives
        assert category.change_types
        assert category.supports_objective("Cost reduction")


def test_unknown_category_is_rejected():
    with pytest.raises(KeyError):
        default_registry().get("unknown")
