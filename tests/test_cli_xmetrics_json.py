import json
import subprocess
import sys


def test_cli_xmetrics_json():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pet.cli",
            "xmetrics",
            "72",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    expected_keys = {
        "node_count",
        "leaf_count",
        "height",
        "max_branching",
        "branch_profile",
        "recursive_mass",
        "average_leaf_depth",
        "leaf_depth_variance",
        "verticality_ratio",
        "structural_asymmetry",
        "subtree_mixing_score",
        "has_root_mixed_simple_pattern",
    }

    assert set(data.keys()) == expected_keys

    assert data["node_count"] == 4
    assert data["leaf_count"] == 2
    assert data["height"] == 2
    assert data["max_branching"] == 2
    assert data["branch_profile"] == [2, 2]
    assert data["recursive_mass"] == 2
    assert data["average_leaf_depth"] == 2.0
    assert data["leaf_depth_variance"] == 0.0

    assert data["verticality_ratio"] == 0.5
    assert data["structural_asymmetry"] == 0.0
    assert data["subtree_mixing_score"] == 0.0
    assert data["has_root_mixed_simple_pattern"] is False
