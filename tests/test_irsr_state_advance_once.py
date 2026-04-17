import json
from pathlib import Path

from pet.irsr_state import (
    advance_residual_state_once,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_advance_residual_state_once_stops_on_contradiction():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    result = advance_residual_state_once(state)

    assert result == {
        "action": "stop",
        "reason": "contradiction",
    }


def test_advance_residual_state_once_promotes_payload_ready_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    result = advance_residual_state_once(state)

    assert result == {
        "action": "promote",
        "builder_payload": {
            "support_size": 2,
            "exponent_profile": [1, 1],
            "prime_slots": [
                {"slot": "a", "candidates": [101, 103]},
                {"slot": "b", "candidates": [113]},
            ],
            "joint_pet_constraints": [],
            "forbidden_patterns": [],
        },
    }


def test_advance_residual_state_once_branches_branchable_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = advance_residual_state_once(state)

    assert result["action"] == "branch"
    assert result["slot"] == "a"
    assert [branch["slots"][0]["domain"]["candidates"] for branch in result["branches"]] == [
        [101],
        [103],
    ]


def test_advance_residual_state_once_returns_idle_for_open_non_branchable_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = advance_residual_state_once(state)

    assert result == {
        "action": "idle",
        "reason": "open-without-branching-policy",
    }
