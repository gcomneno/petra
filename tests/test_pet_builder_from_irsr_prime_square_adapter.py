from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import (
    _run_generic_exponent_profile_solver,
    _run_prime_square_solver,
)


PRIME_SQUARE = 1000000007 * 1000000007


def test_prime_square_legacy_wrapper_matches_generic_backend(tmp_path: Path) -> None:
    generic = _run_generic_exponent_profile_solver(
        PRIME_SQUARE,
        tmp_path / "out-generic",
        exponent_profile=[2],
        radius=1,
    )
    legacy = _run_prime_square_solver(
        PRIME_SQUARE,
        tmp_path / "out-legacy",
    )

    assert generic is not None
    assert legacy is not None
    assert generic["terminal_state"]["status"] == "built"
    assert legacy["terminal_state"]["status"] == "built"
    assert generic["terminal_state"]["constraints"] == legacy["terminal_state"]["constraints"]
    assert generic["irsr_final_status"] == legacy["irsr_final_status"]
