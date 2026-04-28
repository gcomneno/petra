#!/usr/bin/env python3
import json
import subprocess
import sys


def test_cli_metrics_json():
    result = subprocess.run(
        [sys.executable, "-m", "pet.cli", "metrics", "--json", "256"],
        capture_output=True,
        text=True,
        check=True,
    )

    expected = {
        "node_count": 3,
        "leaf_count": 1,
        "height": 3,
        "max_branching": 1,
        "branch_profile": [1, 1, 1],
        "recursive_mass": 2,
        "average_leaf_depth": 3.0,
        "leaf_depth_variance": 0.0,
    }

    assert json.loads(result.stdout) == expected
