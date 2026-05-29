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


def test_pet_object_model_resolves_structural_addresses() -> None:
    root = pet_object_from_int(60)

    assert root.at(()) is root

    two_power = root.at((2,))
    assert two_power.value == 4
    assert two_power.kind == "composite"
    assert two_power.prime_label == 2

    exponent_leaf = root.at((2, 2))
    assert exponent_leaf.value == 2
    assert exponent_leaf.kind == "atomic"
    assert exponent_leaf.prime_label == 2

    assert root.at((3,)).value == 3
    assert root.at((5,)).value == 5


def test_pet_object_model_rejects_missing_structural_addresses() -> None:
    from pet import PETAddressError

    root = pet_object_from_int(60)

    import pytest

    with pytest.raises(PETAddressError, match="not found"):
        root.at((7,))

    with pytest.raises(PETAddressError, match="outside object"):
        root.at((2, 2)).at((3,))


def test_pet_object_model_walk_enumerates_addressed_objects_in_preorder() -> None:
    root = pet_object_from_int(60)

    walked = root.walk()

    assert [obj.address for obj in walked] == [(), (2,), (2, 2), (3,), (5,)]
    assert [obj.value for obj in walked] == [60, 4, 2, 3, 5]


def test_pet_object_model_addresses_and_address_map_are_consistent() -> None:
    root = pet_object_from_int(60)

    address_map = root.address_map()

    assert root.addresses() == tuple(address_map)
    assert address_map[()] is root
    assert address_map[(2,)].value == 4
    assert address_map[(2, 2)].value == 2
    assert address_map[(3,)].value == 3
    assert address_map[(5,)].value == 5


def test_pet_object_model_has_address_reports_validity() -> None:
    root = pet_object_from_int(60)

    assert root.has_address(()) is True
    assert root.has_address((2,)) is True
    assert root.has_address((2, 2)) is True
    assert root.has_address((7,)) is False
    assert root.has_address((2, 3)) is False


def test_pet_object_model_structural_identity_key_is_concrete() -> None:
    left = pet_object_from_int(12)
    right = pet_object_from_int(18)

    assert structurally_equivalent(left, right)
    assert left.structural_identity_key() != right.structural_identity_key()
    assert left.structural_identity_key() == pet_object_from_int(12).structural_identity_key()


def test_pet_object_model_address_resolution_classifies_valid_missing_and_blocked_leaf() -> None:
    root = pet_object_from_int(60)

    assert root.address_resolution(()) == "valid"
    assert root.address_resolution((2,)) == "valid"
    assert root.address_resolution((2, 2)) == "valid"
    assert root.address_resolution((7,)) == "missing"
    assert root.address_resolution((3, 2)) == "blocked-at-leaf"


def test_pet_object_model_compare_address_classifies_stable_created_destroyed() -> None:
    from pet import compare_address

    before = pet_object_from_int(60)
    after_created = pet_object_from_int(420)
    after_destroyed = pet_object_from_int(15)

    stable = compare_address(before, pet_object_from_int(60), (2,))
    created = compare_address(before, after_created, (7,))
    destroyed = compare_address(before, after_destroyed, (2,))

    assert stable.outcome == "stable"
    assert stable.before_resolution == "valid"
    assert stable.after_resolution == "valid"
    assert stable.before_object is not None
    assert stable.after_object is not None

    assert created.outcome == "created"
    assert created.before_resolution == "missing"
    assert created.after_resolution == "valid"

    assert destroyed.outcome == "destroyed"
    assert destroyed.before_resolution == "valid"
    assert destroyed.after_resolution == "missing"


def test_pet_object_model_compare_address_classifies_retargeted() -> None:
    from pet import compare_address

    before = pet_object_from_int(60)
    after = pet_object_from_int(24)

    comparison = compare_address(before, after, (2,))

    assert comparison.outcome == "retargeted"
    assert comparison.before_resolution == "valid"
    assert comparison.after_resolution == "valid"
    assert comparison.before_object is not None
    assert comparison.after_object is not None
    assert comparison.before_object.value == 4
    assert comparison.after_object.value == 8
    assert comparison.before_object.structural_identity_key() != comparison.after_object.structural_identity_key()


def test_pet_object_model_compare_address_classifies_blocked_at_leaf() -> None:
    from pet import compare_address

    before = pet_object_from_int(60)
    after = pet_object_from_int(60)

    comparison = compare_address(before, after, (3, 2))

    assert comparison.outcome == "blocked-at-leaf"
    assert comparison.before_resolution == "blocked-at-leaf"
    assert comparison.after_resolution == "blocked-at-leaf"
    assert comparison.before_object is None
    assert comparison.after_object is None


def test_pet_object_model_address_comparison_serializes() -> None:
    from pet import compare_address

    comparison = compare_address(pet_object_from_int(60), pet_object_from_int(420), (7,))

    payload = comparison.to_dict()

    assert payload["address"] == [7]
    assert payload["outcome"] == "created"
    assert payload["before_resolution"] == "missing"
    assert payload["after_resolution"] == "valid"
    assert payload["before_object"] is None
    assert payload["after_object"]["value"] == 7
