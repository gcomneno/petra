from __future__ import annotations

import subprocess
import sys


def run_flat_k_scan(n: int, *args: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_flat_k_support_scan.py",
            str(n),
            *args,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_flat_k_support_scan_handles_flat_two_leaf_case() -> None:
    output = run_flat_k_scan(
        10403,
        "--shape",
        "[[], []]",
        "--prime-limit",
        "200",
        "--max-supports",
        "5000",
    )

    assert "PET FLAT-K SUPPORT SCAN" in output
    assert "flat_width = 2" in output
    assert "scan_status = complete" in output
    assert "unique_factor_hit_count = 2" in output
    assert "factor_1 = 101" in output
    assert "factor_2 = 103" in output
    assert "factor_selection_policy = deferred-to-residual-descent" in output
    assert "best_factor = deferred" in output
    assert "claim = classic flat-k support scan; PET only selected the shape family" in output


def test_flat_k_support_scan_bounds_wide_flat_output() -> None:
    output = run_flat_k_scan(
        30030,
        "--shape",
        "[[], [], [], [], [], []]",
        "--prime-limit",
        "20",
        "--max-supports",
        "5000",
        "--max-factor-lines",
        "25",
    )

    assert "flat_width = 6" in output
    assert "scan_status = complete" in output
    assert "unique_factor_hit_count = 62" in output
    assert "printed_factor_count = 25" in output
    assert "factor_lines_truncated = yes" in output
    assert "factor_selection_policy = deferred-to-residual-descent" in output
    assert "factor_1 = 2" in output
    assert "factor_25 = 91" in output
    assert "factor_26 =" not in output
    assert "best_factor = deferred" in output


def test_flat_k_support_scan_rejects_non_flat_shape() -> None:
    output = run_flat_k_scan(
        2468,
        "--shape",
        "[[], [[]]]",
        "--prime-limit",
        "20",
        "--max-supports",
        "100",
    )

    assert "scan_status = unsupported-shape" in output
    assert "reason = target shape is not a flat PET leaf family with width >= 2" in output
