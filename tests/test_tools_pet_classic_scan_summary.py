from __future__ import annotations

import json
import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_classic_scan_summary.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_classic_scan_summary_reports_structural_divisor_roles() -> None:
    output = run_tool(3027009081)

    assert "PET CLASSIC SCAN SUMMARY" in output
    assert "N = 3027009081" in output

    assert "verified_divisor = 3" in output
    assert "cofactor = 1009003027" in output
    assert "role_hint = single-leaf divisor" in output

    assert "verified_divisor = 1009" in output
    assert "cofactor = 3000009" in output

    assert "verified_divisor = 3027" in output
    assert "cofactor = 1000003" in output
    assert "divisor_generator = 6" in output
    assert "cofactor_generator = 2" in output
    assert "role_hint = composite-block isolates single-leaf cofactor" in output

    assert "verified_divisor_count = 3" in output
    assert "claim = PET-guided classic scan summary only; divisors are accepted only when verified" in output


def test_classic_scan_summary_tolerates_unavailable_sources() -> None:
    output = run_tool(49)

    assert "PET CLASSIC SCAN SUMMARY" in output
    assert "N = 49" in output
    assert "source_status crumb = unavailable" in output
    assert "source_reason crumb = ERROR: opaque-focused-peel found no matching magnetic bands" in output
    assert "verified_divisor = 7" in output
    assert "cofactor = 7" in output
    assert "sources = root-window-digits:5:exhaustive-like,root-window-fixed:500" in output
    assert "divisor_generator = 2" in output
    assert "cofactor_generator = 2" in output
    assert "role_hint = prime-like split" in output
    assert "verified_divisor_count = 1" in output


def test_classic_scan_summary_preserves_crumb_source_for_first_step_divisor() -> None:
    output = run_tool(3027009081)

    divisor_block = output.split("verified_divisor = 3", maxsplit=1)[1]
    divisor_block = divisor_block.split("verified_divisor = 1009", maxsplit=1)[0]

    assert "cofactor = 1009003027" in divisor_block
    assert "sources = crumb,root-window-digits:5:exhaustive-like,root-window-fixed:500" in divisor_block


def test_classic_scan_summary_supports_json_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_classic_scan_summary.py",
            "3027009081",
            "--json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)

    assert payload["n"] == 3027009081
    assert payload["fixed_radius"] == 500
    assert payload["radius_digits"] == 5
    assert payload["root_window_digit_scope"] == "exhaustive-like"
    assert payload["source_errors"] == {}
    assert payload["verified_divisor_count"] == 3
    assert payload["verified_divisors"][0] == {
        "divisor": 3,
        "cofactor": 1009003027,
        "sources": [
            "crumb",
            "root-window-digits:5:exhaustive-like",
            "root-window-fixed:500",
        ],
        "divisor_generator": "2",
        "cofactor_generator": "6",
        "role_hint": "single-leaf divisor",
        "verified": True,
    }
    assert (
        payload["claim"]
        == "PET-guided classic scan summary only; divisors are accepted only when verified"
    )


def test_classic_scan_summary_json_reports_unavailable_sources() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_classic_scan_summary.py",
            "49",
            "--json",
        ],
        check=True,
        text=True,
        capture_output=True,
    )

    payload = json.loads(result.stdout)

    assert payload["n"] == 49
    assert payload["root_window_digit_scope"] == "exhaustive-like"
    assert payload["source_errors"] == {
        "crumb": "ERROR: opaque-focused-peel found no matching magnetic bands"
    }
    assert payload["verified_divisor_count"] == 1
    assert payload["verified_divisors"] == [
        {
            "divisor": 7,
            "cofactor": 7,
            "sources": [
                "root-window-digits:5:exhaustive-like",
                "root-window-fixed:500",
            ],
            "divisor_generator": "2",
            "cofactor_generator": "2",
            "role_hint": "prime-like split",
            "verified": True,
        }
    ]
