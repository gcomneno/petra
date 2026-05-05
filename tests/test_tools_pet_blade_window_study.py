from __future__ import annotations

import csv
import subprocess
import sys


def run_tool(*args: str) -> list[dict[str, str]]:
    result = subprocess.run(
        [sys.executable, "tools/research/pet_blade_window_study.py", *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return list(csv.DictReader(result.stdout.splitlines()))


def row_for(rows: list[dict[str, str]], n: str) -> dict[str, str]:
    for row in rows:
        if row["N"] == n:
            return row
    raise AssertionError(f"missing row for {n}")


def test_blade_window_study_reports_mass_based_policy_columns() -> None:
    rows = run_tool("--preset", "known")
    row = row_for(rows, "30030")

    assert row["actual_pet_mass"] == "6"
    assert row["candidate_start_mass_minus_2"] == "4"
    assert row["candidate_start_mass_minus_2_or_deep_guard"] == "4"
    assert row["keep_from_mass_minus_2_or_deep_guard"] == "yes"

    assert row["guarded_attempts_ltr"] == "3"
    assert row["guarded_attempts_rtl"] == "2"
    assert row["fill_gt_080_direction"] == "RTL"
    assert row["fill_gt_080_attempts"] == "2"


def test_blade_window_study_keeps_deep_shapes_left_biased() -> None:
    rows = run_tool("--preset", "known")
    row = row_for(rows, "65536")

    assert row["race_shape_diagnostic"] == "narrow-deep"
    assert row["candidate_start_mass_minus_2_or_deep_guard"] == "1"
    assert row["keep_from_mass_minus_2_or_deep_guard"] == "yes"

    assert row["fill_gt_080_direction"] == "LTR"
    assert row["fill_gt_080_attempts"] == "1"


def test_blade_window_study_palindrome_preset_is_available() -> None:
    rows = run_tool("--preset", "palindromes", "--operator-depth", "auto")
    row = row_for(rows, "1001")

    assert row["digits"] == "4"
    assert row["race_shape_diagnostic"] == "complex-border"
    assert row["composite_border_hint"] == "balanced-flat-border"
