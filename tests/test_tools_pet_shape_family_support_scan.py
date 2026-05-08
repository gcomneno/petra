from __future__ import annotations

import subprocess
import sys


def run_shape_family_scan(n: int, *args: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_shape_family_support_scan.py",
            str(n),
            *args,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_shape_family_support_scan_handles_branchy_shape() -> None:
    output = run_shape_family_scan(
        192,
        "--shape",
        "[[], [[], []]]",
        "--support-limit",
        "1000",
        "--max-supports",
        "500",
        "--max-factor-lines",
        "10",
    )

    assert "PET SHAPE-FAMILY SUPPORT SCAN" in output
    assert "shape_family_class = branchy-shape" in output
    assert "scan_status = complete" in output
    assert "support_count = 5" in output
    assert "unique_factor_hit_count = 1" in output
    assert "factor_1 = 64" in output
    assert "factor_1_first_support = 320" in output
    assert "factor_selection_policy = deferred-to-residual-descent" in output
    assert "best_factor = deferred" in output
    assert "claim = classic shape-family support scan; PET only selected the shape family" in output


def test_shape_family_support_scan_handles_mixed_depth_shape() -> None:
    output = run_shape_family_scan(
        36,
        "--shape",
        "[[[]], [[]]]",
        "--support-limit",
        "1000",
        "--max-supports",
        "500",
        "--max-factor-lines",
        "10",
    )

    assert "shape_family_class = mixed-depth" in output
    assert "scan_status = complete" in output
    assert "support_count = 20" in output
    assert "unique_factor_hit_count = 2" in output
    assert "factor_1 = 4" in output
    assert "factor_2 = 9" in output
    assert "factor_selection_policy = deferred-to-residual-descent" in output
    assert "best_factor = deferred" in output


def test_shape_family_support_scan_rejects_unsupported_family() -> None:
    output = run_shape_family_scan(
        10403,
        "--shape",
        "[[], []]",
        "--support-limit",
        "1000",
        "--max-supports",
        "500",
        "--max-factor-lines",
        "10",
    )

    assert "shape_family_class = semiprime-flat" in output
    assert "scan_status = unsupported-shape-family" in output
    assert "reason = shape family is not supported by this structural support scan" in output


def test_shape_family_support_scan_handles_one_deep_tail_shape() -> None:
    output = run_shape_family_scan(
        52,
        "--shape",
        "[[], [[]]]",
        "--support-limit",
        "1000",
        "--max-supports",
        "500",
        "--max-factor-lines",
        "10",
    )

    assert "shape_family_class = one-deep-tail" in output
    assert "scan_status = complete" in output
    assert "unique_factor_hit_count = 4" in output
    assert "factor_selection_policy = deferred-to-residual-descent" in output
    assert "best_factor = deferred" in output

