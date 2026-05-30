from pet import (
    decode,
    encode,
    pet_object_from_int,
    pet_object_from_legacy_tree,
    pet_object_to_legacy_tree,
    structurally_equivalent,
)


def test_pet_object_from_legacy_tree_rebuilds_equivalent_object() -> None:
    legacy = encode(60)

    obj = pet_object_from_legacy_tree(legacy)

    assert obj.value == 60
    assert obj.to_dict() == pet_object_from_int(60).to_dict()


def test_pet_object_to_legacy_tree_round_trips_root_object() -> None:
    obj = pet_object_from_int(60)

    legacy = pet_object_to_legacy_tree(obj)

    assert legacy == encode(60)
    assert decode(legacy) == 60


def test_pet_object_to_legacy_tree_handles_selected_composite_child() -> None:
    obj = pet_object_from_int(60)
    selected = obj.at((2,))

    legacy = pet_object_to_legacy_tree(selected)

    assert legacy == encode(4)
    assert decode(legacy) == 4


def test_pet_object_to_legacy_tree_handles_selected_atomic_child() -> None:
    obj = pet_object_from_int(60)
    selected = obj.at((3,))

    legacy = pet_object_to_legacy_tree(selected)

    assert legacy == encode(3)
    assert decode(legacy) == 3


def test_legacy_bridge_preserves_structural_equivalence() -> None:
    left = pet_object_from_legacy_tree(encode(12))
    right = pet_object_from_legacy_tree(encode(18))

    assert structurally_equivalent(left, right)


def test_legacy_bridge_round_trips_seed_values() -> None:
    for n in [2, 3, 4, 6, 8, 12, 18, 60, 72, 216, 960]:
        obj = pet_object_from_int(n)
        legacy = pet_object_to_legacy_tree(obj)
        rebuilt = pet_object_from_legacy_tree(legacy)

        assert decode(legacy) == n
        assert rebuilt.to_dict() == obj.to_dict()
