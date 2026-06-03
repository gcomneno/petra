from __future__ import annotations

import json
import subprocess
import sys


def _run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pet.cli", *args],
        capture_output=True,
        text=True,
        check=True,
    )


def test_cli_structural_route_from_unit_root_text() -> None:
    result = _run_cli(
        "structural-route",
        "2",
        "--max-depth",
        "1",
    )

    assert result.stdout.strip().splitlines() == [
        "PET STRUCTURAL ROUTE",
        "",
        "source_n = 1",
        "target_value = 2",
        "max_depth = 1",
        "max_paths = 200",
        "found = true",
        "reason = path-found",
        "",
        "selected_path:",
        "depth = 1",
        "values = [1, 2]",
        "labels = ['NEW(parent_address=[],q=2)']",
        "",
        "trace_certificate:",
        "valid = true",
        "reason = trace-replayed",
        "checked_steps = 1",
        "",
        (
            "claim = bounded PET/PEG structural route planning; "
            "selected path is first match in deterministic bounded traversal, "
            "not a global optimality claim"
        ),
    ]


def test_cli_structural_route_from_unit_root_json() -> None:
    result = _run_cli(
        "structural-route",
        "2",
        "--max-depth",
        "1",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.structural_route.v0"
    assert payload["source_n"] == 1
    assert payload["target_value"] == 2
    assert payload["found"] is True
    assert payload["selected_path"]["values"] == [1, 2]
    assert payload["selected_path"]["labels"] == ["NEW(parent_address=[],q=2)"]
    assert payload["trace_certificate"]["valid"] is True
    assert payload["trace_certificate"]["reason"] == "trace-replayed"


def test_cli_structural_route_reports_no_path_within_bound() -> None:
    result = _run_cli(
        "structural-route",
        "2",
        "--max-depth",
        "0",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["found"] is False
    assert payload["reason"] == "no-path-within-bound"
    assert payload["selected_path"] is None
    assert payload["trace_certificate"] is None
