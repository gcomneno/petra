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
