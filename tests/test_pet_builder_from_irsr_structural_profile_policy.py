from __future__ import annotations

from pathlib import Path

from pet.builder_from_irsr import _run_structural_profile_policy_v0


PRIME_SQUARE = 1000000007 * 1000000007
SQUARE_TIMES_PRIME = (1000000007 * 1000000007) * 1000000009
SQUAREFREE_1111 = 1000000007 * 1000000009 * 1000000021 * 1000000033
PRIME_CUBE = 1000000007 * 1000000007 * 1000000007


def test_structural_profile_policy_builds_prime_square(tmp_path: Path) -> None:
    report = _run_structural_profile_policy_v0(
        PRIME_SQUARE,
        tmp_path / "out-square",
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [2]


def test_structural_profile_policy_builds_square_times_prime(tmp_path: Path) -> None:
    report = _run_structural_profile_policy_v0(
        SQUARE_TIMES_PRIME,
        tmp_path / "out-21",
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [2, 1]


def test_structural_profile_policy_builds_squarefree_k4(tmp_path: Path) -> None:
    report = _run_structural_profile_policy_v0(
        SQUAREFREE_1111,
        tmp_path / "out-k4",
    )
    assert report is not None
    assert report["terminal_state"]["status"] == "built"
    assert report["terminal_state"]["constraints"]["exponent_profile"] == [1, 1, 1, 1]


def test_structural_profile_policy_returns_none_outside_supported_profiles(tmp_path: Path) -> None:
    report = _run_structural_profile_policy_v0(
        PRIME_CUBE,
        tmp_path / "out-cube",
    )
    assert report is None


def test_structural_profile_policy_accepts_injected_policy(tmp_path: Path) -> None:
    policy = {
        "allowed_exponent_profiles": {
            "max_support_size": 3,
            "max_total_weight": 4,
            "radius_default": 16,
            "deferred_profiles": [],
        },
        "squarefree_support_size_range": [3, 3],
        "squarefree_radius_default": 16,
        "squarefree_radius_overrides": {},
    }

    n = 100003**2 * 100019 * 100043

    report = _run_structural_profile_policy_v0(
        n,
        tmp_path / "policy-injected",
        structural_radius=64,
        policy=policy,
    )

    assert report is not None
    assert report["builder_report"]["support_report"]["exponent_multiset"] == [2, 1, 1]
