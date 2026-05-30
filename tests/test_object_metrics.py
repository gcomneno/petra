import pytest

from pet import (
    encode,
    metrics_dict,
    pet_object_average_leaf_depth,
    pet_object_branch_profile,
    pet_object_from_int,
    pet_object_height,
    pet_object_leaf_count,
    pet_object_leaf_depth_variance,
    pet_object_max_branching,
    pet_object_metrics_dict,
    pet_object_node_count,
    pet_object_recursive_mass,
)


SEEDS = [2, 3, 4, 6, 8, 12, 18, 30, 60, 72, 216, 960, 65536]


@pytest.mark.parametrize("n", SEEDS)
def test_pet_object_metrics_match_legacy_metrics(n: int) -> None:
    obj = pet_object_from_int(n)

    assert pet_object_metrics_dict(obj) == metrics_dict(encode(n))


def test_pet_object_metric_functions_for_60() -> None:
    obj = pet_object_from_int(60)

    assert pet_object_node_count(obj) == 4
    assert pet_object_leaf_count(obj) == 3
    assert pet_object_height(obj) == 2
    assert pet_object_max_branching(obj) == 3
    assert pet_object_recursive_mass(obj) == 1
    assert pet_object_branch_profile(obj) == [3, 1]
    assert pet_object_average_leaf_depth(obj) == pytest.approx(4 / 3)
    assert pet_object_leaf_depth_variance(obj) == pytest.approx(2 / 9)


def test_pet_object_metrics_work_on_selected_composite_child() -> None:
    selected = pet_object_from_int(60).at((2,))

    assert pet_object_metrics_dict(selected) == metrics_dict(encode(4))


def test_pet_object_metrics_work_on_selected_atomic_child() -> None:
    selected = pet_object_from_int(60).at((3,))

    assert pet_object_metrics_dict(selected) == metrics_dict(encode(3))


def test_pet_object_metrics_deep_power_matches_legacy() -> None:
    obj = pet_object_from_int(65536)

    assert pet_object_metrics_dict(obj) == metrics_dict(encode(65536))
    assert pet_object_branch_profile(obj) == metrics_dict(encode(65536))["branch_profile"]


def test_pet_object_recursive_mass_counts_all_exponent_object_nodes() -> None:
    obj = pet_object_from_int(960)

    assert pet_object_recursive_mass(obj) == 2
    assert pet_object_metrics_dict(obj)["recursive_mass"] == metrics_dict(encode(960))[
        "recursive_mass"
    ]
