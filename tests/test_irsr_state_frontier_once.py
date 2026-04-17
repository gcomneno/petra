import json
from pathlib import Path

from pet.irsr_state import (
    advance_residual_state_frontier_once,
    intersect_residual_state_slot_candidates,
    refine_residual_state_slot_candidates,
)


def _load_state():
    return json.loads(
        Path("tests/fixtures/irsr/minimal_hostile_semiprime_state.json").read_text(
            encoding="utf-8"
        )
    )


def test_advance_residual_state_frontier_once_returns_empty_report_for_empty_frontier():
    result = advance_residual_state_frontier_once([])

    assert result == {
        "consumed": 0,
        "remaining": [],
        "emitted": [],
        "promoted": [],
        "stopped": [],
        "idle": [],
    }


def test_advance_residual_state_frontier_once_branches_first_state_and_preserves_remaining():
    first = _load_state()
    first = refine_residual_state_slot_candidates(first, "a", [101, 103])

    second = _load_state()
    second = refine_residual_state_slot_candidates(second, "a", [211])

    result = advance_residual_state_frontier_once([first, second])

    assert result["consumed"] == 1
    assert result["remaining"] == [second]
    assert [branch["slots"][0]["domain"]["candidates"] for branch in result["emitted"]] == [
        [101],
        [103],
    ]
    assert result["promoted"] == []
    assert result["stopped"] == []
    assert result["idle"] == []


def test_advance_residual_state_frontier_once_promotes_payload_ready_first_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = refine_residual_state_slot_candidates(state, "b", [113])

    result = advance_residual_state_frontier_once([state])

    assert result == {
        "consumed": 1,
        "remaining": [],
        "emitted": [],
        "promoted": [
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
        ],
        "stopped": [],
        "idle": [],
    }


def test_advance_residual_state_frontier_once_stops_contradiction_first_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101, 103])
    state = intersect_residual_state_slot_candidates(state, "a", [109])

    result = advance_residual_state_frontier_once([state])

    assert result["consumed"] == 1
    assert result["remaining"] == []
    assert result["emitted"] == []
    assert result["promoted"] == []
    assert len(result["stopped"]) == 1
    assert result["stopped"][0]["refinement"]["status"] == "contradiction"
    assert result["idle"] == []


def test_advance_residual_state_frontier_once_idles_open_non_branchable_first_state():
    state = _load_state()
    state = refine_residual_state_slot_candidates(state, "a", [101])

    result = advance_residual_state_frontier_once([state])

    assert result["consumed"] == 1
    assert result["remaining"] == []
    assert result["emitted"] == []
    assert result["promoted"] == []
    assert result["stopped"] == []
    assert len(result["idle"]) == 1
    assert result["idle"][0]["slots"][0]["domain"]["candidates"] == [101]
