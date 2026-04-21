from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import _run_squarefree_k_support_solver


FIVE_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033 * 1000000087


def test_squarefree_k_support_respects_combination_budget(tmp_path: Path) -> None:
    report = _run_squarefree_k_support_solver(
        FIVE_SUPPORT,
        tmp_path / "out",
        k=5,
        radius=64,
        max_prime_count=16,
        max_combinations=1,
    )
    assert report is None
