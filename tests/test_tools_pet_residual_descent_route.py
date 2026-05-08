from __future__ import annotations

import subprocess
import sys


def run_residual_descent(n: int, *args: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_residual_descent_route.py",
            str(n),
            *args,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_residual_descent_selects_anchor_by_pet_residual_shape() -> None:
    output = run_residual_descent(24680, "--max-depth", "4")

    assert "PET RESIDUAL DESCENT ROUTE" in output
    assert "depth_0_input = 24680" in output

    assert "depth_0_anchor_candidate_1 = 2" in output
    assert "depth_0_anchor_candidate_1_residual = 12340" in output
    assert "depth_0_anchor_candidate_1_residual_signature = [[], [], [[]]]" in output

    assert "depth_0_anchor_candidate_2 = 10" in output
    assert "depth_0_anchor_candidate_2_residual = 2468" in output
    assert "depth_0_anchor_candidate_2_residual_signature = [[], [[]]]" in output

    assert "depth_0_anchor_candidate_3 = 20" in output
    assert "depth_0_anchor_candidate_3_residual = 1234" in output
    assert "depth_0_anchor_candidate_3_residual_signature = [[], []]" in output

    assert "depth_0_selected_anchor_factor = 20" in output
    assert "depth_0_selected_anchor_reason = best-pet-residual-shape-descent" in output
    assert "depth_0_anchor_selection_policy = best-pet-residual-shape-descent" in output
    assert "depth_0_residual = 1234" in output

    assert "depth_1_input = 1234" in output
    assert "depth_1_anchor_factor = 2" in output
    assert "depth_1_residual = 617" in output

    assert "depth_2_input = 617" in output
    assert "depth_2_status = stopped-at-leaf" in output
    assert "depth_2_anchor_factor = -" in output
    assert "depth_2_residual = -" in output

    assert "residual_descent_status = stopped-at-leaf" in output
    assert "residual_reduction_chain = 20 * 2 * 617" in output
    assert "terminal_residual = 617" in output
    assert "terminal residual is not automatically prime" in output


def test_residual_descent_rejects_negative_depth() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_residual_descent_route.py",
            "24680",
            "--max-depth",
            "-1",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "--max-depth must be >= 0" in result.stderr
