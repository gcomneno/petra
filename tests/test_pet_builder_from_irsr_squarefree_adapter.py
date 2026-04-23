from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import (
    _run_generic_squarefree_profile_solver,
    _run_squarefree_k_support_solver,
)


THREE_SUPPORT = 1000000007 * 1000000009 * 1000000021


def test_squarefree_legacy_wrapper_matches_generic_backend(tmp_path: Path) -> None:
    generic = _run_generic_squarefree_profile_solver(
        THREE_SUPPORT,
        tmp_path / "out-generic",
        support_size=3,
        radius=16,
    )
    legacy = _run_squarefree_k_support_solver(
        THREE_SUPPORT,
        tmp_path / "out-legacy",
        k=3,
        radius=16,
    )

    assert generic is not None
    assert legacy is not None
    assert generic["terminal_state"]["status"] == "built"
    assert legacy["terminal_state"]["status"] == "built"
    assert generic["terminal_state"]["constraints"] == legacy["terminal_state"]["constraints"]
    assert generic["irsr_final_status"] == legacy["irsr_final_status"]
