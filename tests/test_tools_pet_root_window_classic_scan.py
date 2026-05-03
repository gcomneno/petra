from __future__ import annotations

import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_root_window_classic_scan.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_root_window_classic_scan_finds_verified_divisor() -> None:
    output = run_tool(9081007063)

    assert "PET ROOT-WINDOW CLASSIC SCAN" in output
    assert "N = 9081007063" in output
    assert "source = PET decoded-center lens" in output
    assert "move = DROP" in output
    assert "suggested_window = k[5..7]" in output
    assert "radius = 500" in output
    assert "k = 5" in output
    assert "center = 98" in output
    assert "candidate_hit = 277" in output
    assert "divisor_found = 277" in output
    assert "cofactor = 32783419" in output
    assert "matched_k = 5,6,7" in output
    assert "verified = yes" in output
    assert "verified_hit_count = 1" in output
    assert "claim = PET-guided root-window classic scan only; divisors are accepted only when verified" in output


def test_root_window_classic_scan_supports_radius_digits_policy() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_root_window_classic_scan.py",
            "6345405191",
            "--radius-digits",
            "5",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    output = result.stdout

    assert "radius_policy = decimal-digits" in output
    assert "radius_digits = 5" in output
    assert "radius = 100000" in output
    assert "divisor_found = 70139" in output
    assert "cofactor = 90469" in output
    assert "divisor_found = 90469" in output
    assert "cofactor = 70139" in output
    assert "matched_k = 5,6,7" in output
    assert "verified_hit_count = 2" in output
