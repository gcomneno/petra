from __future__ import annotations

import json
import subprocess
import sys
from typing import Any


def run_probe(n: int, *args: str) -> dict[str, Any]:
    result = subprocess.run(
        [
            sys.executable,
            "tools/research/pet_completion_aware_residual_probe.py",
            str(n),
            *args,
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    return json.loads(result.stdout)


def test_completion_aware_probe_marks_selected_trap_door_candidate() -> None:
    probe = run_probe(21021)

    assert probe["schema"] == "pet.completion_aware_residual_probe.v0"
    assert probe["n"] == 21021
    assert probe["status"] == "blocked-no-verified-anchor"
    assert probe["selected_anchor"] == "21"
    assert probe["selected_residual"] == "1001"
    assert probe["terminal_residual"] == "1001"

    selected = next(
        row
        for row in probe["candidates"]
        if row["anchor"] == probe["selected_anchor"]
    )

    assert selected["residual"] == "1001"
    assert selected["residual_final_status"] == "flat-k-scan-required"
    assert selected["classification"] == "selected-trap-door-candidate"


def test_completion_aware_probe_marks_lateral_door_candidate() -> None:
    probe = run_probe(30030)

    assert probe["status"] == "complete"
    assert probe["selected_anchor"] == "5005"
    assert probe["selected_residual"] == "6"
    assert probe["terminal_residual"] == "1"

    selected = next(
        row
        for row in probe["candidates"]
        if row["anchor"] == probe["selected_anchor"]
    )

    assert selected["residual"] == "6"
    assert selected["residual_final_status"] == "solved-by-same-shape-scan"
    assert selected["classification"] == "completion-friendly"


def test_completion_aware_probe_reflects_flat_k_profile() -> None:
    probe = run_probe(21021, "--auto-flat-k-scan")

    assert probe["profile"]["auto_flat_k_scan"] is True
    assert probe["status"] == "complete"
    assert probe["selected_anchor"] == "21"
    assert probe["selected_residual"] == "1001"
    assert probe["terminal_residual"] == "1"

    selected = next(
        row
        for row in probe["candidates"]
        if row["anchor"] == probe["selected_anchor"]
    )

    assert selected["residual_final_status"] == "partial-factorization-by-flat-k-scan"
    assert selected["classification"] == "expandable-with-active-mode"
