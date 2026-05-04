from __future__ import annotations

import subprocess


def run_pipeline(n: int) -> str:
    result = subprocess.run(
        [
            "bash",
            "tools/pet_triage_pipeline.sh",
            str(n),
            "--no-fork",
            "--no-fork-follow",
            "--no-recursive",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_pet_triage_pipeline_matrix_reports_expected_routes() -> None:
    cases = [
        (
            10007,
            "atomic-exact",
            "primality-check-only",
            "available",
            "primality-check-only",
            "python -m pet.cli opaque-probe 10007 --trial-limit 2",
        ),
        (
            65536,
            "narrow-deep",
            "power-like-local-check",
            "available",
            "power-like-local-check",
            "python -m pet.cli opaque-probe 65536 --trial-limit 2",
        ),
        (
            30030,
            "wide-exact",
            "backbone-wide-structural-check",
            "available",
            "backbone-wide-structural-check",
            "python -m pet.cli opaque-probe 30030 --trial-limit 6",
        ),
        (
            9999999999,
            "near-shape",
            "operator-neighborhood-check",
            "available",
            "operator-neighborhood-check",
            "python -m pet.cli opaque-probe 9999999999 --trial-limit 5",
        ),
        (
            3027009081,
            "complex-border",
            "complex-border-route-needed",
            "available",
            "complex-border-lens-drop-classic-probe",
            "python -m pet.cli opaque-probe 3027009081 --trial-limit 20",
        ),
    ]

    for (
        n,
        expected_diagnostic,
        expected_policy,
        expected_status,
        expected_route_kind,
        expected_command,
    ) in cases:
        output = run_pipeline(n)

        assert "PET TRIAGE PIPELINE" in output
        assert "0. PET race diagnostic" in output
        assert "1. PET classic handoff policy" in output

        assert f"race_shape_diagnostic = {expected_diagnostic}" in output
        assert f"classic_probe_policy = {expected_policy}" in output
        assert f"route_status = {expected_status}" in output
        assert f"route_kind = {expected_route_kind}" in output

        assert f"suggested_command = {expected_command}" in output

        assert "route_kind = fork-follow-rescan" not in output
