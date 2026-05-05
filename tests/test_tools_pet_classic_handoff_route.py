from __future__ import annotations

import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_classic_handoff_route.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def run_tool_with_proposal_file(n: int, proposal_file: str) -> str:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_classic_handoff_route.py",
            str(n),
            "--proposal-file",
            proposal_file,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_classic_handoff_route_reports_policy_without_legacy_fallback() -> None:
    output = run_tool(3027009081)

    assert "PET CLASSIC HANDOFF ROUTE" in output
    assert "proposal_race_shape_diagnostic = complex-border" in output
    assert "proposal_composite_border_hint = balanced-flat-border" in output
    assert "proposal_decimal_rigid_border_score = " in output
    assert "proposal_decimal_rigid_border_hint = " in output
    assert "proposal_operator_depth = auto" in output
    assert "proposal_blade_window = full" in output
    assert "classic_probe_policy = complex-border-route-needed" in output
    assert "route_status = available" in output
    assert "route_kind = balanced-flat-border-lens-drop-classic-probe" in output
    assert "reason = balanced flat PET border has a DROP lens transition; run conservative classic residual probe" in output
    assert "suggested_command = python -m pet.cli opaque-probe 3027009081 --trial-limit 20" in output
    assert "route_kind = fork-follow-rescan" not in output
    assert "claim = PET classic handoff route only; classic verification required" in output


def test_classic_handoff_route_supports_atomic_exact_primality_policy() -> None:
    output = run_tool(10007)

    assert "proposal_race_shape_diagnostic = atomic-exact" in output
    assert "classic_probe_policy = primality-check-only" in output
    assert "route_status = available" in output
    assert "route_kind = primality-check-only" in output
    assert "reason = atomic PET shape; run minimal classic residual/primality probe" in output
    assert "suggested_command = python -m pet.cli opaque-probe 10007 --trial-limit 2" in output
    assert "route_kind = fork-follow-rescan" not in output


def test_classic_handoff_route_supports_narrow_deep_power_policy() -> None:
    output = run_tool(65536)

    assert "proposal_race_shape_diagnostic = narrow-deep" in output
    assert "classic_probe_policy = power-like-local-check" in output
    assert "route_status = available" in output
    assert "route_kind = power-like-local-check" in output
    assert "reason = narrow deep PET shape; run minimal classic check for repeated small factors" in output
    assert "suggested_command = python -m pet.cli opaque-probe 65536 --trial-limit 2" in output
    assert "route_kind = fork-follow-rescan" not in output


def test_classic_handoff_route_supports_wide_exact_backbone_policy() -> None:
    output = run_tool(30030)

    assert "proposal_race_shape_diagnostic = wide-exact" in output
    assert "classic_probe_policy = backbone-wide-structural-check" in output
    assert "route_status = available" in output
    assert "route_kind = backbone-wide-structural-check" in output
    assert "reason = wide exact PET shape; run classic probe bounded by selected backbone order" in output
    assert "suggested_command = python -m pet.cli opaque-probe 30030 --trial-limit 6" in output
    assert "route_kind = fork-follow-rescan" not in output


def test_classic_handoff_route_supports_near_shape_operator_policy() -> None:
    output = run_tool(9999999999)

    assert "proposal_race_shape_diagnostic = near-shape" in output
    assert "proposal_selected_operator_sequence = INC (0,)" in output
    assert "classic_probe_policy = operator-neighborhood-check" in output
    assert "route_status = available" in output
    assert "route_kind = operator-neighborhood-check" in output
    assert "reason = near PET shape; run classic probe bounded by selected operator neighborhood" in output
    assert "suggested_command = python -m pet.cli opaque-probe 9999999999 --trial-limit 5" in output
    assert "route_kind = fork-follow-rescan" not in output


def test_classic_probe_policy_maps_pet_shape_diagnostics() -> None:
    import importlib.util
    from pathlib import Path

    module_path = Path("tools/pet_classic_handoff_route.py")
    spec = importlib.util.spec_from_file_location("pet_classic_handoff_route", module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.classic_probe_policy("atomic-exact") == "primality-check-only"
    assert module.classic_probe_policy("narrow-deep") == "power-like-local-check"
    assert module.classic_probe_policy("wide-exact") == "backbone-wide-structural-check"
    assert module.classic_probe_policy("near-shape") == "operator-neighborhood-check"
    assert module.classic_probe_policy("complex-border") == "complex-border-route-needed"
    assert module.classic_probe_policy("unknown") == "route-needed"


def test_classic_handoff_route_can_reuse_precomputed_proposal_file(tmp_path) -> None:
    proposal = subprocess.run(
        [
            sys.executable,
            "tools/pet_local_probe_proposal.py",
            "10007",
            "--operator-depth",
            "auto",
            "--backbone-selection",
            "race",
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout

    proposal_file = tmp_path / "proposal.txt"
    proposal_file.write_text(proposal, encoding="utf-8")

    output = run_tool_with_proposal_file(10007, str(proposal_file))

    assert "proposal_race_shape_diagnostic = atomic-exact" in output
    assert "classic_probe_policy = primality-check-only" in output
    assert "route_status = available" in output
    assert "route_kind = primality-check-only" in output
    assert "suggested_command = python -m pet.cli opaque-probe 10007 --trial-limit 2" in output


def test_classic_handoff_route_can_use_active_blade_window_for_large_input() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "tools/pet_classic_handoff_route.py",
            "387456687301039324825975283416",
            "--operator-depth",
            "0",
            "--blade-window",
            "active",
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    output = result.stdout

    assert "proposal_race_shape_diagnostic = complex-border" in output
    assert "proposal_operator_depth = 0" in output
    assert "proposal_blade_window = active" in output
    assert "classic_probe_policy = complex-border-route-needed" in output
    assert "route_status = available" in output
    assert "route_kind = complex-border-lens-drop-classic-probe" in output
    assert "suggested_command = python -m pet.cli opaque-probe 387456687301039324825975283416 --trial-limit 20" in output


def test_classic_handoff_route_reports_decimal_rigid_border_fields_from_proposal_file(tmp_path) -> None:
    proposal_file = tmp_path / "proposal.txt"
    proposal_file.write_text(
        "\n".join(
            [
                "selected_backbone_order = 3",
                "race_shape_diagnostic = complex-border",
                "selected_operator_sequence = none",
                "composite_border_hint = balanced-flat-border",
                "decimal_rigid_border_score = 0.311",
                "decimal_rigid_border_hint = yes",
            ]
        ),
        encoding="utf-8",
    )

    output = run_tool_with_proposal_file(100000000003900000091, str(proposal_file))

    assert "proposal_composite_border_hint = balanced-flat-border" in output
    assert "proposal_decimal_rigid_border_score = 0.311" in output
    assert "proposal_decimal_rigid_border_hint = yes" in output
    assert "classic_probe_policy = complex-border-route-needed" in output
    assert "route_status = available" in output
    assert "route_kind = balanced-flat-border-lens-drop-classic-probe" in output

