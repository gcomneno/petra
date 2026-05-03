from __future__ import annotations

import subprocess
import sys


def run_tool(n: int) -> str:
    result = subprocess.run(
        [sys.executable, "tools/pet_local_probe_proposal.py", str(n)],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout


def test_local_probe_proposal_selects_drop_multi_threshold_band() -> None:
    output = run_tool(3027009081)

    assert "PET LOCAL PROBE PROPOSAL" in output
    assert "transition = DROP" in output
    assert "source_generator = 30" in output
    assert "target_generator = 6" in output
    assert "representative_target = 15" in output
    assert "primary_band = multi-threshold NEW,DROP k[2..6]" in output
    assert "transition_side = DROP" in output
    assert "proposal_status = strong" in output
    assert "reason = transition-coherent magnetic band selected" in output
    assert "candidate_window = k[2..6]" in output
    assert "side_band = recovery DROP k[7..11]" in output
    assert "side_window = k[7..11]" in output
    assert "claim = PET local probe proposal only; this does not factor N" in output


def test_local_probe_proposal_marks_unknown_transition_as_weak() -> None:
    output = run_tool(49)

    assert "transition = unknown" in output
    assert "source_generator = 4" in output
    assert "target_generator = 2" in output
    assert "representative_target = unknown" in output
    assert "transition_side = fallback" in output
    assert "proposal_status = weak" in output
    assert "reason = no direct PET lens transition available" in output
    assert "suggested_probe_role = inspect unresolved transition neighborhood" in output
    assert "side_band = unknown" in output
    assert "side_window = unknown" in output
    assert "claim = PET local probe proposal only; this does not factor N" in output
