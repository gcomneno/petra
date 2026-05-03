from __future__ import annotations

import json
import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_classic_scan_policy.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_classic_scan_policy_classifies_baseline_bounded_and_exhaustive_sources() -> None:
    output = run_tool(3027009081)

    assert "PET CLASSIC SCAN POLICY" in output
    assert "N = 3027009081" in output
    assert "root_window_digit_scope = exhaustive-like" in output

    assert "source = crumb" in output
    assert "source_kind = baseline" in output
    assert "reason = first-step classic fallback" in output

    assert "source = root-window-fixed:500" in output
    assert "source_kind = bounded-window" in output
    assert "reason = bounded root-window classic scan" in output

    assert "source = root-window-digits:5:exhaustive-like" in output
    assert "source_kind = exhaustive-like" in output
    assert "reason = digit radius reaches exhaustive-like low-side coverage" in output

    assert "usable_sources = crumb,root-window-fixed:500" in output
    assert "caution_sources = root-window-digits:5:exhaustive-like" in output
    assert "unavailable_sources = none" in output
    assert "verified_divisor_count = 3" in output
    assert (
        "claim = PET classic scan policy only; it classifies scan sources and does not verify new divisors"
        in output
    )


def test_classic_scan_policy_json_reports_unavailable_sources() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_classic_scan_policy.py",
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
    assert payload["usable_sources"] == ["root-window-fixed:500"]
    assert payload["caution_sources"] == ["root-window-digits:5:exhaustive-like"]
    assert payload["unavailable_sources"] == ["crumb"]
    assert payload["verified_divisor_count"] == 1
    assert payload["source_policies"] == [
        {
            "source": "crumb",
            "status": "unavailable",
            "source_kind": "unavailable",
            "usable": False,
            "reason": "ERROR: opaque-focused-peel found no matching magnetic bands",
        },
        {
            "source": "root-window-digits:5:exhaustive-like",
            "status": "available",
            "source_kind": "exhaustive-like",
            "usable": False,
            "reason": "digit radius reaches exhaustive-like low-side coverage",
        },
        {
            "source": "root-window-fixed:500",
            "status": "available",
            "source_kind": "bounded-window",
            "usable": True,
            "reason": "bounded root-window classic scan",
        },
    ]
    assert (
        payload["claim"]
        == "PET classic scan policy only; it classifies scan sources and does not verify new divisors"
    )
