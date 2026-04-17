import json
from pathlib import Path

from pet.irsr_state import (
    advance_residual_state_frontier_n_steps,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_advance_residual_state_frontier_n_steps_keeps_empty_frontier_empty():
    result = advance_residual_state_frontier_n_steps([], 3)

    assert result == {
        "steps_run": 0,
        "frontier": [],
        "promoted": [],
        "stopped": [],
        "idle": [],
    }


def test_advance_residual_state_frontier_n_steps_accumulates_promoted_payloads():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    result = advance_residual_state_frontier_n_steps([state], 1)

    assert result["steps_run"] == 1
    assert result["frontier"] == []
    assert result["stopped"] == []
    assert result["idle"] == []
    assert result["promoted"] == [
        {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [101, 103]},
                {"slot": "b", "candidates": [113]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        }
    ]


def test_advance_residual_state_frontier_n_steps_promotes_ready_state_before_branching():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    result = advance_residual_state_frontier_n_steps([state], 3)

    assert result["steps_run"] == 1
    assert result["frontier"] == []
    assert result["stopped"] == []
    assert result["idle"] == []
    assert result["promoted"] == [
        {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [101, 103]},
                {"slot": "b", "candidates": [113]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        }
    ]


def test_advance_residual_state_frontier_n_steps_preserves_idle_frontier_when_bounded():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = advance_residual_state_frontier_n_steps([state], 2)

    assert result["steps_run"] == 2
    assert len(result["frontier"]) == 1
    assert result["frontier"][0]["slots"][0]["domain"]["candidates"] == [101]
    assert result["promoted"] == []
    assert result["stopped"] == []
    assert len(result["idle"]) == 2
