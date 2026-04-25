from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import (
    _run_generic_exponent_profile_solver,
    _run_generic_squarefree_profile_solver,
)


THREE_SUPPORT = 1000000007 * 1000000009 * 1000000021


def test_squarefree_backend_matches_generic_exponent_backend(tmp_path: Path) -> None:
    generic_exp = _run_generic_exponent_profile_solver(
        THREE_SUPPORT,
        tmp_path / "out-exp",
        exponent_profile=[1, 1, 1],
        radius=16,
    )
    generic_sq = _run_generic_squarefree_profile_solver(
        THREE_SUPPORT,
        tmp_path / "out-sq",
        support_size=3,
        radius=16,
    )

    assert generic_exp is not None
    assert generic_sq is not None
    assert generic_exp["terminal_state"]["status"] == "built"
    assert generic_sq["terminal_state"]["status"] == "built"
    assert generic_exp["terminal_state"]["constraints"] == generic_sq["terminal_state"]["constraints"]
    assert generic_exp["irsr_final_status"] == generic_sq["irsr_final_status"]
