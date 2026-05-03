from __future__ import annotations

import json
import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_crumb_classic_scan.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_crumb_classic_scan_finds_first_step_divisor() -> None:
    output = run_tool(3027009081)

    assert "PET CRUMB CLASSIC SCAN" in output
    assert "N = 3027009081" in output
    assert "source = boundary-entry NEW" in output
    assert "selected_band = boundary-entry NEW k[1..1]" in output
    assert "edge_k = 1" in output
    assert "center = 3027009081" in output
    assert "method = classic-small-n-trial-division" in output
    assert "recommended = yes" in output
    assert "divisor_found = 3" in output
    assert "cofactor = 1009003027" in output
    assert "verified = yes" in output
    assert "claim = PET-guided crumb classic scan only; divisors are accepted only when verified" in output


def test_crumb_classic_scan_supports_json_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_crumb_classic_scan.py",
            "3027009081",
            "--json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)

    assert payload["n"] == 3027009081
    assert payload["source"] == "boundary-entry NEW"
    assert payload["selected_band"] == {
        "kind": "boundary-entry",
        "move": "NEW",
        "k_range": "1..1",
    }
    assert payload["edge_k"] == 1
    assert payload["center"] == 3027009081
    assert payload["method"] == "classic-small-n-trial-division"
    assert payload["recommended"] is True
    assert payload["divisor_found"] == 3
    assert payload["cofactor"] == 1009003027
    assert payload["verified"] is True
    assert (
        payload["claim"]
        == "PET-guided crumb classic scan only; divisors are accepted only when verified"
    )
