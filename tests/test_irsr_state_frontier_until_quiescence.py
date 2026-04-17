import json
from pathlib import Path

import pytest

from pet.irsr_state import (
    refine_residual_state_slot_candidates,
    run_residual_state_frontier_until_quiescence,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_run_residual_state_frontier_until_quiescence_rejects_negative_budget():
    with pytest.raises(ValueError, match="max_steps must be >= 0"):
        run_residual_state_frontier_until_quiescence([], -1)


def test_run_residual_state_frontier_until_quiescence_stops_on_empty_frontier():
    result = run_residual_state_frontier_until_quiescence([], 5)

    assert result["steps_run"] == 0
    assert result["frontier"] == []
    assert result["frontier_summary"] == {
        "total": 0,
        "open": 0,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["promoted"] == []
    assert result["stopped"] == []
    assert result["idle"] == []
    assert result["trace"] == []
    assert result["termination_reason"] == "frontier-exhausted"


def test_run_residual_state_frontier_until_quiescence_stops_on_quiescent_idle_frontier():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = run_residual_state_frontier_until_quiescence([state], 5)

    assert result["steps_run"] == 1
    assert len(result["frontier"]) == 1
    assert result["frontier"][0]["slots"][0]["domain"]["candidates"] == [101]
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


def test_run_residual_state_frontier_until_quiescence_branches_then_reaches_quiescence():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = run_residual_state_frontier_until_quiescence([state], 5)

    assert result["steps_run"] == 3
    assert len(result["frontier"]) == 2
    assert result["frontier_summary"] == {
        "total": 2,
        "open": 2,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["promoted"] == []
    assert result["stopped"] == []
    assert len(result["idle"]) == 2
    assert result["trace"] == [
        {"step": 1, "action": "branch", "emitted": 2},
        {"step": 2, "action": "idle"},
        {"step": 3, "action": "idle"},
    ]
    assert result["termination_reason"] == "quiescent-idle-frontier"


def test_run_residual_state_frontier_until_quiescence_promotes_and_exhausts_frontier():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    result = run_residual_state_frontier_until_quiescence([state], 5)

    assert result["steps_run"] == 1
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
    assert result["trace"] == [
        {"step": 1, "action": "promote"},
    ]
    assert result["termination_reason"] == "frontier-exhausted"


def test_run_residual_state_frontier_until_quiescence_respects_budget_before_quiescence():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])

    result = run_residual_state_frontier_until_quiescence([state], 2)

    assert result["steps_run"] == 2
    assert len(result["frontier"]) == 2
    assert result["frontier_summary"] == {
        "total": 2,
        "open": 2,
        "branchable": 0,
        "payload_ready": 0,
        "contradiction": 0,
    }
    assert result["trace"] == [
        {"step": 1, "action": "branch", "emitted": 2},
        {"step": 2, "action": "idle"},
    ]
    assert result["termination_reason"] == "step-budget-exhausted"
