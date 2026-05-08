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
    assert "depth_2_status = complete-prime-leaf" in output
    assert "depth_2_anchor_factor = -" in output
    assert "depth_2_residual = 1" in output

    assert "residual_descent_status = complete" in output
    assert "residual_reduction_chain = 20 * 2 * 617" in output
    assert "terminal_residual = 1" in output
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


def test_residual_descent_can_use_auto_flat_k_scan() -> None:
    output = run_residual_descent(
        1001,
        "--max-depth",
        "4",
        "--auto-flat-k-scan",
        "--flat-k-prime-limit",
        "20",
        "--flat-k-max-supports",
        "5000",
        "--flat-k-max-factor-lines",
        "10",
    )

    assert "depth_0_input = 1001" in output
    assert "depth_0_route_escalation_policy = flat-k-support-scan" in output
    assert "depth_0_route_execution_status = flat-k-scan-running" in output
    assert "depth_0_route_final_status = partial-factorization-by-flat-k-scan" in output
    assert "depth_0_anchor_candidate_" in output
    assert "depth_0_selected_anchor_reason = best-pet-residual-shape-descent" in output
    assert "residual_reduction_chain =" in output
    assert "terminal_residual =" in output
