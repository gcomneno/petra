import json
from pathlib import Path

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    run_residual_state_frontier_until_quiescence_with_policy,
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


def test_run_residual_state_frontier_until_quiescence_with_policy_refines_then_promotes():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = run_residual_state_frontier_until_quiescence_with_policy(
        [state], 5, _seed_b_with_113
    )

    assert result["steps_run"] == 2
    assert result["frontier"] == []
    assert result["frontier_summary"] == {
        "total": 0,
        "open": 0,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["stopped"] == []
    assert result["idle"] == []
    assert result["trace"] == [
        {"step": 1, "action": "refine"},
        {"step": 2, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"
    assert result["promoted"] == [
        {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [101]},
                {"slot": "b", "candidates": [113]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        }
    ]


def test_run_residual_state_frontier_until_quiescence_with_policy_still_quiesces_without_progress():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = run_residual_state_frontier_until_quiescence_with_policy(
        [state], 5, lambda s: None
    )

    assert result["steps_run"] == 1
    assert len(result["frontier"]) == 1
    assert result["frontier_summary"] == {
        "total": 1,
        "open": 1,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["promoted"] == []
    assert result["stopped"] == []
    assert len(result["idle"]) == 1
    assert result["trace"] == [
        {"step": 1, "action": "idle"},
    ]
    assert result["termination_reason"] == "quiescent-idle-frontier"
