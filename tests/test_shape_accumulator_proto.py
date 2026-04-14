from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PROTO = REPO_ROOT / "tools" / "shape_accumulator_proto.py"


def _run_proto(*args: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(PROTO), *args, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


TARGET = "84739348317483740132"


def test_moves_deduplicates_symmetric_leaf_inc_from_oracle_top_candidate():
    data = _run_proto(
        "moves",
        "None",
        "--max-mass", "11",
        "--preview", "10",
        "--target", TARGET,
        "--oracle-schedule", "10",
        "--candidate", "1",
    )

    assert data["selected_shape"] == [[], [], [], [[]]]
    assert data["distinct_move_count"] >= 6

    inc_leaf = None
    for row in data["moves"]:
        if (
            row["op"] == "INC"
            and row["representative_path"] == [0]
            and row["equivalent_paths"] == [[0], [1], [2]]
        ):
            inc_leaf = row
            break

    assert inc_leaf is not None, "missing deduplicated symmetric leaf INC move"
    assert inc_leaf["result_shape"] == [[], [], [[]], [[]]]
    assert inc_leaf["next_state"]["kind"] == "shallow"
    assert inc_leaf["next_state"]["compat_status"] == "open"
    assert inc_leaf["next_state"]["oracle_rank"] == 2


def test_moves_exact_start_fast_path_reports_exact_start():
    data = _run_proto(
        "moves",
        "[[], [], [[]], [[[[[[]]]]]]]",
        "--max-mass", "11",
        "--target", TARGET,
        "--oracle-schedule", "10",
    )

    assert data["selected_candidate_compat"] == "exact-start"
    assert data["selected_candidate_note"] == "fast-path-exact-start"
    assert data["selected_shape"] == [[], [], [[]], [[[[[[]]]]]]]
    assert data["distinct_move_count"] >= 10


def test_greedy_walk_follows_single_free_tower_policy():
    data = _run_proto(
        "greedy-walk",
        "None",
        "--max-mass", "11",
        "--preview", "10",
        "--target", TARGET,
        "--oracle-schedule", "10",
        "--steps", "4",
    )

    trace = data["trace"]
    assert len(trace) == 4

    expected_shapes = [
        [[], [], [], [[]]],
        [[], [], [[]], [[]]],
        [[], [], [[]], [[[]]]],
        [[], [], [[]], [[[[]]]]],
    ]
    got_shapes = [row["shape"] for row in trace]
    assert got_shapes == expected_shapes

    chosen = [row["chosen_move"] for row in trace]
    assert [row["op"] for row in chosen] == ["INC", "INC", "INC", "INC"]
    assert [row["representative_path"] for row in chosen] == [
        [0],
        [2, 0],
        [3, 0, 0],
        [3, 0, 0, 0],
    ]

    assert [row["moved_mass"] for row in chosen] == [6, 7, 8, 9]
    assert [row["next_state"]["compat_status"] for row in chosen] == ["open"] * 4
    assert [row["next_state"]["oracle_rank"] for row in chosen] == [2] * 4
