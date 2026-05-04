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


def test_classic_handoff_route_follows_drop_branch_to_boundary_entry() -> None:
    output = run_tool(3027009081)

    assert "PET CLASSIC HANDOFF ROUTE" in output
    assert "proposal_transition = DROP" in output
    assert "proposal_transition_side = DROP" in output
    assert "proposal_status = strong" in output
    assert "proposal_selected_backbone_order = " in output
    assert "proposal_race_shape_diagnostic = " in output
    assert "proposal_selected_operator_sequence = " in output
    assert "classic_probe_policy = existing-route-fallback" in output
    assert "route_status = available" in output
    assert "route_kind = fork-follow-rescan" in output
    assert "route_branch = DROP" in output
    assert "source_branch = DROP-side" in output
    assert "next_move = NEW" in output
    assert "next_kind = boundary-entry" in output
    assert "source_window = k[1..1]" in output
    assert "target_edge_hint = 1" in output
    assert "recommended_next_lens = rescan-branch-window" in output
    assert "--move NEW --kind boundary-entry" in output
    assert "claim = PET classic handoff route only; classic verification required" in output


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
    assert module.classic_probe_policy("complex-border") == "existing-route-fallback"
    assert module.classic_probe_policy("unknown") == "existing-route-fallback"
