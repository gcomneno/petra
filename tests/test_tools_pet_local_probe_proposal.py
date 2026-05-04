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
    assert "target_role = reduction/probe target, not full N mass" in output
    assert "representative_target = 15" in output
    assert "Lens mass/shadow" in output
    assert "mass_source_generator = 30" in output
    assert "primorial_expanded_generator = " in output
    assert "digit_aligned = " in output
    assert "weight_alignment = " in output
    assert "weight_direction = " in output
    assert "digit_repetition_ratio = " in output
    assert "shadow_note = " in output
    assert "primary_band = multi-threshold NEW,DROP k[2..6]" in output
    assert "transition_side = DROP" in output
    assert "proposal_status = strong" in output
    assert "proposal_status_kind = structural" in output
    assert "verification_status = unverified" in output
    assert "reason = transition-coherent magnetic band selected" in output
    assert "candidate_status = window-only" in output
    assert "candidate_window = k[2..6]" in output
    assert "side_band = recovery DROP k[7..11]" in output
    assert "side_window = k[7..11]" in output
    assert "claim = PET local probe proposal only; this does not factor N" in output


def test_local_probe_proposal_handles_dec_transition() -> None:
    output = run_tool(49)

    assert "transition = DEC" in output
    assert "source_generator = 4" in output
    assert "target_generator = 2" in output
    assert "representative_target = 2" in output
    assert "primary_band = recovery DROP k[2..6]" in output
    assert "transition_side = DEC-as-DROP" in output
    assert "proposal_status = partial" in output
    assert "reason = exponent transition mapped to DROP-like release band" in output
    assert "suggested_probe_role = inspect DEC exponent release through DROP-like band" in output
    assert "candidate_window = k[2..6]" in output
    assert "side_band = unknown" in output
    assert "side_window = unknown" in output
    assert "claim = PET local probe proposal only; this does not factor N" in output


def test_local_probe_proposal_handles_dec_path_transition() -> None:
    output = run_tool(16)

    assert "transition = DEC_PATH" in output
    assert "source_generator = 16" in output
    assert "target_generator = 2" in output
    assert "representative_target = 2" in output
    assert "primary_band = recovery DROP k[2..6]" in output
    assert "transition_side = DEC_PATH-as-DROP" in output
    assert "proposal_status = partial" in output
    assert "reason = exponent transition path mapped to DROP-like release band" in output
    assert "suggested_probe_role = inspect DEC exponent path through DROP-like band" in output
    assert "candidate_window = k[2..6]" in output
    assert "side_band = unknown" in output
    assert "side_window = unknown" in output
    assert "claim = PET local probe proposal only; this does not factor N" in output
