from __future__ import annotations

import json
import subprocess
import sys


def run_probe(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "tools/research/pet_structural_route_probe.py",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def test_structural_route_probe_finds_target_value_path() -> None:
    result = run_probe(
        "60",
        "--target-value",
        "420",
        "--max-depth",
        "1",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["schema"] == "pet.structural_route_probe.v0"
    assert payload["found"] is True
    assert payload["reason"] == "path-found"
    assert payload["selection_policy"] == "first-match-in-deterministic-bounded-bfs"
    assert "not a global optimality claim" in payload["claim"]

    path = payload["selected_path"]
    assert path["depth"] == 1
    assert path["values"] == [60, 420]
    assert path["labels"] == ["NEW(parent_address=[],q=7)"]

    certificate = payload["trace_certificate"]
    assert certificate["valid"] is True
    assert certificate["reason"] == "trace-replayed"
    assert certificate["checked_steps"] == 1


def test_structural_route_probe_finds_target_shape_path() -> None:
    result = run_probe(
        "60",
        "--target-shape-of",
        "420",
        "--max-depth",
        "1",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["found"] is True
    assert payload["target_shape_of"] == 420
    assert payload["selected_path"]["values"] == [60, 420]
    assert payload["selected_path"]["labels"] == ["NEW(parent_address=[],q=7)"]
    assert payload["trace_certificate"]["valid"] is True


def test_structural_route_probe_reports_no_path_within_bound() -> None:
    result = run_probe(
        "60",
        "--target-value",
        "420",
        "--max-depth",
        "0",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["found"] is False
    assert payload["reason"] == "no-path-within-bound"
    assert payload["selected_path"] is None
    assert payload["trace_certificate"] is None


def test_structural_route_probe_starts_from_unit_seed() -> None:
    result = run_probe(
        "1",
        "--target-value",
        "2",
        "--max-depth",
        "1",
        "--json",
    )

    payload = json.loads(result.stdout)

    assert payload["found"] is True
    assert payload["source_n"] == 1
    assert payload["selected_path"]["values"] == [1, 2]
    assert payload["selected_path"]["labels"] == ["NEW(parent_address=[],q=2)"]
    assert payload["trace_certificate"]["valid"] is True
    assert payload["trace_certificate"]["reason"] == "trace-replayed"
