import pytest

from pet import PETObject, pet_object_from_int, structurally_equivalent


def test_pet_object_model_builds_root_and_atomic_child_for_prime() -> None:
    root = pet_object_from_int(13)

    assert isinstance(root, PETObject)
    assert root.value == 13
    assert root.role == "root"
    assert root.kind == "composite"
    assert root.address == ()
    assert root.prime_label is None
    assert root.is_root is True
    assert root.is_composite is True

    assert len(root.children) == 1
    child = root.children[0]

    assert child.value == 13
    assert child.role == "child"
    assert child.kind == "atomic"
    assert child.prime_label == 13
    assert child.address == (13,)
    assert child.children == ()
    assert child.is_atomic is True


def test_pet_object_model_builds_recursive_children_from_exponents() -> None:
    root = pet_object_from_int(60)

    assert root.value == 60
    assert [child.prime_label for child in root.children] == [2, 3, 5]
    assert [child.address for child in root.children] == [(2,), (3,), (5,)]

    two_power = root.children[0]

    assert two_power.value == 4
    assert two_power.kind == "composite"
    assert two_power.prime_label == 2
    assert two_power.address == (2,)
    assert len(two_power.children) == 1

    exponent_object = two_power.children[0]

    assert exponent_object.value == 2
    assert exponent_object.kind == "atomic"
    assert exponent_object.prime_label == 2
    assert exponent_object.address == (2, 2)
    assert exponent_object.children == ()


def test_pet_object_model_serializes_identity_roles_and_children() -> None:
    root = pet_object_from_int(12)

    assert root.to_dict() == {
        "value": 12,
        "role": "root",
        "kind": "composite",
        "prime_label": None,
        "address": [],
        "children": [
            {
                "value": 4,
                "role": "child",
                "kind": "composite",
                "prime_label": 2,
                "address": [2],
                "children": [
                    {
                        "value": 2,
                        "role": "child",
                        "kind": "atomic",
                        "prime_label": 2,
                        "address": [2, 2],
                        "children": [],
                    }
                ],
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
    }


def test_pet_object_model_structural_equivalence_ignores_values_and_primes() -> None:
    assert structurally_equivalent(
        pet_object_from_int(12),
        pet_object_from_int(18),
    )

    assert not structurally_equivalent(
        pet_object_from_int(12),
        pet_object_from_int(72),
    )


def test_pet_object_model_rejects_values_below_two() -> None:
    with pytest.raises(ValueError, match="n must be >= 2"):
        pet_object_from_int(1)
