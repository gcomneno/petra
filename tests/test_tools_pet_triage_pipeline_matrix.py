from __future__ import annotations

import subprocess


def run_pipeline(n: int) -> str:
    return run_pipeline_with_args(str(n))


def run_pipeline_with_args(n: str, *args: str) -> str:
    result = subprocess.run(
        [
            "bash",
            "tools/pet_triage_pipeline.sh",
            n,
            *args,
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
            "balanced-flat-border-lens-drop-classic-probe",
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
        if expected_diagnostic == "complex-border":
            assert "proposal_composite_border_hint = balanced-flat-border" in output

        assert f"suggested_command = {expected_command}" in output

        assert "route_kind = fork-follow-rescan" not in output


def test_pet_triage_pipeline_passes_active_blade_window_options() -> None:
    n = "387456687301039324825975283416"

    output = run_pipeline_with_args(
        n,
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
    )

    assert "operator_depth = 0" in output
    assert "blade_window = active" in output
    assert "active_blade_start = 4" in output
    assert "active_blade_end = 32" in output
    assert "proposal_operator_depth = 0" in output
    assert "proposal_blade_window = active" in output
    assert "route_kind = complex-border-lens-drop-classic-probe" in output
    assert (
        "suggested_command = python -m pet.cli opaque-probe "
        "387456687301039324825975283416 --trial-limit 20"
    ) in output

def test_pet_triage_pipeline_route_only_skips_classic_and_legacy_sections() -> None:
    output = run_pipeline_with_args(
        "10000030000091",
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
        "--route-only",
    )

    assert "0. PET decimal boundary preflight" in output
    assert "0. PET race diagnostic" in output
    assert "1. PET classic handoff policy" in output
    assert "route_kind = balanced-flat-border-lens-drop-classic-probe" in output
    assert "decimal_rigid_border_hint" in output

    assert "2. PET verified divisor summary" not in output
    assert "3. PET classic scan policy" not in output
    assert "4. Legacy lens hint" not in output
    assert "5. Legacy lens candidates" not in output
    assert "6. Legacy lens transition" not in output
    assert "7. Legacy mass response" not in output
    assert "8. Legacy focused peel classic handoff diagnostic" not in output
    assert "9. Legacy focused peel fork diagnostic" not in output
    assert "10. Legacy fork-follow diagnostic" not in output
    assert "11. Legacy recursive lens diagnostic" not in output


def test_pet_triage_pipeline_skips_legacy_diagnostics_by_default() -> None:
    output = run_pipeline_with_args(
        "55",
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
    )

    assert "0. PET race diagnostic" in output
    assert "1. PET classic handoff policy" in output
    assert "2. PET verified divisor summary" in output
    assert "3. PET classic scan policy" in output

    assert "4. Legacy lens hint" not in output
    assert "5. Legacy lens candidates" not in output
    assert "6. Legacy lens transition" not in output
    assert "7. Legacy mass response" not in output
    assert "8. Legacy focused peel classic handoff diagnostic" not in output


def test_pet_triage_pipeline_legacy_diagnostics_are_opt_in() -> None:
    output = run_pipeline_with_args(
        "55",
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
        "--legacy-diagnostics",
    )

    assert "4. Legacy lens hint" in output
    assert "5. Legacy lens candidates" in output
    assert "6. Legacy lens transition" in output
    assert "7. Legacy mass response" in output
    assert "8. Legacy focused peel classic handoff diagnostic" in output

def test_pet_triage_pipeline_rigid_border_guard_stops_before_race() -> None:
    output = run_pipeline_with_args(
        "9999999999000000000119",
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
        "--route-only",
        "--rigid-border-guard",
    )

    assert "0. PET decimal boundary preflight" in output
    assert "9999999999000000000119" in output
    assert "decimal_rigid_border_hint" in output
    assert "preflight_guard_status = stopped" in output
    assert "preflight_guard_kind = decimal-rigid-border" in output
    assert "reason = decimal rigid border detected; skipping PET race diagnostic" in output
    assert (
        "preflight_guard_suggested_next = use shallow decimal-rigid route or rerun "
        "without --rigid-border-guard to force PET race"
    ) in output

    assert "0. PET race diagnostic" not in output
    assert "1. PET classic handoff policy" not in output

def test_pet_triage_pipeline_decimal_rigid_shallow_route_skips_race() -> None:
    output = run_pipeline_with_args(
        "9999999999000000000119",
        "--operator-depth",
        "0",
        "--blade-window",
        "active",
        "--route-only",
        "--decimal-rigid-shallow-route",
    )

    assert "0. PET decimal boundary preflight" in output
    assert "9999999999000000000119" in output
    assert "decimal_rigid_border_hint" in output
    assert "shallow_route_status = available" in output
    assert "shallow_route_kind = decimal-rigid-border-shallow-classic-probe" in output
    assert (
        "reason = decimal rigid border detected; using conservative shallow route "
        "without PET race diagnostic"
    ) in output
    assert (
        "suggested_command = python -m pet.cli opaque-probe "
        "9999999999000000000119 --trial-limit 20"
    ) in output

    assert "0. PET race diagnostic" not in output
    assert "1. PET classic handoff policy" not in output

