from __future__ import annotations

import json
import subprocess
import sys


def run_matrix(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "tools/research/pet_shadow_ranking_matrix.py",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_shadow_ranking_matrix_reports_known_divergence() -> None:
    result = run_matrix(
        "--walls",
        "17017",
        "--contexts",
        "21",
        "--changed-only",
    )

    lines = result.stdout.strip().splitlines()

    assert lines[0].startswith("wall\tcontext\tn\tstatus")
    assert len(lines) == 2
    assert "17017\t21\t357357" in lines[1]
    assert "\t231\t1547\t3\t119119\tTrue\t" in lines[1]
    assert "active-partial-expandable beats inactive-flat-k-required" in lines[1]


def test_shadow_ranking_matrix_filters_unchanged_rows() -> None:
    result = run_matrix(
        "--walls",
        "1001",
        "--contexts",
        "30",
        "--changed-only",
    )

    lines = result.stdout.strip().splitlines()

    assert lines == [
        "wall\tcontext\tn\tstatus\tcurrent_anchor\tcurrent_residual\t"
        "shadow_anchor\tshadow_residual\tchanged\treason\tcandidate_count"
    ]


def test_shadow_ranking_matrix_can_emit_json() -> None:
    result = run_matrix(
        "--walls",
        "17017",
        "--contexts",
        "21",
        "--changed-only",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.shadow_ranking_matrix.v0"
    assert payload["profile"]["changed_only"] is True
    assert payload["rows"][0]["wall"] == 17017
    assert payload["rows"][0]["context"] == 21
    assert payload["rows"][0]["n"] == 357357
    assert payload["rows"][0]["current_anchor"] == "231"
    assert payload["rows"][0]["shadow_anchor"] == "3"
    assert payload["rows"][0]["changed"] is True
