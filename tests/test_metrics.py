#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pet import (
    average_leaf_depth,
    leaf_depth_variance,
    branch_profile,
    encode,
    height,
    leaf_count,
    max_branching,
    metrics_dict,
    node_count,
    recursive_mass,
)

@pytest.mark.parametrize(
    "n, expected_nodes, expected_leaves, expected_height, expected_branching, expected_profile, expected_mass, expected_avg_leaf_depth, expected_leaf_depth_variance",
    [
        (2,   1, 1, 1, 1, [1],       0, 1.0,     0.0),
        (4,   2, 1, 2, 1, [1, 1],    1, 2.0,     0.0),
        (12,  3, 2, 2, 2, [2, 1],    1, 1.5,     0.25),
        (256, 3, 1, 3, 1, [1, 1, 1], 2, 3.0,     0.0),
        (72,  4, 2, 2, 2, [2, 2],    2, 2.0,     0.0),
        (360, 5, 3, 2, 3, [3, 2],    2, 5 / 3,   2 / 9),
    ],
)
def test_metrics(
    n,
    expected_nodes,
    expected_leaves,
    expected_height,
    expected_branching,
    expected_profile,
    expected_mass,
    expected_avg_leaf_depth,
    expected_leaf_depth_variance,
):
    tree = encode(n)
    assert node_count(tree) == expected_nodes, f"node_count failed for {n}"
    assert leaf_count(tree) == expected_leaves, f"leaf_count failed for {n}"
    assert height(tree) == expected_height, f"height failed for {n}"
    assert max_branching(tree) == expected_branching, f"max_branching failed for {n}"
    assert branch_profile(tree) == expected_profile, f"branch_profile failed for {n}"
    assert recursive_mass(tree) == expected_mass, f"recursive_mass failed for {n}"
    assert average_leaf_depth(tree) == pytest.approx(expected_avg_leaf_depth), (
        f"average_leaf_depth failed for {n}"
    )
    assert leaf_depth_variance(tree) == pytest.approx(expected_leaf_depth_variance), (
        f"leaf_depth_variance failed for {n}"
    )


def test_metrics_dict_exposes_exact_canonical_metric_set():
    tree = encode(72)

    expected_keys = {
        "node_count",
        "leaf_count",
        "height",
        "max_branching",
        "branch_profile",
        "recursive_mass",
        "average_leaf_depth",
        "leaf_depth_variance",
    }

    assert set(metrics_dict(tree).keys()) == expected_keys
