from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "tools" / "shape_rewrite_arithmetic_v0.py"


def _run_tool(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(TOOL), *args, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_neighbors_smoke_for_mixed_shape():
    data = _run_tool("neighbors", "[[], [[]]]")

    assert data["shape"] == [[], [[]]]
    assert data["neighbor_count"] == 6

    got = [(row["op"], row["path"], row["result"]) for row in data["neighbors"]]
    expected = [
        ("DEC", [1], [[], []]),
        ("DROP", [], [[[]]]),
        ("INC", [0], [[[]], [[]]]),
        ("INC", [1], [[], [[], []]]),
        ("INC", [1, 0], [[], [[[]]]]),
        ("NEW", [], [[], [], [[]]]),
    ]
    assert got == expected


def test_distance_and_path_match_small_example():
    dist = _run_tool("distance", "[[], []]", "[[], [[]]]")
    path = _run_tool("path", "[[], []]", "[[], [[]]]")

    assert dist["distance"] == 1
    assert path["distance"] == 1
    assert path["path"] == [
        {
            "op": "INC",
            "path": [0],
            "result": [[], [[]]],
        }
    ]


def test_diff_interprets_left_minus_right_as_rewrite_from_rhs_to_lhs():
    data = _run_tool("diff", "[[], [[]]]", "[[], []]")

    assert data["lhs"] == [[], [[]]]
    assert data["rhs"] == [[], []]
    assert data["cost"] == 1
    assert data["rewrite"] == [
        {
            "op": "INC",
            "path": [0],
            "result": [[], [[]]],
        }
    ]
