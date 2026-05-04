from __future__ import annotations

import subprocess
import sys


def run_race(n: int, orders: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_backbone_race.py",
            str(n),
            "--operator-depth",
            "auto",
            "--orders",
            orders,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_backbone_race_selects_lower_cost_candidate_for_large_diagonal() -> None:
    output = run_race(9999999999, "5,7,10")

    assert "PET BACKBONE RACE PROTOTYPE" in output
    assert "N = 9999999999" in output
    assert "n_digits = 10" in output
    assert "candidate_orders = 5,7,10" in output

    assert "candidate_order = 5; shape_fit = backbone-underestimates; result = matched; move_count = 1; sequence = INC (0,)" in output
    assert "candidate_order = 7; shape_fit = backbone-overestimates; result = matched; move_count = 3; sequence = DROP root -> DROP root -> INC (0,)" in output
    assert "candidate_order = 10; shape_fit = backbone-overestimates; result = matched; move_count = 6; sequence = DROP root -> DROP root -> DROP root -> DROP root -> DROP root -> INC (0,)" in output

    assert "selected_backbone_order = 5" in output
    assert "selected_result = matched" in output
    assert "selected_move_count = 1" in output
    assert "selected_sequence = INC (0,)" in output
    assert "selection_quality = one-move" in output
    assert "claim = PET backbone race prototype only; this does not factor N" in output


def test_backbone_race_reports_exact_shape_quality() -> None:
    output = run_race(2222222222, "4,5,10")

    assert "selected_backbone_order = 5" in output
    assert "selected_move_count = 0" in output
    assert "selected_sequence = none" in output
    assert "selection_quality = exact-shape" in output


def test_backbone_race_selects_narrow_backbone_for_deep_power_shape() -> None:
    output = run_race(65536, "1,3,5")

    assert "PET BACKBONE RACE PROTOTYPE" in output
    assert "N = 65536" in output
    assert "n_digits = 5" in output
    assert "candidate_orders = 1,3,5" in output

    assert "selected_backbone_order = 1" in output
    assert "selected_result = matched" in output
    assert "selected_move_count = 3" in output
    assert "selected_sequence = INC (0,) -> INC (0, 0) -> INC (0, 0, 0)" in output
    assert "selection_quality = multi-move" in output
    assert "claim = PET backbone race prototype only; this does not factor N" in output


def test_backbone_race_default_orders_include_wide_mixed_shape() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_backbone_race.py",
            "30030",
            "--operator-depth",
            "auto",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    output = result.stdout

    assert "N = 30030" in output
    assert "n_digits = 5" in output
    assert "candidate_orders = 1,2,3,4,5,6,7" in output
    assert "selected_backbone_order = 6" in output
    assert "selected_result = already-matching" in output
    assert "selected_move_count = 0" in output
    assert "selected_sequence = none" in output
    assert "selection_quality = exact-shape" in output
