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
    assert "claim = PET backbone race prototype only; this does not factor N" in output
