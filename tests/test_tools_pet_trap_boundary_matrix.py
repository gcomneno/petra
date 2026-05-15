from __future__ import annotations

import json
import subprocess
import sys


def run_matrix(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "tools/research/pet_trap_boundary_matrix.py",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_trap_boundary_matrix_reports_recoverable_transition() -> None:
    result = run_matrix("357357")

    lines = result.stdout.strip().splitlines()

    assert lines[0].startswith(
        "n\tcurrent_status\tcurrent_anchor"
    )

    assert len(lines) == 2

    assert "357357" in lines[1]
    assert "inactive-to-active" in lines[1]
    assert "redirect-recoverable-flat-k" in lines[1]
    assert "structural-prefix-trap-active-shadow" in lines[1]


def test_trap_boundary_matrix_reports_wall_stable_blocked() -> None:
    result = run_matrix("323323")

    lines = result.stdout.strip().splitlines()

    assert len(lines) == 2

    assert "323323" in lines[1]
    assert "inactive-stable" in lines[1]
    assert "wall-stable-blocked" in lines[1]
    assert "shadow-ranking-does-not-change-selection" in lines[1]


def test_trap_boundary_matrix_can_emit_json() -> None:
    result = run_matrix(
        "357357",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.trap_boundary_matrix.v0"

    row = payload["rows"][0]

    assert row["n"] == 357357
    assert row["current_anchor"] == "231"
    assert row["shadow_anchor"] == "3"

    assert (
        row["activity_transition"]
        == "inactive-to-active"
    )

    assert (
        row["classification"]
        == "redirect-recoverable-flat-k"
    )


def test_trap_boundary_matrix_can_filter_classification() -> None:
    result = run_matrix(
        "357357",
        "323323",
        "--classification-filter",
        "redirect-recoverable-flat-k",
    )

    lines = result.stdout.strip().splitlines()

    assert len(lines) == 2

    assert "357357" in lines[1]
    assert "323323" not in lines[1]


def test_trap_boundary_matrix_filter_can_return_empty() -> None:
    result = run_matrix(
        "357357",
        "--classification-filter",
        "wall-stable-blocked",
    )

    lines = result.stdout.strip().splitlines()

    assert len(lines) == 1
