from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import _run_generic_exponent_profile_solver


THREE_SUPPORT = 1000000007 * 1000000009 * 1000000021
FOUR_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033
FIVE_SUPPORT = 1000000007 * 1000000009 * 1000000021 * 1000000033 * 1000000087


def test_generic_exponent_backend_builds_squarefree_k3(tmp_path: Path) -> None:
    report = _run_generic_exponent_profile_solver(
        THREE_SUPPORT,
        tmp_path / "out-k3",
        exponent_profile=[1, 1, 1],
        radius=16,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1]


def test_generic_exponent_backend_builds_squarefree_k4(tmp_path: Path) -> None:
    report = _run_generic_exponent_profile_solver(
        FOUR_SUPPORT,
        tmp_path / "out-k4",
        exponent_profile=[1, 1, 1, 1],
        radius=16,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1, 1]


def test_generic_exponent_backend_builds_squarefree_k5(tmp_path: Path) -> None:
    report = _run_generic_exponent_profile_solver(
        FIVE_SUPPORT,
        tmp_path / "out-k5",
        exponent_profile=[1, 1, 1, 1, 1],
        radius=64,
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1, 1, 1]
