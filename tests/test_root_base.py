import pytest

from pet import PETRootBase, exact_root_base_from_int


def test_exact_root_base_detects_prime_power_with_maximal_exponent() -> None:
    root_base = exact_root_base_from_int(64)

    assert isinstance(root_base, PETRootBase)
    assert root_base.value == 64
    assert root_base.status == "exact"
    assert root_base.is_exact is True
    assert root_base.is_power is True
    assert root_base.base_value == 2
    assert root_base.exponent == 6
    assert root_base.exponent_object is not None
    assert root_base.exponent_object.value == 6
    assert [child.prime_label for child in root_base.exponent_object.children] == [2, 3]
    assert root_base.base_object is not None
    assert root_base.base_object.value == 2


def test_exact_root_base_detects_composite_base_power() -> None:
    root_base = exact_root_base_from_int(216)

    assert root_base.status == "exact"
    assert root_base.base_value == 6
    assert root_base.exponent == 3
    assert root_base.exponent_object is not None
    assert root_base.exponent_object.value == 3
    assert root_base.base_object is not None
    assert root_base.base_object.value == 6
    assert [child.prime_label for child in root_base.base_object.children] == [2, 3]


def test_exact_root_base_rejects_non_power() -> None:
    root_base = exact_root_base_from_int(72)

    assert root_base.value == 72
    assert root_base.status == "non-power"
    assert root_base.is_exact is False
    assert root_base.is_power is False
    assert root_base.base_value is None
    assert root_base.exponent is None
    assert root_base.exponent_object is None
    assert root_base.base_object is None


def test_exact_root_base_uses_maximal_exponent_not_smallest_power_form() -> None:
    # 65536 could be written as 256^2, 16^4, 4^8, or 2^16.
    # PET/PEG 2.0 exact root-base form uses maximal exponent.
    root_base = exact_root_base_from_int(65536)

    assert root_base.status == "exact"
    assert root_base.base_value == 2
    assert root_base.exponent == 16


def test_exact_root_base_serializes_base_object() -> None:
    root_base = exact_root_base_from_int(36)

    assert root_base.to_dict() == {
        "value": 36,
        "status": "exact",
        "exponent": 2,
        "exponent_object": {
            "value": 2,
            "role": "root",
            "kind": "composite",
            "prime_label": None,
            "address": [],
            "children": [
                {
                    "value": 2,
                    "role": "child",
                    "kind": "atomic",
                    "prime_label": 2,
                    "address": [2],
                    "children": [],
                }
            ],
        },
        "base_value": 6,
        "base_object": {
            "value": 6,
            "role": "root",
            "kind": "composite",
            "prime_label": None,
            "address": [],
            "children": [
                {
                    "value": 2,
                    "role": "child",
                    "kind": "atomic",
                    "prime_label": 2,
                    "address": [2],
                    "children": [],
                },
                {
                    "value": 3,
                    "role": "child",
                    "kind": "atomic",
                    "prime_label": 3,
                    "address": [3],
                    "children": [],
                },
            ],
        },
    }


def test_exact_root_base_rejects_values_below_two() -> None:
    with pytest.raises(ValueError, match="n must be >= 2"):
        exact_root_base_from_int(1)
