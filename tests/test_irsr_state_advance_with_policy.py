import json
from pathlib import Path

from pet.irsr_state import (
    advance_residual_state_once_with_policy,
    refine_residual_state_slot_candidates,
    try_seed_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def _seed_b_with_113(state: dict):
    return try_seed_residual_state_slot_candidates(state, "b", [113])


def test_advance_residual_state_once_with_policy_refines_open_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = advance_residual_state_once_with_policy(state, _seed_b_with_113)

    assert result["action"] == "refine"
    assert result["state"]["slots"][0]["domain"]["candidates"] == [101]
    assert result["state"]["slots"][1]["domain"]["candidates"] == [113]
    assert result["state"]["refinement"]["iteration"] == 2
    assert result["state"]["refinement"]["status"] == "payload-ready"
    assert result["state"]["refinement"]["payload_ready"] is True


def test_advance_residual_state_once_with_policy_falls_back_to_idle_when_policy_does_nothing():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = advance_residual_state_once_with_policy(state, lambda s: None)

    assert result == {
        "action": "idle",
        "reason": "open-without-branching-policy",
    }
