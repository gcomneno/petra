from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import _run_generic_exponent_profile_solver


SQUARE_TIMES_PRIME = (1000000007 * 1000000007) * 1000000009
PRIME_CUBE = 1000000007 * 1000000007 * 1000000007


def test_generic_exponent_profile_lane_builds_21(tmp_path: Path) -> None:
    report = _run_generic_exponent_profile_solver(
        SQUARE_TIMES_PRIME,
        tmp_path / "out-21",
        exponent_profile=[2, 1],
        radius=1,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["support_size"] == 2
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [2, 1]


def test_generic_exponent_profile_lane_respects_budget_and_returns_none(tmp_path: Path) -> None:
    report = _run_generic_exponent_profile_solver(
        SQUARE_TIMES_PRIME,
        tmp_path / "out-budget",
        exponent_profile=[2, 1],
        radius=1,
        max_k=2,
        max_radius=1,
        max_prime_count=2,
        max_combinations=1,
        max_assignments=1,
    )
    assert report is None


def test_generic_exponent_profile_lane_does_not_fake_prime_cube_as_21(tmp_path: Path) -> None:
    report = _run_generic_exponent_profile_solver(
        PRIME_CUBE,
        tmp_path / "out-cube",
        exponent_profile=[2, 1],
        radius=1,
    )
    assert report is None
