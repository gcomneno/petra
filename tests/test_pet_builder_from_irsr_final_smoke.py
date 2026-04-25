from pathlib import Path

from pet.builder_from_irsr import _run_structural_profile_policy_v0


def test_final_smoke_structural_policy_builds_supported_profiles(tmp_path: Path) -> None:
    cases = [
        (101**2, "prime-square"),
        (101**2 * 103, "square-times-prime"),
        (101 * 103 * 107 * 109, "squarefree-k4"),
    ]

    for n, name in cases:
        report = _run_structural_profile_policy_v0(
            n,
            tmp_path / name,
        )

        assert report is not None, name
        assert report["builder_report"] is not None


def test_final_smoke_structural_policy_returns_none_outside_supported_profiles(
    tmp_path: Path,
) -> None:
    report = _run_structural_profile_policy_v0(
        101**3,
        tmp_path / "outside-profile",
    )

    assert report is None
