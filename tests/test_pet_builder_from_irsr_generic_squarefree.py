from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import _run_generic_squarefree_profile_solver


THREE_SUPPORT = 1000000007 * 1000000009 * 1000000021
FOUR_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033
FIVE_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033 * 1000000087
SIX_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033 * 1000000087 * 1000000093


def test_generic_squarefree_lane_builds_k3(tmp_path: Path) -> None:
    report = _run_generic_squarefree_profile_solver(
        THREE_SUPPORT,
        tmp_path / "out-k3",
        support_size=3,
        radius=16,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["support_size"] == 3
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1]


def test_generic_squarefree_lane_builds_k4(tmp_path: Path) -> None:
    report = _run_generic_squarefree_profile_solver(
        FOUR_SUPPORT,
        tmp_path / "out-k4",
        support_size=4,
        radius=16,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["support_size"] == 4
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1, 1]


def test_generic_squarefree_lane_builds_k5(tmp_path: Path) -> None:
    report = _run_generic_squarefree_profile_solver(
        FIVE_SUPPORT,
        tmp_path / "out-k5",
        support_size=5,
        radius=64,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["support_size"] == 5
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1, 1, 1]


def test_generic_squarefree_lane_respects_budget_and_returns_none(tmp_path: Path) -> None:
    report = _run_generic_squarefree_profile_solver(
        SIX_SUPPORT,
        tmp_path / "out-k6",
        support_size=6,
        radius=64,
        max_k=5,
        max_radius=64,
        max_prime_count=16,
        max_combinations=256,
    )
    assert report is None
